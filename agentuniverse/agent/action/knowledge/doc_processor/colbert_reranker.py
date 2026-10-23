"""Opt-in, CPU-only late-interaction reranking with one reproducible model profile."""

from copy import deepcopy
from threading import RLock
from typing import Any, ClassVar

from pydantic import Field, PrivateAttr, StrictInt

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


class ColbertReranker(DocProcessor):
    """Score token matrices with sum-of-max dot products, not pooled vectors.

    The first profile is intentionally fixed to an English, safetensors checkpoint.
    Models must be cached separately; processing never downloads weights. Long
    inputs are rejected before encoding, not silently truncated by the encoder.
    """

    MODEL: ClassVar[str] = "answerdotai/answerai-colbert-small-v1"
    REVISION: ClassVar[str] = "934fa8bb4ce2284f4c2baa232d81aca4d076fa5e"
    QUERY_TOKENS: ClassVar[int] = 32
    DOCUMENT_TOKENS: ClassVar[int] = 300
    top_n: StrictInt = Field(default=5, gt=0, le=64)
    max_documents: StrictInt = Field(default=32, gt=0, le=64)
    max_query_chars: StrictInt = Field(default=1000, gt=0, le=10000)
    max_document_chars: StrictInt = Field(default=4000, gt=0, le=20000)
    max_total_chars: StrictInt = Field(default=64000, gt=0, le=500000)
    max_score_cells: StrictInt = Field(default=9600, gt=0, le=100000)
    batch_size: StrictInt = Field(default=4, gt=0, le=16)
    cache_folder: str | None = None
    _encoder: Any = PrivateAttr(default=None)
    _lock: Any = PrivateAttr(default_factory=RLock)

    def create_copy(self):
        """Share the read-only encoder and its lock, without duplicating model weights."""
        return self.model_copy(deep=False)

    def _get_encoder(self):
        if self._encoder is None:
            try:
                from sentence_transformers import MultiVectorEncoder
            except ImportError as error:
                raise ImportError(
                    "Install the colbert_ext optional dependencies before using ColbertReranker"
                ) from error
            encoder = MultiVectorEncoder(
                self.MODEL,
                revision=self.REVISION,
                device="cpu",
                cache_folder=self.cache_folder,
                local_files_only=True,
                trust_remote_code=False,
                token=False,
            )
            # Guard the profile assumptions used by the pre-encoding budgets.
            config = encoder[0].get_config_dict()
            expansion = config.get("query_expansion") or {}
            if (
                config.get("document_length") != self.DOCUMENT_TOKENS
                or expansion.get("length") != self.QUERY_TOKENS
                or expansion.get("strategy") != "fixed"
            ):
                raise ValueError("Unsupported ColBERT profile: token-budget assumptions differ")
            self._encoder = encoder
        return self._encoder

    def _validate_inputs(self, documents, query):
        if not isinstance(documents, list) or len(documents) > self.max_documents:
            raise ValueError("Candidate list exceeds max_documents; retrieve a bounded set first")
        if not isinstance(query, Query) or not query.query_str or not query.query_str.strip():
            raise ValueError("ColbertReranker requires a nonempty text query")
        if len(query.query_str) > self.max_query_chars:
            raise ValueError("Query exceeds max_query_chars")
        total = len(query.query_str)
        if total > self.max_total_chars:
            raise ValueError("Inputs exceed max_total_chars")
        for document in documents:
            if not isinstance(document, Document) or not document.text or not document.text.strip():
                raise ValueError("Candidates must be Documents with nonempty text")
            if len(document.text) > self.max_document_chars:
                raise ValueError("Candidate exceeds max_document_chars")
            total += len(document.text)
            if total > self.max_total_chars:
                raise ValueError("Inputs exceed max_total_chars")

    def _token_counts(self, encoder, texts, task, limit):
        prefix = encoder.prompts.get(task) or ""
        counts = []
        for text in texts:
            tokens = encoder[0].tokenizer(prefix + text, add_special_tokens=True, truncation=False)["input_ids"]
            if len(tokens) > limit:
                raise ValueError(f"{task} exceeds profile token limit {limit}; split it before reranking")
            counts.append(len(tokens))
        return counts

    @staticmethod
    def _maxsim(query_vectors, document_vectors, max_cells):
        import torch

        if (
            query_vectors.ndim != 2
            or document_vectors.ndim != 2
            or not query_vectors.shape[0]
            or not document_vectors.shape[0]
            or query_vectors.shape[1] != document_vectors.shape[1]
        ):
            raise ValueError("Expected nonempty compatible token matrices")
        if query_vectors.shape[0] * document_vectors.shape[0] > max_cells:
            raise ValueError("Token interaction exceeds max_score_cells")
        if not torch.isfinite(query_vectors).all() or not torch.isfinite(document_vectors).all():
            raise ValueError("Encoder returned nonfinite token vectors")
        score = (query_vectors @ document_vectors.T).max(dim=1).values.sum()
        if not torch.isfinite(score):
            raise ValueError("Nonfinite MaxSim score")
        return float(score.item())

    def rerank(self, documents: list[Document], query: Query) -> tuple[list[Document], dict]:
        """Return isolated documents and an explicit bounded-execution receipt."""
        self._validate_inputs(documents, query)
        report = {
            "model": self.MODEL,
            "revision": self.REVISION,
            "device": "cpu",
            "scoring": "sum_max_token_dot",
            "truncated": False,
            "candidate_count": len(documents),
            "returned_count": min(self.top_n, len(documents)),
        }
        if not documents:
            return [], report
        with self._lock:
            encoder = self._get_encoder()
            texts = [document.text for document in documents]
            query_counts = self._token_counts(encoder, [query.query_str], "query", self.QUERY_TOKENS)
            doc_counts = self._token_counts(encoder, texts, "document", self.DOCUMENT_TOKENS)
            # Query expansion includes masked augmentation positions in MaxSim.
            if self.QUERY_TOKENS * max(doc_counts) > self.max_score_cells:
                raise ValueError("Planned token interaction exceeds max_score_cells")
            import torch

            with torch.inference_mode():
                query_vectors = encoder.encode_query(
                    [query.query_str], show_progress_bar=False, normalize_embeddings=True
                )[0]
                scores = []
                encoded_tokens = []
                for start in range(0, len(texts), self.batch_size):
                    vectors = encoder.encode_document(
                        texts[start : start + self.batch_size],
                        batch_size=self.batch_size,
                        show_progress_bar=False,
                        normalize_embeddings=True,
                    )
                    if len(vectors) != len(texts[start : start + self.batch_size]):
                        raise ValueError("Encoder returned an unexpected document count")
                    for vector in vectors:
                        scores.append(self._maxsim(query_vectors, vector, self.max_score_cells))
                        encoded_tokens.append(int(vector.shape[0]))
        result = []
        for rank, index in enumerate(sorted(range(len(scores)), key=lambda i: (-scores[i], i))[: self.top_n], 1):
            document = documents[index].model_copy(deep=True)
            document.metadata = deepcopy(document.metadata or {})
            document.metadata["colbert_rerank"] = {
                "score": scores[index],
                "rank": rank,
                "source_rank": index + 1,
                "revision": self.REVISION,
            }
            result.append(document)
        report.update(
            {
                "query_input_tokens": query_counts[0],
                "query_vectors": int(query_vectors.shape[0]),
                "document_input_tokens": doc_counts,
                "document_vectors": encoded_tokens,
                "scores_in_input_order": scores,
            }
        )
        return result, report

    def _process_docs(self, origin_docs: list[Document], query: Query = None) -> list[Document]:
        return self.rerank(origin_docs, query)[0]

    def _initialize_by_component_configer(self, config):
        super()._initialize_by_component_configer(config)
        fields = (
            "top_n",
            "max_documents",
            "max_query_chars",
            "max_document_chars",
            "max_total_chars",
            "max_score_cells",
            "batch_size",
            "cache_folder",
        )
        validated = type(self)(**{key: getattr(config, key, getattr(self, key)) for key in fields})
        with self._lock:
            for key in fields:
                setattr(self, key, getattr(validated, key))
            self._encoder = None
        return self
