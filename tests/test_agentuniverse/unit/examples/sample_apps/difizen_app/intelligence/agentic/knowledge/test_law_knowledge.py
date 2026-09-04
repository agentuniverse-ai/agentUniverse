# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the LawKnowledge to_llm formatter."""

from agentuniverse.agent.action.knowledge.store.document import Document
from examples.sample_apps.difizen_app.intelligence.agentic.knowledge.law_knowledge import LawKnowledge


class TestLawKnowledge:
    """Test the retrieved-document to llm formatter."""

    def test_to_llm_joins_documents(self):
        docs = [
            Document(text="第一条内容", metadata={"file_name": "a.txt"}),
            Document(text="第二条内容", metadata={"file_name": "b.txt"}),
        ]
        result = LawKnowledge().to_llm(docs)
        assert "第一条内容" in result
        assert "第二条内容" in result
        assert "a.txt" in result
        assert "b.txt" in result

    def test_to_llm_uses_separator(self):
        docs = [
            Document(text="x", metadata={"file_name": "a.txt"}),
            Document(text="y", metadata={"file_name": "b.txt"}),
        ]
        result = LawKnowledge().to_llm(docs)
        assert "==========" in result

    def test_to_llm_single_document(self):
        docs = [Document(text="only", metadata={"file_name": "c.txt"})]
        result = LawKnowledge().to_llm(docs)
        assert "only" in result
        assert result.count("==========") == 0
