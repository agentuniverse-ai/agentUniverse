# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_mcp_server_manager.py

"""Unit tests for MCPServerManager registration logic."""

from copy import deepcopy
from types import SimpleNamespace

import pytest

from agentuniverse.agent_serve.web.mcp.mcp_server_manager import (
    DEFAULT_SERVER_NAME,
    MCPServerManager,
    is_method_overridden,
)
from agentuniverse.base.component.component_enum import ComponentEnum

DEFAULT_MAP = {DEFAULT_SERVER_NAME: {"tool": [], "toolkit": []}}


@pytest.fixture(autouse=True)
def reset_server_map():
    manager = MCPServerManager()
    manager.server_tool_map = deepcopy(DEFAULT_MAP)
    yield manager
    manager.server_tool_map = deepcopy(DEFAULT_MAP)


def test_default_server_name():
    assert DEFAULT_SERVER_NAME == "default_mcp_server"


class TestIsMethodOverridden:
    """Test the method-override detection helper."""

    def test_non_callable_is_not_overridden(self):
        assert is_method_overridden(None, object()) is False

    def test_missing_origin_counts_as_overridden(self):
        assert is_method_overridden(lambda: None, None) is True

    def test_different_method_counts_as_overridden(self):
        def first():
            pass

        def second():
            pass

        assert is_method_overridden(first, second) is True

    def test_same_method_is_not_overridden(self):
        def same():
            pass

        assert is_method_overridden(same, same) is False


class TestRegisterMcpTool:
    """Test registering tools and toolkits to mcp servers."""

    def test_new_server_entry_created_for_dict_config(self, reset_server_map):
        configer = SimpleNamespace(
            as_mcp_tool={"server_name": "srv1"}, name="toolA")
        reset_server_map.register_mcp_tool(configer,
                                           ComponentEnum.TOOL.value)
        assert reset_server_map.server_tool_map["srv1"]["tool"] == ["toolA"]

    def test_default_server_for_bool_config(self, reset_server_map):
        configer = SimpleNamespace(as_mcp_tool=True, name="toolB")
        reset_server_map.register_mcp_tool(configer,
                                           ComponentEnum.TOOL.value)
        assert reset_server_map.server_tool_map[DEFAULT_SERVER_NAME][
            "tool"] == ["toolB"]

    def test_non_mcp_config_is_ignored(self, reset_server_map):
        configer = SimpleNamespace(as_mcp_tool=None, name="toolC")
        reset_server_map.register_mcp_tool(configer,
                                           ComponentEnum.TOOL.value)
        assert reset_server_map.server_tool_map == DEFAULT_MAP

    def test_toolkit_type_goes_to_toolkit_list(self, reset_server_map):
        configer = SimpleNamespace(as_mcp_tool=True, name="tkA")
        reset_server_map.register_mcp_tool(configer,
                                           ComponentEnum.TOOLKIT.value)
        assert reset_server_map.server_tool_map[DEFAULT_SERVER_NAME][
            "toolkit"] == ["tkA"]
        assert reset_server_map.server_tool_map[DEFAULT_SERVER_NAME][
            "tool"] == []

    def test_multiple_tools_accumulate(self, reset_server_map):
        first = SimpleNamespace(as_mcp_tool=True, name="t1")
        second = SimpleNamespace(as_mcp_tool=True, name="t2")
        reset_server_map.register_mcp_tool(first, ComponentEnum.TOOL.value)
        reset_server_map.register_mcp_tool(second, ComponentEnum.TOOL.value)
        assert reset_server_map.server_tool_map[DEFAULT_SERVER_NAME][
            "tool"] == ["t1", "t2"]
