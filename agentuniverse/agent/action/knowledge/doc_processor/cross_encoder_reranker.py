# !/usr/bin/env python3

# @Time    : 2026/10/02
# @FileName: cross_encoder_reranker.py

"""
Local cross-encoder reranking post-processor.

Reranks documents recalled by a RAG pipeline with a local CrossEncoder
model — by default ``BAAI/bge-reranker-base``, any sentence-transformers
CrossEncoder-compatible checkpoint works (``BAAI/bge-reranker-v2-m3``,
``jinaai/jina-reranker-v1-tiny-en``, a fine-tuned local path, ...). Unlike
the existing DashScope / Jina cloud rerankers, scoring happens fully
in-process: no API key, no network call at query time, and recalled text
never leaves the machine — the standard requirement for offline and
private-deployment scenarios.

The heavy ``sentence-transformers`` dependency (which pulls in torch) is
optional and lazily imported on first use: the shipped yaml loads at
framework start without the package installed, and a missing package
raises an ``ImportError`` carrying the exact install command
(``pip install 'agentuniverse[rerank_ext]'``).

Scoring semantics follow the existing reranker conventions:

* one ``(query, document text)`` pair per document, scored in a single
  batched ``predict`` call (``batch_size`` bounds peak memory);
* documents are sorted by score, descending; the sort is stable, so tied
  scores keep the incoming recall order (a preceding fusion processor's
  ranking is respected, not shuffled);
* ``top_n`` optionally truncates the result; ``None`` (default) keeps
  every document and only reorders;
* each kept document's score is stamped under ``score_key``
  (``relevance_score`` by default, matching DashscopeReranker); an empty
  ``score_key`` skips stamping so earlier scores are never clobbered.

A configured reranker is relevance-critical, so failures are loud: a
missing query raises (same contract as DashscopeReranker), a missing
dependency raises with install instructions, and model/predict errors
propagate instead of silently returning the unreranked list — a silent
pass-through would quietly disable exactly the ranking the operator
configured. Static configuration errors (empty model_name, non-positive
top_n/batch_size, non-string score_key/device) fail at component-load
time.
"""

import logging

from pydantic import PrivateAttr

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)


class CrossEncoderReranker(DocProcessor):
    """Rerank recalled documents with a local CrossEncoder model.

    Attributes:
        model_name: CrossEncoder model identifier or local checkpoint path.
            Any sentence-transformers CrossEncoder-compatible model works.
        top_n: Number of documents to keep after reranking; ``None``
            (default) keeps every document and only reorders.
        score_key: Metadata key under which each kept document's relevance
            score is stamped; an empty string skips stamping.
        batch_size: Batch size passed to ``CrossEncoder.predict``, bounding
            peak memory for large recall lists.
        device: Device string forwarded to the model (``"cpu"``, ``"cuda"``,
            ``"mps"``, ...); empty (default) lets sentence-transformers pick.
    """

    model_name: str = "BAAI/bge-reranker-base"
    top_n: int | None = None
    score_key: str = "relevance_score"
    batch_size: int = 32
    device: str = ""

    # Loaded on first use and cached: model loading is expensive (weights +
    # tokenizer), while component configuration is final by then. Private so
    # pydantic does not treat the heavyweight model object as a field.
    _model: object | None = PrivateAttr(default=None)

    def _process_docs(self, origin_docs: list[Document], query: Query = None) -> list[Document]:
        """Score every document against the query and sort by relevance.

        Args:
            origin_docs: Documents recalled by the knowledge query.
            query: Query whose ``query_str`` is scored against each document.

        Returns:
            The (optionally truncated) documents ordered by descending
            cross-encoder score, with scores stamped under ``score_key``
            when it is set. Tied scores keep the incoming order.

        Raises:
            ValueError: On invalid static configuration, or when no query
                string is available to score against.
            ImportError: When ``sentence-transformers`` is not installed.
        """
        self._validate_config()
        if not origin_docs:
            return origin_docs
        if not query or not (query.query_str or "").strip():
            raise ValueError("CrossEncoderReranker needs an origin string query.")
        model = self._get_model()
        pairs = [(query.query_str, doc.text or "") for doc in origin_docs]
        scores = model.predict(pairs, batch_size=self.batch_size, show_progress_bar=False)
        scored = list(zip(origin_docs, (float(score) for score in scores), strict=False))
        # Stable descending sort: tied scores keep the incoming recall order.
        scored.sort(key=lambda item: item[1], reverse=True)
        if self.top_n is not None:
            scored = scored[: self.top_n]
        reranked: list[Document] = []
        for doc, score in scored:
            if self.score_key:
                metadata = dict(doc.metadata or {})
                metadata[self.score_key] = score
                doc.metadata = metadata
            reranked.append(doc)
        return reranked

    # ------------------------------------------------------------------ #
    # Model loading
    # ------------------------------------------------------------------ #
    def _get_model(self):
        """Load (once) and cache the CrossEncoder model.

        Raises:
            ImportError: With the exact install command when the optional
                ``sentence-transformers`` dependency is missing.
        """
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
            except ImportError as exc:
                raise ImportError(
                    "CrossEncoderReranker requires the sentence-transformers package. "
                    "Install it with: pip install 'agentuniverse[rerank_ext]' "
                    "(or pip install sentence-transformers)."
                ) from exc
            kwargs = {"device": self.device} if self.device else {}
            logger.info("CrossEncoderReranker loading model %r", self.model_name)
            self._model = CrossEncoder(self.model_name, **kwargs)
        return self._model

    # ------------------------------------------------------------------ #
    # Configuration validation
    # ------------------------------------------------------------------ #
    def _validate_config(self) -> None:
        """Fail loudly on configuration that contradicts the operator's intent.

        Raises:
            TypeError: When a field carries the wrong type (non-string
                ``model_name`` / ``score_key`` / ``device``, non-integer
                ``top_n`` / ``batch_size``).
            ValueError: On an empty ``model_name`` or a non-positive
                ``top_n`` (other than ``None``) / ``batch_size``.
        """
        if not isinstance(self.model_name, str):
            raise TypeError(f"model_name must be a string, got {self.model_name!r}.")
        if not self.model_name.strip():
            raise ValueError("model_name must be a non-empty string.")
        if self.top_n is not None:
            if not isinstance(self.top_n, int):
                raise TypeError(f"top_n must be an integer or None, got {self.top_n!r}.")
            if self.top_n < 1:
                raise ValueError(f"top_n must be a positive integer or None, got {self.top_n!r}.")
        if not isinstance(self.batch_size, int):
            raise TypeError(f"batch_size must be an integer, got {self.batch_size!r}.")
        if self.batch_size < 1:
            raise ValueError(f"batch_size must be a positive integer, got {self.batch_size!r}.")
        if not isinstance(self.score_key, str):
            raise TypeError(f"score_key must be a string ('' to skip stamping), got {self.score_key!r}.")
        if not isinstance(self.device, str):
            raise TypeError(f"device must be a string ('' for auto), got {self.device!r}.")

    def _initialize_by_component_configer(self, doc_processor_configer: ComponentConfiger) -> "CrossEncoderReranker":
        """Initialize the reranker from its component config."""
        super()._initialize_by_component_configer(doc_processor_configer)
        for attr in ("model_name", "top_n", "score_key", "batch_size", "device"):
            if hasattr(doc_processor_configer, attr):
                setattr(self, attr, getattr(doc_processor_configer, attr))
        # Validate eagerly so a misconfiguration fails at component-load time
        # rather than on the first query. The model itself stays lazy: the
        # shipped yaml must load without sentence-transformers installed.
        self._validate_config()
        return self
