# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_bing_search_tool.py
"""Unit tests for BingSearchTool fallback behaviour."""

import pytest

from agentuniverse.agent.action.tool.common_tool.bing_search_tool import BingSearchTool
from agentuniverse.agent.action.tool.common_tool.mock_search_tool import MockSearchTool
from agentuniverse.agent.action.tool.tool import Tool


class TestBingSearchTool:
    def test_is_tool_subclass(self):
        assert isinstance(BingSearchTool(), Tool)

    def test_default_search_url(self):
        tool = BingSearchTool()
        assert tool.bing_search_url == 'https://api.bing.microsoft.com/v7.0/search'

    def test_key_reads_env(self, monkeypatch):
        monkeypatch.setenv('BING_SUBSCRIPTION_KEY', 'sk-bing')
        assert BingSearchTool().bing_subscription_key == 'sk-bing'

    def test_mock_fallback_when_no_key(self):
        tool = BingSearchTool(bing_subscription_key=None)
        result = tool.execute('hello')
        assert isinstance(result, str)
        assert '巴菲特' in result

    def test_mock_fallback_matches_mock_search_tool(self):
        tool = BingSearchTool(bing_subscription_key=None)
        assert tool.execute('hello') == MockSearchTool().execute('hello')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
