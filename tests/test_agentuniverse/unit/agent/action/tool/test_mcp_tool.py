# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_mcp_tool.py

"""Unit tests for MCPTool naming and connection-args behavior."""

import pytest

from agentuniverse.agent.action.tool.mcp_tool import MCPTool


class TestMCPTool:
    """Test MCPTool tool naming and mcp server connect args."""

    def test_default_transport_is_stdio(self):
        tool = MCPTool(name="tool_x")
        assert tool.transport == "stdio"
        assert tool.origin_tool_name == ""

    def test_tool_name_prefers_origin_name(self):
        tool = MCPTool(name="au_name", origin_tool_name="mcp_name")
        assert tool.tool_name == "mcp_name"
        assert MCPTool(name="au_name").tool_name == "au_name"

    def test_stdio_connect_args(self):
        tool = MCPTool(name="x", command="python", args=["srv.py"],
                       env={"A": "1"})
        assert tool.get_mcp_server_connect_args() == {
            "transport": "stdio", "command": "python",
            "args": ["srv.py"], "env": {"A": "1"}}

    def test_sse_connect_args_with_connection_kwargs(self):
        tool = MCPTool(name="x", transport="sse",
                       url="http://localhost:8000/sse",
                       connection_kwargs={"timeout": 30})
        assert tool.get_mcp_server_connect_args() == {
            "transport": "sse", "url": "http://localhost:8000/sse",
            "timeout": 30}

    def test_streamable_http_connect_args(self):
        tool = MCPTool(name="x", transport="streamable_http",
                       url="http://localhost:8000/mcp")
        assert tool.get_mcp_server_connect_args() == {
            "transport": "streamable_http",
            "url": "http://localhost:8000/mcp"}

    def test_unsupported_transport_raises(self):
        tool = MCPTool(name="x")
        tool.transport = "carrier-pigeon"
        with pytest.raises(Exception, match="Unsupported mcp server type"):
            tool.get_mcp_server_connect_args()

    def test_invalid_transport_rejected_on_construction(self):
        with pytest.raises(Exception):
            MCPTool(name="x", transport="carrier-pigeon")
