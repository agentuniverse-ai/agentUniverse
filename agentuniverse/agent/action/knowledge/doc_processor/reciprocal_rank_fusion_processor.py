# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/10
# @Author  : contributor
# @FileName: reciprocal_rank_fusion_processor.py

"""
Reciprocal Rank Fusion (RRF) document processor.

Recall post-processor that merges the results of several retrieval channels
into a single relevance ranking, addressing the *融合 (fusion)* direction of
issue #248 ("融合、过滤、摘要、总结...进一步提升多路召回后内容的质量").

Reciprocal Rank Fusion is a parameter-light way to combine multiple ranked
result lists without needing the (often incomparable) raw scores of each
channel. For a document ``d`` the fused score is::

    score(d) = Σ_channels  1 / (k + rank_channel(d))

where ``rank_channel(d)`` is the 1-based position of ``d`` within the channel
that returned it (``k`` is a smoothing constant, conventionally 60). A document
that appears near the top of several channels therefore accumulates a higher
fused score than one that only appears in a single channel, even if it ranks
first there.

The processor consumes a flat list of retrieved :class:`Document` objects.
Channels are told apart by a metadata field (``channel_key``) that each
retrieval channel is expected to stamp onto its documents.
:meth:`Knowledge.query_knowledge` does this automatically: it stamps every
recalled document with the store code under the ``recall_channel`` key and
keeps per-store ranked results, so fusing multi-store recall works without
extra wiring. When no document carries the channel field the whole input is
treated as a single channel, in which case RRF degrades to deterministic
position-based scoring that preserves the input order — making the component
safe to drop into an existing single-store pipeline.
"""

from typing import Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class ReciprocalRankFusionProcessor(DocProcessor):
    """Fuses the ranked results of multiple retrieval channels via RRF.

    Attributes:
        channel_key (Optional[str]): Metadata field used to tell channels
            apart. Each retrieval channel should write its identifier into
            ``document.metadata[channel_key]``. When ``None`` (or when no
            document carries the field) the whole input is treated as one
            channel.
        dedup_key (str): Identity used to deduplicate the same document
            appearing in several channels. ``"id"`` (the default) uses the
            deterministic document id; ``"text"`` compares raw content; any
            other value is read from ``document.metadata``. When the configured
            metadata field is absent from a document, its unique id is used as
            a safe fallback so such documents are not all collapsed together.
        k (int): RRF smoothing constant. Larger values dampen the advantage of
            top ranks; the conventional value is 60.
        top_n (Optional[int]): Maximum number of fused documents to return.
            ``None`` returns all.
        score_field (str): Metadata key the fused score is written into on each
            returned document.
    """

    channel_key: Optional[str] = None
    dedup_key: str = "id"
    k: int = 60
    top_n: Optional[int] = None
    score_field: str = "relevance_score"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Fuse the input documents via reciprocal rank fusion.

        Args:
            origin_docs (List[Document]): Documents retrieved across one or
                more channels, intra-channel order reflecting relevance.
            query (Query, optional): Unused; kept for interface compatibility.

        Returns:
            List[Document]: Documents re-ranked by fused relevance score
            (descending), each carrying ``metadata[score_field]``. An empty
            input yields an empty list.
        """
        if not origin_docs:
            return []

        channels = self._group_channels(origin_docs)

        # Accumulate fused score per document identity. First occurrence wins
        # so the returned object keeps the id / embedding / keywords / text of
        # the document as it first appeared.
        scores: Dict[Tuple, float] = {}
        representatives: Dict[Tuple, Document] = {}
        for channel in channels:
            seen_in_channel = set()
            for rank, doc in enumerate(channel):
                identity = self._identity(doc)
                if identity in seen_in_channel:
                    continue
                seen_in_channel.add(identity)
                scores[identity] = scores.get(identity, 0.0) + \
                    1.0 / (self.k + rank + 1)
                if identity not in representatives:
                    representatives[identity] = doc

        ranked_identities = sorted(
            scores,
            key=lambda ident: (-scores[ident], self._tiebreak(representatives[ident])),
        )
        if self.top_n is not None:
            ranked_identities = ranked_identities[:max(0, self.top_n)]

        # Build the output list, writing the fused score into each document's
        # metadata without disturbing its other fields.
        fused: List[Document] = []
        for identity in ranked_identities:
            doc = representatives[identity]
            metadata = dict(doc.metadata or {})
            metadata[self.score_field] = scores[identity]
            doc.metadata = metadata
            fused.append(doc)
        return fused

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _group_channels(self, origin_docs: List[Document]) -> List[List[Document]]:
        """Split the flat doc list into per-channel sub-lists.

        Documents are grouped by ``metadata[channel_key]`` while preserving
        input order both across and within channels. When ``channel_key`` is
        unset, or when no document carries the field, the whole input forms a
        single channel.
        """
        if not self.channel_key:
            return [list(origin_docs)]

        order: List = []
        buckets: Dict = {}
        for doc in origin_docs:
            channel_id = (doc.metadata or {}).get(self.channel_key)
            if channel_id is None:
                channel_id = "__default__"
            if channel_id not in buckets:
                buckets[channel_id] = []
                order.append(channel_id)
            buckets[channel_id].append(doc)

        # If every document landed in the default bucket (none carried the
        # field), behave exactly like single-channel mode.
        if len(order) == 1 and order[0] == "__default__":
            return [list(origin_docs)]

        return [buckets[name] for name in order]

    def _identity(self, doc: Document) -> Tuple:
        """Stable, hashable identity of a document for cross-channel dedup.

        When ``dedup_key`` names a metadata field that a document does not
        carry, fall back to the document id instead of returning ``None``;
        otherwise every such document would share the same identity and be
        collapsed into a single result.
        """
        if self.dedup_key == "id":
            return ("id", doc.id)
        if self.dedup_key == "text":
            return ("text", doc.text)
        meta_value = (doc.metadata or {}).get(self.dedup_key)
        if meta_value is None:
            return ("id", doc.id)
        return ("meta", self.dedup_key, meta_value)

    @staticmethod
    def _tiebreak(doc: Document) -> str:
        """Deterministic secondary sort key to keep RRF output stable."""
        return doc.id or doc.text or ""

    # ------------------------------------------------------------------ #
    # Config
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self,
            doc_processor_configer: ComponentConfiger) \
            -> 'ReciprocalRankFusionProcessor':
        """Initialize the processor parameters from the component configer.

        Args:
            doc_processor_configer (ComponentConfiger): Configuration object
                containing the fusion parameters.

        Returns:
            The initialized processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "channel_key"):
            self.channel_key = doc_processor_configer.channel_key
        if hasattr(doc_processor_configer, "dedup_key"):
            self.dedup_key = doc_processor_configer.dedup_key
        if hasattr(doc_processor_configer, "k"):
            self.k = doc_processor_configer.k
        if hasattr(doc_processor_configer, "top_n"):
            self.top_n = doc_processor_configer.top_n
        if hasattr(doc_processor_configer, "score_field"):
            self.score_field = doc_processor_configer.score_field
        return self
