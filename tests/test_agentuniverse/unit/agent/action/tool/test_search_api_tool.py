# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_search_api_tool.py
"""Unit tests for SearchAPITool request dispatch."""

import pytest

from agentuniverse.agent.action.tool.common_tool.search_api_tool import SearchAPITool
from agentuniverse.agent.action.tool.tool import ToolInput


class FakeSearchWrapper:
    """In-memory stand-in for the SearchApi wrapper."""

    def __init__(self):
        self.last_query = None

    def run(self, query=None, **kwargs):
        self.last_query = query
        return f'run:{query}'

    def results(self, query=None, **kwargs):
        self.last_query = query
        return f'json:{query}'

    async def arun(self, query=None, **kwargs):
        return f'arun:{query}'

    async def aresults(self, query=None, **kwargs):
        return f'ajson:{query}'


class TestSearchAPITool:
    @pytest.fixture
    def tool(self, monkeypatch):
        monkeypatch.delenv('SEARCHAPI_API_KEY', raising=False)
        tool = SearchAPITool()
        tool.search_api_wrapper = FakeSearchWrapper()
        monkeypatch.setattr(SearchAPITool, '_load_api_wapper', lambda self: self.search_api_wrapper)
        return tool

    def test_default_engine_and_search_type(self):
        tool = SearchAPITool()
        assert tool.engine == 'google'
        assert tool.search_type == 'common'
        assert tool.search_params == {}

    def test_load_wrapper_raises_without_key(self, monkeypatch):
        monkeypatch.delenv('SEARCHAPI_API_KEY', raising=False)
        tool = SearchAPITool()
        with pytest.raises(ValueError, match='SEARCHAPI_API_KEY'):
            tool._load_api_wapper()

    def test_key_reads_env(self, monkeypatch):
        monkeypatch.setenv('SEARCHAPI_API_KEY', 'sk-search')
        assert SearchAPITool().search_api_key == 'sk-search'

    def test_common_execute_uses_run(self, tool):
        assert tool.execute('python') == 'run:python'
        assert tool.search_api_wrapper.last_query == 'python'

    def test_json_execute_uses_results(self, tool):
        tool.search_type = 'json'
        assert tool.execute('python') == 'json:python'

    def test_execute_merges_search_params(self, tool):
        tool.search_params = {'engine': 'google'}
        result = tool.execute('python', engine='bing')
        assert result == 'run:python'
        assert tool.search_api_wrapper.last_query == 'python'

    def test_async_execute_common(self, tool):
        import asyncio

        async def run():
            return await tool.async_execute(ToolInput({'input': 'async-q'}))

        assert asyncio.run(run()) == 'arun:async-q'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
