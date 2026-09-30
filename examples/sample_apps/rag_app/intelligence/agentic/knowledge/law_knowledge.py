# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List, Any

# @Time    : 2024/8/14 15:54
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: law_knowledge.py
import json

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.document import Document


class LawKnowledge(Knowledge):
    """Knowledge subclass that formats retrieved legal documents for LLM consumption."""

    def to_llm(self, retrieved_docs: List[Document]) -> Any:
        """Serialize the retrieved documents into a single text block for the LLM.

        Args:
            retrieved_docs (List[Document]): The documents retrieved from the store.

        Returns:
            Any: A string joining each document's JSON payload (text and source
                file name) with separator lines.
        """

        retrieved_texts = [json.dumps({
            "text": doc.text,
            "from": doc.metadata["file_name"]
        },ensure_ascii=False) for doc in retrieved_docs]
        return '\n=========================================\n'.join(
            retrieved_texts)
