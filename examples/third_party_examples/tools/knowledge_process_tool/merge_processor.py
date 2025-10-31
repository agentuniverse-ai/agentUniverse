# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/13
# @Author  : au-bot
# @FileName: merge_processor.py

from typing import List, Optional, Dict, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class MergeByMetadata(DocProcessor):
    """Merge documents that share the same metadata keys.

    Documents are grouped by the tuple of values for `group_keys` inside
    `Document.metadata`. Within each group, texts are concatenated with
    `separator`. Optionally, keep only the best scored document's metadata
    when `prefer_higher_score` is True.
    """

    name: Optional[str] = "merge_by_metadata"
    description: Optional[str] = "Merge docs by metadata keys"

    group_keys: List[str] = []
    separator: str = "\n\n"
    prefer_higher_score: bool = True

    def _make_group_key(self, metadata: Optional[Dict]) -> Tuple:
        metadata = metadata or {}
        return tuple(metadata.get(k) for k in self.group_keys)

    def _process_docs(self, origin_docs: List[Document], query: Query | None = None) -> List[Document]:
        if not origin_docs or not self.group_keys:
            return origin_docs
        grouped: Dict[Tuple, List[Document]] = {}
        for doc in origin_docs:
            key = self._make_group_key(doc.metadata)
            grouped.setdefault(key, []).append(doc)

        merged_docs: List[Document] = []
        for _, docs in grouped.items():
            if len(docs) == 1:
                merged_docs.append(docs[0])
                continue
            combined_text = self.separator.join(d.text or "" for d in docs if d.text)
            # choose metadata representative
            rep = docs[0]
            if self.prefer_higher_score:
                rep = max(docs, key=lambda d: (d.metadata or {}).get("relevance_score", -1))
            merged_docs.append(Document(text=combined_text, metadata=rep.metadata))
        return merged_docs

    def _initialize_by_component_configer(self, doc_processor_configer: ComponentConfiger) -> "DocProcessor":
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "group_keys"):
            self.group_keys = list(doc_processor_configer.group_keys)
        if hasattr(doc_processor_configer, "separator"):
            self.separator = str(doc_processor_configer.separator)
        if hasattr(doc_processor_configer, "prefer_higher_score"):
            self.prefer_higher_score = bool(doc_processor_configer.prefer_higher_score)
        return self


