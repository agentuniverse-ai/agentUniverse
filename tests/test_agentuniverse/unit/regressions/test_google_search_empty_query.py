import asyncio

import pytest

from agentuniverse.agent.action.tool.common_tool.google_search_tool_v2 import GoogleSearchTool


@pytest.mark.parametrize("query", [None, "", "   "])
def test_empty_query_does_not_return_mock_results(query):
    tool = GoogleSearchTool(serper_api_key=None)

    assert tool.execute(query) == "搜索查询不能为空"
    assert asyncio.run(tool.async_execute(query)) == "搜索查询不能为空"
