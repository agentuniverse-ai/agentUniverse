# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_mcp_toolkit.py

"""Unit tests for MCPToolkit connect-args and naming behavior."""

import pytest

from agentuniverse.agent.action.toolkit.mcp_toolkit import MCPToolkit


class TestMCPToolkit:
    """Test MCPToolkit connection args and prefixed tool names."""

    def test_default_transport_is_stdio(self):
        toolkit = MCPToolkit(name="mtk")
        assert toolkit.transport == "stdio"
        assert toolkit.always_refresh is False

    def test_stdio_connect_args(self):
        toolkit = MCPToolkit(name="mtk", command="python", args=["-m", "srv"],
                             env={"A": "1"})
        assert toolkit.get_mcp_server_connect_args() == {
            "transport": "stdio", "command": "python",
            "args": ["-m", "srv"], "env": {"A": "1"}}

    def test_sse_connect_args_with_connection_kwargs(self):
        toolkit = MCPToolkit(name="mtk", transport="sse",
                             url="http://localhost:8000/sse",
                             connection_kwargs={"timeout": 30})
        assert toolkit.get_mcp_server_connect_args() == {
            "transport": "sse", "url": "http://localhost:8000/sse",
            "timeout": 30}

    def test_websocket_connect_args(self):
        toolkit = MCPToolkit(name="mtk", transport="websocket",
                             url="ws://localhost:9000")
        assert toolkit.get_mcp_server_connect_args() == {
            "transport": "websocket", "url": "ws://localhost:9000"}

    def test_streamable_http_connect_args(self):
        toolkit = MCPToolkit(name="mtk", transport="streamable_http",
                             url="http://localhost:8000/mcp")
        assert toolkit.get_mcp_server_connect_args() == {
            "transport": "streamable_http",
            "url": "http://localhost:8000/mcp"}

    def test_unsupported_transport_raises(self):
        toolkit = MCPToolkit(name="mtk")
        toolkit.transport = "carrier-pigeon"
        with pytest.raises(Exception, match="Unsupported mcp server type"):
            toolkit.get_mcp_server_connect_args()

    def test_tool_names_are_prefixed_with_toolkit_name(self):
        toolkit = MCPToolkit(name="mtk", include=["tool_a", "tool_b"])
        assert toolkit.tool_names == ["mtk@tool_a", "mtk@tool_b"]

    def test_func_call_list_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            MCPToolkit(name="mtk").func_call_list
