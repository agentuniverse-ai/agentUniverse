# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Deterministic text statistics for knowledge documents."""

import re
from typing import Dict, List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


class TextStatisticsProcessor(DocProcessor):
    """Annotate documents with text-size and line statistics."""

    metadata_key: str = "text_statistics"
    overwrite: bool = True

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        if not isinstance(self.metadata_key, str) or not self.metadata_key.strip():
            raise ValueError("metadata_key must be a non-empty string")

        for document in origin_docs:
            text = document.text or ""
            statistics: Dict[str, int] = {
                "character_count": len(text),
                "non_whitespace_count": len(re.sub(r"\s", "", text)),
                "line_count": len(text.splitlines()),
                "word_count": len(re.findall(r"\b[\w'-]+\b", text, re.UNICODE)),
            }
            metadata = dict(document.metadata or {})
            if not self.overwrite and self.metadata_key in metadata:
                continue
            metadata[self.metadata_key] = statistics
            document.metadata = metadata
        return origin_docs
