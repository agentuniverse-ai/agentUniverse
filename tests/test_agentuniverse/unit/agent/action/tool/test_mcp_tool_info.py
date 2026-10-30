# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Regression tests for MCPTool.get_tool_info inputSchema handling.

`required` is an optional key in a JSON Schema; an MCP tool whose
inputSchema omits it must register with empty input_keys instead of
raising KeyError during initialization.
"""
import asyncio
from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.tool import mcp_tool as mcp_tool_module
from agentuniverse.agent.action.tool.mcp_tool import MCPTool


class _FakeSession:
    def __init__(self, tools):
        self._tools = tools

    async def list_tools(self):
        return SimpleNamespace(tools=self._tools)


class _FakeTempClient:
    """Stands in for MCPTempClient; no server connection is made."""

    instances: list = []

    def __init__(self, connect_args):
        self.connect_args = connect_args
        self.session = None
        _FakeTempClient.instances.append(self)

    def set_tools(self, tools):
        self.session = _FakeSession(tools)
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


def _make_tool(schema) -> MCPTool:
    fake_tool = SimpleNamespace(
        name="target",
        inputSchema=schema,
        description="a fake mcp tool",
    )
    _FakeTempClient.instances = []
    original = mcp_tool_module.MCPTempClient
    mcp_tool_module.MCPTempClient = _FakeTempClient
    # Pre-register the fake tools on the next client instance.
    original_init = _FakeTempClient.__init__

    def init(self, connect_args):
        original_init(self, connect_args)
        self.set_tools([fake_tool])

    _FakeTempClient.__init__ = init
    try:
        tool = MCPTool(name="target")
        asyncio.run(tool.get_tool_info())
    finally:
        mcp_tool_module.MCPTempClient = original
        _FakeTempClient.__init__ = original_init
    return tool


def test_input_keys_defaults_to_empty_when_required_missing():
    tool = _make_tool({
        "type": "object",
        "properties": {"q": {"type": "string"}},
    })
    assert tool.input_keys == []
    assert tool.args_model_schema == {
        "type": "object",
        "properties": {"q": {"type": "string"}},
    }


def test_input_keys_keeps_declared_required_list():
    tool = _make_tool({
        "type": "object",
        "properties": {"q": {"type": "string"}},
        "required": ["q"],
    })
    assert tool.input_keys == ["q"]


def test_input_keys_null_required_becomes_empty():
    tool = _make_tool({"type": "object", "required": None})
    assert tool.input_keys == []


def test_missing_tool_still_raises():
    schema = {"type": "object", "properties": {}}
    fake_other = SimpleNamespace(
        name="other", inputSchema=schema, description="d")
    _FakeTempClient.instances = []
    original = mcp_tool_module.MCPTempClient
    mcp_tool_module.MCPTempClient = _FakeTempClient
    original_init = _FakeTempClient.__init__

    def init(self, connect_args):
        original_init(self, connect_args)
        self.set_tools([fake_other])

    _FakeTempClient.__init__ = init
    try:
        tool = MCPTool(name="target")
        with pytest.raises(Exception, match="No tool named target"):
            asyncio.run(tool.get_tool_info())
    finally:
        mcp_tool_module.MCPTempClient = original
        _FakeTempClient.__init__ = original_init
