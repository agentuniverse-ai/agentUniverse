# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_query_keyword_extractor.py
"""Unit tests for QueryKeywordExtractor (offline, manager stubbed)."""

import pytest

import agentuniverse.agent.action.knowledge.query_paraphraser.query_keyword_extractor as qke_module
from agentuniverse.agent.action.knowledge.query_paraphraser.query_keyword_extractor import \
    QueryKeywordExtractor
from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser import \
    QueryParaphraser
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

_KEYWORDS = ("alpha", "beta")


class _StubExtractor:
    """Fake doc processor that records texts and returns fixed keywords."""

    def __init__(self):
        self.seen_texts = []

    def process_docs(self, docs):
        self.seen_texts.append(docs[0].text)
        return [Document(text=docs[0].text, keywords=set(_KEYWORDS))]


class _StubManager:
    """In-memory stand-in for the DocProcessorManager singleton."""

    def __init__(self):
        self.requested_name = None
        self.extractor = None

    def get_instance_obj(self, name):
        self.requested_name = name
        self.extractor = _StubExtractor()
        return self.extractor


class TestQueryKeywordExtractor:
    """Test defaults, configer init and keyword merging of the extractor."""

    @pytest.fixture
    def extractor(self):
        """Create a QueryKeywordExtractor instance."""
        return QueryKeywordExtractor()

    @pytest.fixture
    def manager_stub(self, monkeypatch):
        """Route DocProcessorManager() calls in the module to a stub."""
        stub = _StubManager()
        monkeypatch.setattr(qke_module, "DocProcessorManager", lambda: stub)
        return stub

    def test_component_defaults(self, extractor):
        """Defaults: jieba extractor and QUERY_PARAPHRASER component type."""
        assert isinstance(extractor, QueryParaphraser)
        assert extractor.component_type == ComponentEnum.QUERY_PARAPHRASER
        assert extractor.keyword_extractor == "jieba_keyword_extractor"
        assert extractor.name is None

    def test_initialize_sets_keyword_extractor(self, extractor):
        """Configer overrides name/description/keyword_extractor."""
        configer = ComponentConfiger()
        configer.name = "kw_extractor"
        configer.description = "Extracts keywords"
        configer.keyword_extractor = "custom_keyword_extractor"

        extractor.initialize_by_component_configer(configer)

        assert extractor.name == "kw_extractor"
        assert extractor.description == "Extracts keywords"
        assert extractor.keyword_extractor == "custom_keyword_extractor"

    def test_initialize_keeps_default_extractor_when_absent(self, extractor):
        """Configer without keyword_extractor keeps the jieba default."""
        configer = ComponentConfiger()
        configer.name = "kw_extractor"
        configer.description = "Extracts keywords"

        extractor.initialize_by_component_configer(configer)

        assert extractor.name == "kw_extractor"
        assert extractor.keyword_extractor == "jieba_keyword_extractor"

    def test_query_paraphrase_merges_keywords(self, extractor, manager_stub):
        """Keywords from the extractor are merged onto the origin query."""
        origin = Query(query_str="machine learning embeddings")

        result = extractor.query_paraphrase(origin)

        assert result is origin
        assert manager_stub.requested_name == "jieba_keyword_extractor"
        assert manager_stub.extractor.seen_texts == ["machine learning embeddings"]
        assert origin.keywords == set(_KEYWORDS)

    def test_query_paraphrase_keeps_existing_keywords(self, extractor,
                                                      manager_stub):
        """Pre-existing query keywords survive the merge."""
        origin = Query(query_str="embedding search", keywords={"seed"})

        extractor.query_paraphrase(origin)

        assert origin.keywords == {"seed"}.union(_KEYWORDS)

    def test_query_paraphrase_uses_configured_extractor(self, manager_stub):
        """The configured keyword_extractor name is requested at runtime."""
        custom = QueryKeywordExtractor(keyword_extractor="my_extractor")
        origin = Query(query_str="deep learning")

        custom.query_paraphrase(origin)

        assert manager_stub.requested_name == "my_extractor"
        assert origin.keywords == set(_KEYWORDS)
