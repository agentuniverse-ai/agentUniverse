"""Reject unusable academic queries before mock output or provider construction."""
import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from agentuniverse.agent.action.tool.common_tool.google_search_tool_v2 import GoogleScholarSearchTool

MODULE = 'agentuniverse.agent.action.tool.common_tool.google_search_tool_v2'


@pytest.mark.parametrize('query', [None, '', ' \t\n', 42])
@pytest.mark.parametrize('api_key', [None, 'offline-placeholder'])
def test_invalid_queries_do_not_construct_provider_or_mock_results(query, api_key):
    tool = GoogleScholarSearchTool(serper_api_key=api_key)
    with patch(MODULE + '.GoogleSerperAPIWrapper') as wrapper:
        assert tool.execute(query) == '搜索查询不能为空'
        assert asyncio.run(tool.async_execute(query)) == '搜索查询不能为空'
    wrapper.assert_not_called()


def test_valid_query_keeps_filters_and_sync_async_paths():
    tool = GoogleScholarSearchTool(serper_api_key='offline-placeholder')
    wrapper = Mock()
    wrapper.run.return_value = 'sync result'
    wrapper.arun = AsyncMock(return_value='async result')
    with patch(MODULE + '.GoogleSerperAPIWrapper', return_value=wrapper):
        sync = tool.execute('battery', year='2024', author='A', journal='J', k=3)
        asynchronous = asyncio.run(tool.async_execute('battery', year='2024', author='A', journal='J', k=3))
    query = 'site:scholar.google.com battery author:"A" journal:"J" 2024'
    wrapper.run.assert_called_once_with(query=query)
    wrapper.arun.assert_awaited_once_with(query=query)
    assert 'sync result' in sync
    assert 'async result' in asynchronous


def test_valid_query_without_key_keeps_explicitly_labeled_mock_results():
    tool = GoogleScholarSearchTool(serper_api_key=None)
    assert '模拟结果' in tool.execute('battery')
    assert '模拟结果' in asyncio.run(tool.async_execute('battery'))
