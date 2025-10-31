# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/13
# @Author  : au-bot
# @FileName: score_filter_processor.py

from typing import List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class ScoreThresholdFilter(DocProcessor):
    """Filter documents by a relevance score threshold.

    This post-retrieval processor expects each `Document.metadata` to optionally
    contain a numeric field `relevance_score` (e.g., from a reranker). Documents
    with a score lower than `min_score` will be dropped. If a document has no
    score, it is kept only when `keep_no_score` is True.
    """

    name: Optional[str] = "score_threshold_filter"
    description: Optional[str] = "Filter docs by relevance score"

    min_score: float = 0.0
    keep_no_score: bool = True
    top_k: Optional[int] = None

    def _process_docs(self, origin_docs: List[Document], query: Query | None = None) -> List[Document]:
        if not origin_docs:
            return origin_docs
        filtered: List[Document] = []
        for doc in origin_docs:
            metadata = doc.metadata or {}
            score = metadata.get("relevance_score")
            if score is None:
                if self.keep_no_score:
                    filtered.append(doc)
            else:
                if score >= self.min_score:
                    filtered.append(doc)
        if self.top_k is not None and self.top_k > 0:
            filtered = filtered[: self.top_k]
        return filtered

    def _initialize_by_component_configer(self, doc_processor_configer: ComponentConfiger) -> "DocProcessor":
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "min_score"):
            self.min_score = float(doc_processor_configer.min_score)
        if hasattr(doc_processor_configer, "keep_no_score"):
            self.keep_no_score = bool(doc_processor_configer.keep_no_score)
        if hasattr(doc_processor_configer, "top_k"):
            self.top_k = int(doc_processor_configer.top_k)
        return self


