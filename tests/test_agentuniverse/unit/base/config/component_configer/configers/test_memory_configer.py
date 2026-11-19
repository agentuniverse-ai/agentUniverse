# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the MemoryConfiger component configer."""

import pytest

from agentuniverse.base.config.component_configer.configers.memory_configer import MemoryConfiger
from agentuniverse.base.config.configer import Configer


def _build_configer(value: dict) -> Configer:
    configer = Configer()
    configer.value = value
    return configer


class TestMemoryConfiger:
    """Tests for the MemoryConfiger class."""

    def test_properties_default_to_none(self):
        configer = MemoryConfiger()
        assert configer.name is None
        assert configer.description is None
        assert configer.type is None
        assert configer.memory_key is None
        assert configer.max_tokens is None
        assert configer.memory_compressor is None
        assert configer.memory_storages is None
        assert configer.memory_retrieval_storage is None
        assert configer.memory_summarize_agent is None
        assert configer.context_manager is None

    def test_load_by_configer_populates_all_fields(self):
        configer = _build_configer({
            "name": "test_memory",
            "description": "a test memory",
            "type": "memory_type",
            "memory_key": "chat_history",
            "max_tokens": 1024,
            "memory_compressor": "default_compressor",
            "memory_storages": ["store_a", "store_b"],
            "memory_retrieval_storage": "store_a",
            "memory_summarize_agent": "summarize_agent",
            "context_manager": "context_manager",
        })
        memory_configer = MemoryConfiger().load_by_configer(configer)
        assert memory_configer.name == "test_memory"
        assert memory_configer.description == "a test memory"
        assert memory_configer.type == "memory_type"
        assert memory_configer.memory_key == "chat_history"
        assert memory_configer.max_tokens == 1024
        assert memory_configer.memory_compressor == "default_compressor"
        assert memory_configer.memory_storages == ["store_a", "store_b"]
        assert memory_configer.memory_retrieval_storage == "store_a"
        assert memory_configer.memory_summarize_agent == "summarize_agent"
        assert memory_configer.context_manager == "context_manager"

    def test_load_by_configer_missing_keys_stay_none(self):
        configer = _build_configer({"name": "partial_memory"})
        memory_configer = MemoryConfiger().load_by_configer(configer)
        assert memory_configer.name == "partial_memory"
        assert memory_configer.type is None
        assert memory_configer.memory_storages is None

    def test_load_uses_constructor_configer(self):
        configer = _build_configer({"name": "ctor_memory", "type": "memory_type"})
        memory_configer = MemoryConfiger(configer).load()
        assert memory_configer.name == "ctor_memory"
        assert memory_configer.type == "memory_type"

    def test_load_returns_self(self):
        configer = _build_configer({"name": "self_memory"})
        memory_configer = MemoryConfiger()
        assert memory_configer.load_by_configer(configer) is memory_configer
        assert memory_configer.load() is memory_configer

    def test_load_without_configer_raises(self):
        with pytest.raises(Exception):
            MemoryConfiger().load()
