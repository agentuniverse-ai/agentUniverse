# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_tool_configer.py

"""Unit tests for the ToolConfiger."""

from types import SimpleNamespace

from agentuniverse.base.config.component_configer.configers.tool_configer import \
    ToolConfiger


class TestToolConfiger:
    """Test tool configuration loading."""

    def test_defaults(self):
        configer = ToolConfiger()
        assert configer.name is None
        assert configer.description is None
        assert configer.tool_type is None
        assert configer.input_keys is None

    def test_load_by_configer(self):
        configer = ToolConfiger()
        value = {"name": "api_tool", "description": "call api",
                 "tool_type": "api", "input_keys": ["q"],
                 "metadata": {"type": "tool", "module": "m", "class": "C"}}
        returned = configer.load_by_configer(SimpleNamespace(value=value,
                                                             path="x.yaml"))
        assert returned is configer
        assert configer.name == "api_tool"
        assert configer.description == "call api"
        assert configer.tool_type == "api"
        assert configer.input_keys == ["q"]
        assert configer.metadata_type == "tool"
