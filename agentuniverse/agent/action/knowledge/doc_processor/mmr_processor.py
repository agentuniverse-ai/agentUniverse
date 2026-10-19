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
retrieval). When an ``embedding_name`` is configured, *every* embedding is
recomputed with that single model so the whole set lives in one space — this
is the only way to obtain a meaningful ranking for documents recalled from
multiple stores that may carry precomputed vectors from different models. A
query is embedded from its ``query_str``; a query that only carries a
precomputed vector is unverifiable (equal dimension does not imply same model)
and the processor degrades to input order. If embeddings cannot be obtained,
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

        # Guarantee a homogeneous embedding space before ranking. Documents
        # recalled from multiple stores can carry vectors from different models
        # or dimensions; comparing them with cosine would silently truncate to
        # the shortest vector and produce a plausible but meaningless ranking.
        # Require one shared dimension, else degrade to input order.
        dims = {len(e) for e in doc_embeddings} | {len(query_embedding)}
        if len(dims) > 1:
            logger.warning(
                f"MMR: embeddings have inconsistent dimensions {sorted(dims)}; "
                "cannot compute meaningful similarities. Returning documents in "
                "input order. Set embedding_name to recompute all embeddings "
                "with a single model.")
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
        """Return per-document and query embeddings.

        Returns ``(doc_embeddings, query_embedding)`` where ``doc_embeddings``
        aligns positionally with ``docs``. Entries that cannot be obtained stay
        ``None``; the caller treats any ``None`` as "MMR not runnable" and
        degrades to input order.

        When ``embedding_name`` is configured, *every* embedding (all documents
        and the query) is recomputed with that single model. This is the only
        way to guarantee a homogeneous embedding space for documents recalled
        from multiple stores that may carry precomputed vectors from different
        models or dimensions; reusing those precomputed vectors would mix
        incompatible spaces and yield meaningless similarities.
        """
        if self.embedding_name:
            return self._resolve_embeddings_via_model(docs, query)

        # No model configured: rely on embeddings already carried by the
        # documents and query. Any heterogeneity here is caught by the
        # dimension check in ``_process_docs`` and degrades explicitly.
        doc_embeddings: List[Optional[List[float]]] = [
            doc.embedding if doc.embedding else None for doc in docs]
        query_embedding: Optional[List[float]] = None
        if query is not None and query.embeddings:
            query_embedding = query.embeddings[0]
        return doc_embeddings, query_embedding

    def _resolve_embeddings_via_model(
            self, docs: List[Document], query: Optional[Query]
    ) -> Tuple[List[Optional[List[float]]], Optional[List[float]]]:
        """Recompute all embeddings with the configured model.

        Precomputed ``Document.embedding`` / ``Query.embeddings`` are ignored on
        purpose so the whole set lives in one embedding space. A query with a
        ``query_str`` is embedded in that same space. A query that only carries
        a precomputed vector has unverifiable provenance — even when its
        dimension matches the configured model, it may come from a different
        model and the dimension check cannot tell. The processor therefore
        degrades to input order rather than rank on a possibly-foreign vector.
        """
        doc_embeddings: List[Optional[List[float]]] = [None] * len(docs)
        query_embedding: Optional[List[float]] = None
        try:
            model = EmbeddingManager().get_instance_obj(self.embedding_name)
            if docs:
                computed = model.get_embeddings([doc.text or "" for doc in docs])
                for idx, emb in enumerate(computed):
                    doc_embeddings[idx] = emb
                    docs[idx].embedding = emb
            if query is not None and query.query_str:
                # Only a freshly computed embedding shares the configured model's
                # space; a precomputed Query.embeddings value has no verifiable
                # provenance (equal dimension does NOT imply same model).
                query_embedding = model.get_embeddings([query.query_str])[0]
            elif query is not None and not query.query_str and query.embeddings:
                logger.warning(
                    "MMR: embedding_name is configured but the query carries no "
                    "query_str, only a precomputed vector. Its provenance cannot "
                    "be verified against the configured model (equal dimensions "
                    "do not imply the same embedding space); returning documents "
                    "in input order. Pass query_str to embed the query with the "
                    "configured model.")
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
        """Cosine similarity; zero when either vector has zero magnitude.

        Raises ``ValueError`` for vectors of different dimensions rather than
        silently truncating via ``zip`` (which would rank on meaningless
        similarities). The dimension check in ``_process_docs`` keeps this from
        firing in normal operation; the guard is an explicit invariant.
        """
        if len(a) != len(b):
            raise ValueError(
                f"Cannot compute cosine similarity between vectors of different "
                f"dimensions ({len(a)} vs {len(b)}); ensure all embeddings come "
                f"from a single model, or set embedding_name to recompute them.")
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
