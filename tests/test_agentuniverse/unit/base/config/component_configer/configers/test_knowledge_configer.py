# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/13 10:00
# @Author  : kaichuan
# @FileName: test_knowledge_configer.py
"""Unit tests for KnowledgeConfiger."""

import pytest

from agentuniverse.base.config.component_configer.configers.knowledge_configer import (
    KnowledgeConfiger,
)
from agentuniverse.base.config.configer import Configer


class TestKnowledgeConfiger:
    """Test KnowledgeConfiger defaults and load behavior."""

    def test_default_values_before_load(self):
        """A freshly constructed configer exposes documented defaults."""
        configer = KnowledgeConfiger()
        assert configer.name is None
        assert configer.description is None
        assert configer.ext_info is None
        assert configer.stores == []
        assert configer.query_paraphrasers == []
        assert configer.insert_processors == []
        assert configer.rag_router == "base_router"
        assert configer.post_processors == []
        assert configer.readers == {}

    def test_load_populates_metadata_properties(self):
        """load() copies name/description/ext_info from the Configer value."""
        configer = Configer()
        configer.value = {
            "name": "faq_knowledge",
            "description": "FAQ knowledge base",
            "ext_info": {"team": "search"},
        }
        loaded = KnowledgeConfiger(configer).load()
        assert loaded.name == "faq_knowledge"
        assert loaded.description == "FAQ knowledge base"
        assert loaded.ext_info == {"team": "search"}

    def test_load_without_name_leaves_it_none(self):
        """A value missing the name key keeps the name property as None."""
        configer = Configer()
        configer.value = {"description": "no name here"}
        loaded = KnowledgeConfiger(configer).load()
        assert loaded.name is None
        assert loaded.description == "no name here"

    def test_load_overwrites_stores_and_router(self):
        """Configer keys for stores/rag_router override the defaults."""
        configer = Configer()
        configer.value = {
            "name": "kb",
            "stores": ["vector_store", "keyword_store"],
            "rag_router": "advanced_router",
        }
        loaded = KnowledgeConfiger(configer).load()
        assert loaded.stores == ["vector_store", "keyword_store"]
        assert loaded.rag_router == "advanced_router"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
