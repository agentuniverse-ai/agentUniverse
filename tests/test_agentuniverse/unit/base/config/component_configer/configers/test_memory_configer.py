# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_memory_configer.py
"""Unit tests for MemoryConfiger configuration parsing."""

import pytest

from agentuniverse.base.config.component_configer.configers.memory_configer import (
    MemoryConfiger,
)
from agentuniverse.base.config.configer import Configer


class TestMemoryConfiger:
    """Test MemoryConfiger field parsing from a Configer."""

    @pytest.fixture
    def configer(self):
        """Build a Configer holding a complete memory configuration."""
        configer = Configer()
        configer.value = {
            "name": "user_memory",
            "description": "stores user facts",
            "type": "conversation",
            "memory_key": "user",
            "max_tokens": 1024,
            "memory_compressor": "compressor_a",
            "memory_storages": ["sqlite", "mem0"],
            "memory_retrieval_storage": "sqlite",
            "memory_summarize_agent": "summarizer",
            "context_manager": "ctx_mgr",
        }
        return configer

    def test_defaults_before_load(self):
        """All parsed properties are None before load runs."""
        configer = MemoryConfiger(Configer())
        assert configer.name is None
        assert configer.max_tokens is None
        assert configer.memory_storages is None

    def test_load_parses_all_fields(self, configer):
        """load maps every configuration key onto its property."""
        configer = MemoryConfiger(configer).load()
        assert configer.name == "user_memory"
        assert configer.description == "stores user facts"
        assert configer.type == "conversation"
        assert configer.memory_key == "user"
        assert configer.max_tokens == 1024
        assert configer.memory_compressor == "compressor_a"
        assert configer.memory_storages == ["sqlite", "mem0"]
        assert configer.memory_retrieval_storage == "sqlite"
        assert configer.memory_summarize_agent == "summarizer"
        assert configer.context_manager == "ctx_mgr"

    def test_load_returns_self(self, configer):
        """load is fluent and returns the same configer object."""
        configer = MemoryConfiger(configer)
        assert configer.load() is configer

    def test_load_wraps_parse_failure(self):
        """A non-dict configer value raises a wrapped parse error."""
        bad_configer = Configer()
        bad_configer.value = ["not", "a", "dict"]
        with pytest.raises(Exception, match="Failed to parse the component configuration"):
            MemoryConfiger(bad_configer).load()
        # None of the parsed fields should have been populated
        configer = MemoryConfiger(Configer())
        assert configer.name is None

    def test_missing_keys_stay_none(self):
        """Keys absent from the config keep their None default."""
        empty = Configer()
        empty.value = {"name": "only_name"}
        configer = MemoryConfiger(empty).load()
        assert configer.name == "only_name"
        assert configer.max_tokens is None
        assert configer.memory_storages is None
        assert configer.context_manager is None
