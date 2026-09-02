# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_mock_search_tool.py
"""Unit tests for MockSearchTool."""

import asyncio

import pytest

from agentuniverse.agent.action.tool.common_tool.mock_search_tool import MockSearchTool
from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class TestMockSearchTool:
    @pytest.fixture
    def tool(self):
        return MockSearchTool(name='mock_search')

    def test_is_tool_subclass(self, tool):
        assert isinstance(tool, Tool)

    def test_execute_returns_mock_text(self, tool):
        result = tool.execute('任何问题')
        assert isinstance(result, str)
        assert '巴菲特' in result

    def test_execute_ignores_query_content(self, tool):
        assert tool.execute('query-a') == tool.execute('query-b')

    def test_mock_result_is_long(self, tool):
        assert len(tool.mock_api_res()) > 100

    def test_async_execute_matches_sync(self, tool):
        tool_input = ToolInput({'input': '问题'})
        async_result = asyncio.run(tool.async_execute(tool_input))
        assert async_result == tool.execute('问题')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
