# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_knowledge_configer.py

"""Unit tests for the KnowledgeConfiger."""

from types import SimpleNamespace

from agentuniverse.base.config.component_configer.configers.knowledge_configer import \
    KnowledgeConfiger


class TestKnowledgeConfiger:
    """Test knowledge configuration loading."""

    def test_defaults(self):
        configer = KnowledgeConfiger()
        assert configer.name is None
        assert configer.description is None
        assert configer.ext_info is None
        assert configer.stores == []
        assert configer.rag_router == "base_router"
        assert configer.post_processors == []
        assert configer.readers == {}

    def test_load_by_configer(self):
        configer = KnowledgeConfiger()
        value = {"name": "kb", "description": "docs",
                 "ext_info": {"a": 1},
                 "metadata": {"type": "knowledge", "module": "m",
                              "class": "C"}}
        returned = configer.load_by_configer(SimpleNamespace(value=value,
                                                             path="x.yaml"))
        assert returned is configer
        assert configer.name == "kb"
        assert configer.description == "docs"
        assert configer.ext_info == {"a": 1}
        assert configer.metadata_type == "knowledge"
