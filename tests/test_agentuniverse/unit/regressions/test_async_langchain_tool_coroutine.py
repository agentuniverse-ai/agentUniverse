"""Regression tests for async LangChain tool coroutine registration."""

import pytest

from agentuniverse.agent.action.tool.common_tool.mock_search_tool import MockSearchTool


@pytest.mark.asyncio
async def test_async_as_langchain_registers_coroutine_and_sync_adapter():
    tool = MockSearchTool(input_keys=["input"])
    lc_tool = await tool.async_as_langchain()

    assert lc_tool.coroutine is not None
    assert lc_tool.func is not None
    assert callable(lc_tool.coroutine)
    assert callable(lc_tool.func)
