# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_google_search_tool_v2.py
"""Unit tests for GoogleSearchTool / GoogleScholarSearchTool mock helpers."""

import asyncio
import json

import pytest

from agentuniverse.agent.action.tool.common_tool.google_search_tool_v2 import (
    GoogleScholarSearchTool,
    GoogleSearchTool,
)


class TestGoogleSearchToolV2:
    @pytest.fixture
    def tool(self):
        return GoogleSearchTool(serper_api_key=None)

    @pytest.fixture
    def scholar(self):
        return GoogleScholarSearchTool(serper_api_key=None)

    def test_mock_fallback_when_no_key(self, tool):
        result = tool.execute('langchain')
        assert '模拟结果' in result

    def test_mock_result_contains_query(self, tool):
        result = tool.execute('agentuniverse')
        assert 'agentuniverse' in result

    def test_async_execute_mock(self, tool):
        result = asyncio.run(tool.async_execute('hello'))
        assert 'hello' in result

    def test_default_k_field(self):
        assert GoogleSearchTool().default_k == 10

    def test_scholar_mock_fallback(self, scholar):
        result = scholar.execute('llm')
        assert '学术搜索模拟结果' in result

    def test_build_scholar_query_plain(self, scholar):
        assert scholar._build_scholar_query('llm') == 'site:scholar.google.com llm'

    def test_build_scholar_query_with_filters(self, scholar):
        query = scholar._build_scholar_query('llm', year='2023', author='smith',
                                             journal='ACL')
        assert '2023' in query and 'smith' in query and 'ACL' in query

    def test_format_raw_text_result(self, tool):
        formatted = tool._format_search_result('plain body', 'q', 'search')
        assert 'plain body' in formatted

    def test_format_json_list_result(self, tool):
        items = [{'title': 'T1', 'link': 'http://x', 'snippet': 'S1'},
                 {'title': 'T2', 'link': 'http://y', 'snippet': 'S2'}]
        formatted = tool._format_search_result(json.dumps(items), 'q', 'news')
        assert 'T1' in formatted and 'T2' in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
