# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/14 15:54
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: law_knowledge.py
from typing import List, Any
import json

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.document import Document


class LawKnowledge(Knowledge):
    """A Knowledge subclass that serializes retrieved legal documents for the LLM."""

    def to_llm(self, retrieved_docs: List[Document]) -> Any:
        """Convert the retrieved documents into a single LLM-readable text block.

        Args:
            retrieved_docs: The documents retrieved from the knowledge store.

        Returns:
            str: One JSON snippet per document (its text and source file name),
            joined by '=' separator lines.
        """
        retrieved_texts = [json.dumps({
            "text": doc.text,
            "from": doc.metadata["file_name"]
        }, ensure_ascii=False) for doc in retrieved_docs]
        return '\n=========================================\n'.join(
            retrieved_texts)
