# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_doc_processor.py
"""Unit tests for the DocProcessor abstract base class."""

from typing import List, Optional

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer


class _UpperDocProcessor(DocProcessor):
    """Concrete DocProcessor used to exercise the base-class API."""

    last_query: Optional[Query] = None

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        self.last_query = query
        return [Document(text=(d.text or "").upper()) for d in origin_docs]


class TestDocProcessor:
    """Test the abstract DocProcessor contract without app configuration."""

    @pytest.fixture
    def processor(self):
        """A freshly built concrete processor."""
        return _UpperDocProcessor(name="upper_processor")

    def test_default_attributes(self):
        processor = _UpperDocProcessor()
        assert processor.name is None
        assert processor.description is None
        assert processor.component_type is ComponentEnum.DOC_PROCESSOR
        assert processor.component_type.value == "DOC_PROCESSOR"

    def test_process_docs_delegates_to_implementation(self, processor):
        out = processor.process_docs([Document(text="hello")])
        assert out[0].text == "HELLO"

    def test_query_is_forwarded_to_implementation(self, processor):
        query = Query(query_str="the query")
        processor.process_docs([Document(text="a")], query)
        assert processor.last_query is query

    def test_empty_input_returns_empty_list(self, processor):
        assert processor.process_docs([]) == []

    def test_initialize_by_component_configer_sets_basic_info(self, processor):
        cfg = Configer()
        cfg.value = {"name": "upper_processor",
                     "description": "upper cases the text"}
        configer = ComponentConfiger().load_by_configer(cfg)
        processor._initialize_by_component_configer(configer)
        assert processor.name == "upper_processor"
        assert processor.description == "upper cases the text"

    def test_name_is_not_shared_between_instances(self):
        named = _UpperDocProcessor(name="a")
        unnamed = _UpperDocProcessor()
        assert named.name == "a"
        assert unnamed.name is None

    def test_create_copy_preserves_attributes(self, processor):
        processor.description = "upper cases the text"
        clone = processor.create_copy()
        assert clone is not processor
        assert clone.name == "upper_processor"
        assert clone.description == "upper cases the text"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
