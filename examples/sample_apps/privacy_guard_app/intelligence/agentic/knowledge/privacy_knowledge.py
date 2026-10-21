# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import List, Any
import json

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.document import Document


class PrivacyKnowledge(Knowledge):
    """Knowledge that surfaces redaction summaries alongside retrieved text."""

    def to_llm(self, retrieved_docs: List[Document]) -> Any:
        retrieved_texts = []
        for doc in retrieved_docs:
            redaction_summary = (doc.metadata or {}).get('redaction_summary', {})
            retrieved_texts.append(json.dumps({
                "ticket": (doc.metadata or {}).get("source", "unknown"),
                "text": doc.text,
                "redacted": redaction_summary,
            }, ensure_ascii=False))
        return '\n=========================================\n'.join(retrieved_texts)
