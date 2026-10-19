# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_summarize_processor.py

"""Unit tests for the SummarizeDocs doc processor (no LLM calls)."""

from types import SimpleNamespace

from agentuniverse.agent.action.knowledge.store.document import Document
from examples.third_party_examples.tools.knowledge_process_tool.summarize_processor import \
    SummarizeDocs


class TestSummarizeDocs:
    """Test SummarizeDocs defaults and offline behaviors."""

    def test_defaults(self):
        processor = SummarizeDocs()
        assert processor.name == "summarize_docs"
        assert processor.llm == "__default_instance__"
        assert processor.mode == "stuff"
        assert processor.return_only_summary is True
        assert processor.summary_metadata_key == "is_summary"

    def test_empty_docs_returns_unchanged(self):
        processor = SummarizeDocs()
        assert processor._process_docs([]) == []

    def test_initialize_by_component_configer(self):
        processor = SummarizeDocs()
        configer = SimpleNamespace(name="summarize", description=None,
                                   llm="my_llm", mode="map_reduce",
                                   summary_prompt_version="v1",
                                   combine_prompt_version="v2",
                                   return_only_summary=False,
                                   summary_metadata_key="flag")
        returned = processor._initialize_by_component_configer(configer)
        assert returned is processor
        assert processor.llm == "my_llm"
        assert processor.mode == "map_reduce"
        assert processor.summary_prompt_version == "v1"
        assert processor.combine_prompt_version == "v2"
        assert processor.return_only_summary is False
        assert processor.summary_metadata_key == "flag"
