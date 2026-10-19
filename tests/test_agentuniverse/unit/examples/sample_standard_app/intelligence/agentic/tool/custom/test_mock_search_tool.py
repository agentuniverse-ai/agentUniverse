# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_mock_search_tool.py
"""Unit tests for the MockSearchTool example tool.

The mock tool returns a fixed canned search result and never performs any real
network request, so its behavior is fully deterministic.
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[9]))

from agentuniverse.agent.action.tool.tool import Tool
from examples.sample_standard_app.intelligence.agentic.tool.custom.mock_search_tool import \
    MockSearchTool


class TestMockSearchTool:
    """Test the MockSearchTool example tool."""

    @pytest.fixture
    def tool(self) -> MockSearchTool:
        return MockSearchTool()

    def test_is_tool_subclass(self):
        assert issubclass(MockSearchTool, Tool)

    def test_mock_api_res_returns_string(self, tool):
        assert isinstance(tool.mock_api_res(), str)

    def test_mock_api_res_is_not_empty(self, tool):
        assert tool.mock_api_res().strip()

    def test_mock_api_res_contains_expected_markers(self, tool):
        res = tool.mock_api_res()
        assert '巴菲特' in res
        assert '比亚迪' in res

    def test_execute_matches_mock_api_res(self, tool):
        assert tool.execute('anything') == tool.mock_api_res()

    def test_execute_ignores_input(self, tool):
        assert tool.execute('first query') == tool.execute('second query')

    def test_execute_returns_string(self, tool):
        assert isinstance(tool.execute('query'), str)
