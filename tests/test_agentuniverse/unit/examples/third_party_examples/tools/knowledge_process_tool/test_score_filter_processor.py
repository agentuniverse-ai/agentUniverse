# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/13
# @Author  : au-bot
# @FileName: test_score_filter_processor.py
"""Unit tests for ScoreThresholdFilter."""

import pytest

from agentuniverse.agent.action.knowledge.store.document import Document
from examples.third_party_examples.tools.knowledge_process_tool.score_filter_processor import \
    ScoreThresholdFilter


class TestScoreThresholdFilter:
    """Test the ScoreThresholdFilter doc processor."""

    def test_filter_keeps_docs_above_min_score(self):
        """Docs with a score at/above min_score survive."""
        docs = [
            Document(text="good", metadata={"relevance_score": 0.9}),
            Document(text="ok", metadata={"relevance_score": 0.5}),
            Document(text="bad", metadata={"relevance_score": 0.1}),
        ]
        processor = ScoreThresholdFilter(min_score=0.5)
        result = processor.process_docs(docs)
        assert [doc.text for doc in result] == ["good", "ok"]

    def test_keep_no_score_docs_by_default(self):
        """Docs without a relevance_score are kept when keep_no_score=True."""
        docs = [
            Document(text="scored", metadata={"relevance_score": 0.8}),
            Document(text="no-meta"),
            Document(text="empty-meta", metadata={}),
        ]
        processor = ScoreThresholdFilter(min_score=0.5, keep_no_score=True)
        result = processor.process_docs(docs)
        assert [doc.text for doc in result] == ["scored", "no-meta", "empty-meta"]

    def test_drop_no_score_docs_when_disabled(self):
        """Docs without a relevance_score are dropped when keep_no_score=False."""
        docs = [
            Document(text="scored", metadata={"relevance_score": 0.8}),
            Document(text="no-meta"),
        ]
        processor = ScoreThresholdFilter(min_score=0.5, keep_no_score=False)
        result = processor.process_docs(docs)
        assert [doc.text for doc in result] == ["scored"]

    def test_top_k_trims_result(self):
        """top_k limits the number of returned docs."""
        docs = [
            Document(text=f"d{i}", metadata={"relevance_score": float(i)})
            for i in range(5)
        ]
        processor = ScoreThresholdFilter(min_score=0.0, top_k=2)
        result = processor.process_docs(docs)
        assert len(result) == 2
        assert result[0].text == "d0"

    def test_empty_input_is_returned_unchanged(self):
        """An empty doc list short-circuits and is returned as-is."""
        processor = ScoreThresholdFilter(min_score=0.5)
        result = processor.process_docs([])
        assert result == []
