# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : Yue Wang
# @FileName: lost_in_the_middle_reorderer.py

"""
Lost-in-the-middle position-aware re-orderer post-processor.

Research on long-context LLMs ("Lost in the Middle: How Language Models Use
Long Contexts", Liu et al., 2023) shows that models attend best to content at
the beginning and the end of their input window, while quality degrades for
content buried in the middle — regardless of its actual relevance.

This processor takes the recalled document list — typically already ranked by
a reranker or fusion processor via the ``relevance_score`` metadata convention
— and re-assigns presentation positions so that:

* the most relevant documents occupy the beginning of the list,
* the next most relevant documents occupy the end of the list,
* the least relevant documents end up in the middle, where positional bias
  hurts the least.

It never drops or mutates documents; it is a pure re-ordering stage intended
to run last in a ``post_processors`` chain, right before the recalled texts
are assembled into the LLM prompt.

This is one of the knowledge recall post-processing directions of issue #248.
"""

import math
from typing import List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class LostInTheMiddleReorderer(DocProcessor):
    """Re-order recalled documents to dodge LLM positional bias.

    Documents are ranked by the numeric relevance score found under
    ``score_field`` in their metadata (the same convention written by
    ``DashscopeReranker`` / ``JinaReranker`` / ``ReciprocalRankFusionProcessor``
    and read by ``ThresholdFilter``). The ranked sequence is then dealt onto
    the strongest prompt positions: rank 1 -> first slot, rank 2 -> last slot,
    rank 3 -> second slot, rank 4 -> second-to-last slot, and so on, leaving
    the weakest documents in the middle of the final list.

    Documents without a usable score are kept (never dropped) and follow the
    scored ones in their original input order, which naturally parks them in
    the middle region. When *no* document carries a score the list is returned
    unchanged, since there is no relevance signal to re-order by.

    Attributes:
        score_field: Metadata key holding each document's relevance score.
    """

    score_field: str = "relevance_score"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Re-order documents into a lost-in-the-middle friendly layout.

        Args:
            origin_docs: Documents to be re-ordered.
            query: Query object (accepted for interface compatibility; the
                re-ordering is driven purely by document metadata scores).

        Returns:
            List[Document]: The same documents, re-ordered so the most
            relevant sit at the two ends of the list and the least relevant in
            the middle.
        """
        if len(origin_docs) < 3:
            # 0, 1 or 2 documents: every position is already a "strong"
            # position, nothing to optimise.
            return list(origin_docs)

        scored = []
        unscored = []
        for idx, doc in enumerate(origin_docs):
            score = self._extract_score(doc)
            if score is None:
                unscored.append((idx, doc))
            else:
                scored.append((idx, doc, score))

        if not scored:
            # No relevance signal at all: keep the caller's order.
            return list(origin_docs)

        # Rank scored documents by score descending; the index tie-break keeps
        # the original relative order of documents with equal scores.
        scored.sort(key=lambda item: (-item[2], item[0]))
        ranked_docs = [doc for _, doc, _ in scored] + \
                      [doc for _, doc in unscored]

        return self._deal_onto_positions(ranked_docs)

    def _extract_score(self, doc: Document) -> Optional[float]:
        """Read the relevance score of a document from its metadata.

        Non-numeric values (including booleans and NaN) are treated as
        missing so a malformed score can never corrupt the ranking.

        Args:
            doc: Document to read the score from.

        Returns:
            Optional[float]: The numeric score, or None when absent or
            unusable.
        """
        if not doc.metadata:
            return None
        raw = doc.metadata.get(self.score_field)
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            return None
        score = float(raw)
        if math.isnan(score) or math.isinf(score):
            return None
        return score

    @staticmethod
    def _deal_onto_positions(ranked_docs: List[Document]) -> List[Document]:
        """Deal a ranked list onto strong first/last positions.

        The best document takes the first slot, the second best the last
        slot, the third the second slot, the fourth the second-to-last slot,
        alternating until every document is placed. The weakest documents
        accumulate in the middle of the result.

        Args:
            ranked_docs: Documents ordered by descending relevance.

        Returns:
            List[Document]: Documents re-ordered into the final layout.
        """
        total = len(ranked_docs)
        result: List[Optional[Document]] = [None] * total
        front, back = 0, total - 1
        use_front = True
        for doc in ranked_docs:
            if use_front:
                result[front] = doc
                front += 1
            else:
                result[back] = doc
                back -= 1
            use_front = not use_front
        return [doc for doc in result if doc is not None]

    def _initialize_by_component_configer(self,
                                          doc_processor_configer:
                                          ComponentConfiger) \
            -> 'LostInTheMiddleReorderer':
        """Initialize re-orderer parameters from component configuration.

        Args:
            doc_processor_configer: Configuration object containing the
                processor parameters.

        Returns:
            LostInTheMiddleReorderer: The initialized processor instance.

        Raises:
            ValueError: If ``score_field`` is configured as a non-string or
                an empty string.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "score_field"):
            score_field = doc_processor_configer.score_field
            if not isinstance(score_field, str) or not score_field:
                raise ValueError(
                    "score_field must be a non-empty string, got: "
                    f"{score_field!r}")
            self.score_field = score_field
        return self
