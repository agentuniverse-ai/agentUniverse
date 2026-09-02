# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/13 10:00
# @Author  : kaichuan
# @FileName: test_tool_configer.py
"""Unit tests for ToolConfiger."""

import pytest

from agentuniverse.base.config.component_configer.configers.tool_configer import (
    ToolConfiger,
)
from agentuniverse.base.config.configer import Configer


class TestToolConfiger:
    """Test ToolConfiger defaults and load behavior."""

    def test_default_values_before_load(self):
        """A freshly constructed configer has all fields unset."""
        configer = ToolConfiger()
        assert configer.name is None
        assert configer.description is None
        assert configer.tool_type is None
        assert configer.input_keys is None

    def test_load_populates_all_fields(self):
        """load() copies every declared field from the Configer value."""
        configer = Configer()
        configer.value = {
            "name": "search_tool",
            "description": "Search the web",
            "tool_type": "api",
            "input_keys": ["query", "limit"],
        }
        loaded = ToolConfiger(configer).load()
        assert loaded.name == "search_tool"
        assert loaded.description == "Search the web"
        assert loaded.tool_type == "api"
        assert loaded.input_keys == ["query", "limit"]

    def test_load_partial_value_leaves_missing_fields_none(self):
        """Only keys present in the value are populated; others stay None."""
        configer = Configer()
        configer.value = {"name": "only_name"}
        loaded = ToolConfiger(configer).load()
        assert loaded.name == "only_name"
        assert loaded.description is None
        assert loaded.tool_type is None
        assert loaded.input_keys is None

    def test_load_preserves_input_keys_order(self):
        """input_keys is stored as-is, preserving list order."""
        configer = Configer()
        configer.value = {"name": "t", "input_keys": ["b", "a", "c"]}
        loaded = ToolConfiger(configer).load()
        assert loaded.input_keys == ["b", "a", "c"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
