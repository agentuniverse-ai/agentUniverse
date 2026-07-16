# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/16
# @FileName: mmr_processor.py

"""
Maximal Marginal Relevance (MMR) post-processor.

Re-ranks the documents recalled by a RAG pipeline so the result set is both
on-topic and non-repetitive. Classic MMR selects documents one at a time,
maximising

    score(d) = lambda * sim(d, query) - (1 - lambda) * max_{s in selected} sim(d, s)

The first term keeps selected documents relevant to the query; the second
penalises redundancy with anything already chosen. ``lambda = 1`` collapses to
pure relevance ranking; ``lambda = 0`` maximises diversity.

This is the *post-processing* direction of issue #248 (knowledge post-
processing components): it runs over the list of documents that
``Knowledge.query_knowledge`` already retrieved and de-duplicated, and returns a
re-ordered (and optionally truncated) list.

It is intentionally distinct from sibling components: ``semantic_deduplicator``
*removes* near-duplicate documents above a hard threshold, and
``ReciprocalRankFusionProcessor`` *combines* ranked lists from several stores;
MMR instead performs diversity-aware *selection / re-ranking* of a single
recalled set.

Embeddings: query and document embeddings are taken from ``Query.embeddings``
and ``Document.embedding`` when present (the store populates them during
retrieval). When an ``embedding_name`` is configured, any missing embeddings are
computed on demand via ``EmbeddingManager``. If embeddings cannot be obtained,
the processor degrades gracefully and returns the documents in their input
order rather than crashing retrieval.
"""

import logging
import math
from typing import Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.embedding.embedding_manager import \
    EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)


class MMRProcessor(DocProcessor):
    """Re-rank recalled documents with Maximal Marginal Relevance.

    Attributes:
        lambda_coef: Relevance/diversity trade-off in [0.0, 1.0]. ``1.0`` is
            pure relevance ranking, ``0.0`` maximises diversity, and ``0.5``
            (the default) balances the two.
        top_n: Number of documents to keep after re-ranking. ``None`` keeps all
            documents, only re-ordering them.
        embedding_name: Name of a registered embedding component used to embed
            documents / the query on demand when they lack an embedding. When
            ``None``, only embeddings already carried on the documents and the
            query are used.
        score_key: Optional metadata key under which each kept document's cosine
            relevance to the query is stamped. ``None`` (the default) stamps
            nothing, so the processor does not clobber scores written by earlier
            processors such as RRF.
    """

    lambda_coef: float = 0.5
    top_n: Optional[int] = None
    embedding_name: Optional[str] = None
    score_key: Optional[str] = None

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Re-rank ``origin_docs`` by maximal marginal relevance.

        Args:
            origin_docs: Documents recalled by the knowledge query.
            query: The originating query; its embedding drives relevance.

        Returns:
            Re-ranked (and optionally truncated to ``top_n``) documents. If
            embeddings are unavailable the input order is preserved.
        """
        if not origin_docs:
            return []
        if self.top_n is not None and self.top_n <= 0:
            return []

        doc_embeddings, query_embedding = self._resolve_embeddings(
            origin_docs, query)
        if query_embedding is None or any(e is None for e in doc_embeddings):
            logger.warning(
                "MMR: embeddings unavailable (set embedding_name or ensure the "
                "store populates Document.embedding / Query.embeddings); "
                "returning documents in input order.")
            return origin_docs[:self.top_n] if self.top_n else list(origin_docs)

        order = self._select(doc_embeddings, query_embedding)
        if self.score_key:
            for i in order:
                meta = dict(origin_docs[i].metadata or {})
                meta[self.score_key] = self._cosine(doc_embeddings[i],
                                                    query_embedding)
                origin_docs[i].metadata = meta
        return [origin_docs[i] for i in order]

    # ------------------------------------------------------------------ #
    # Embedding resolution
    # ------------------------------------------------------------------ #
    def _resolve_embeddings(
            self, docs: List[Document], query: Query
    ) -> Tuple[List[Optional[List[float]]], Optional[List[float]]]:
        """Return per-document and query embeddings, computing missing ones.

        Returns ``(doc_embeddings, query_embedding)`` where ``doc_embeddings``
        aligns positionally with ``docs``. Entries that cannot be obtained stay
        ``None``; the caller treats any ``None`` as "MMR not runnable" and
        degrades to input order.
        """
        doc_embeddings: List[Optional[List[float]]] = []
        missing_texts: List[str] = []
        missing_indices: List[int] = []
        for idx, doc in enumerate(docs):
            if doc.embedding:
                doc_embeddings.append(doc.embedding)
            else:
                doc_embeddings.append(None)
                missing_texts.append(doc.text or "")
                missing_indices.append(idx)

        query_embedding: Optional[List[float]] = None
        query_text: Optional[str] = None
        if query is not None:
            if query.embeddings:
                query_embedding = query.embeddings[0]
            elif query.query_str:
                query_text = query.query_str

        needs_model = bool(missing_texts) or query_text is not None
        if not needs_model:
            return doc_embeddings, query_embedding
        if not self.embedding_name:
            # No model configured to compute the missing embeddings.
            return doc_embeddings, query_embedding
        try:
            model = EmbeddingManager().get_instance_obj(self.embedding_name)
            if missing_texts:
                computed = model.get_embeddings(missing_texts)
                for idx, emb in zip(missing_indices, computed):
                    doc_embeddings[idx] = emb
                    docs[idx].embedding = emb
            if query_text is not None:
                query_embedding = model.get_embeddings([query_text])[0]
        except Exception as exc:  # noqa: BLE001 - degrade, never crash retrieval
            logger.error(f"MMR: embedding lookup failed: {exc}")
        return doc_embeddings, query_embedding

    # ------------------------------------------------------------------ #
    # MMR selection (pure)
    # ------------------------------------------------------------------ #
    def _select(self, doc_embeddings: List[List[float]],
                query_embedding: List[float]) -> List[int]:
        """Greedy MMR selection; returns chosen indices in selection order."""
        n = len(doc_embeddings)
        relevance = [self._cosine(e, query_embedding) for e in doc_embeddings]
        sim_cache: Dict[Tuple[int, int], float] = {}

        def pair_sim(i: int, j: int) -> float:
            key = (i, j) if i < j else (j, i)
            cached = sim_cache.get(key)
            if cached is None:
                cached = self._cosine(doc_embeddings[i], doc_embeddings[j])
                sim_cache[key] = cached
            return cached

        remaining = list(range(n))
        # First pick: the most query-relevant document.
        first = max(remaining, key=lambda i: relevance[i])
        selected = [first]
        remaining.remove(first)

        limit = self.top_n if self.top_n is not None else n
        while remaining and len(selected) < limit:
            best_i = remaining[0]
            best_score = None
            for i in remaining:
                redundancy = max(pair_sim(i, s) for s in selected)
                score = self.lambda_coef * relevance[i] \
                    - (1.0 - self.lambda_coef) * redundancy
                if best_score is None or score > best_score:
                    best_score = score
                    best_i = i
            selected.append(best_i)
            remaining.remove(best_i)
        return selected

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        """Cosine similarity; zero when either vector has zero magnitude."""
        dot = 0.0
        for x, y in zip(a, b):
            dot += x * y
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> 'MMRProcessor':
        """Initialize the processor from its component config."""
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "lambda_coef"):
            self.lambda_coef = doc_processor_configer.lambda_coef
        if hasattr(doc_processor_configer, "top_n"):
            self.top_n = doc_processor_configer.top_n
        if hasattr(doc_processor_configer, "embedding_name"):
            self.embedding_name = doc_processor_configer.embedding_name
        if hasattr(doc_processor_configer, "score_key"):
            self.score_key = doc_processor_configer.score_key
        if not 0.0 <= self.lambda_coef <= 1.0:
            raise ValueError(
                f"lambda_coef must be in [0.0, 1.0], got {self.lambda_coef}.")
        return self
