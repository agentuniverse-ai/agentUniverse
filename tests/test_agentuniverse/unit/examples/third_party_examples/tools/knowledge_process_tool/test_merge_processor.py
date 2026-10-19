# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/13
# @Author  : au-bot
# @FileName: test_merge_processor.py
"""Unit tests for MergeByMetadata."""

import pytest

from agentuniverse.agent.action.knowledge.store.document import Document
from examples.third_party_examples.tools.knowledge_process_tool.merge_processor import \
    MergeByMetadata


class TestMergeByMetadata:
    """Test the MergeByMetadata doc processor."""

    def _docs(self):
        return [
            Document(text="first", metadata={"group": "a", "relevance_score": 0.9}),
            Document(text="second", metadata={"group": "a", "relevance_score": 0.3}),
            Document(text="lone", metadata={"group": "b", "relevance_score": 0.5}),
        ]

    def test_merges_docs_sharing_group_key(self):
        """Docs sharing a group key are merged into a single text."""
        processor = MergeByMetadata(group_keys=["group"], separator=" | ")
        result = processor.process_docs(self._docs())
        assert len(result) == 2
        merged = [doc for doc in result if doc.text == "first | second"]
        assert merged
        assert merged[0].metadata["group"] == "a"

    def test_keeps_single_doc_groups_unchanged(self):
        """Groups with one doc pass through untouched."""
        processor = MergeByMetadata(group_keys=["group"])
        result = processor.process_docs([self._docs()[2]])
        assert result[0].text == "lone"

    def test_prefer_higher_score_metadata(self):
        """Representative metadata comes from the best-scored doc."""
        processor = MergeByMetadata(group_keys=["group"], prefer_higher_score=True)
        result = processor.process_docs(self._docs())
        merged = [doc for doc in result if doc.metadata["group"] == "a"][0]
        assert merged.metadata["relevance_score"] == 0.9

    def test_make_group_key_only_uses_group_keys(self):
        """Group key ignores metadata fields not listed in group_keys."""
        processor = MergeByMetadata(group_keys=["group"])
        key = processor._make_group_key({"group": "a", "other": 1})
        assert key == ("a",)

    def test_make_group_key_handles_missing_metadata(self):
        """A doc without metadata produces a group key of Nones."""
        processor = MergeByMetadata(group_keys=["group", "kind"])
        assert processor._make_group_key(None) == (None, None)

    def test_empty_input_returns_unchanged(self):
        """An empty doc list is returned as-is."""
        processor = MergeByMetadata(group_keys=["group"])
        assert processor.process_docs([]) == []
