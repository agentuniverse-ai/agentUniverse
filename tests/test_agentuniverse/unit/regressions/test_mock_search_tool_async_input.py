"""Regression tests for MockSearchTool async input handling."""

import asyncio

import pytest

from agentuniverse.agent.action.tool.common_tool.mock_search_tool import MockSearchTool


def test_execute_accepts_keyword_args():
    tool = MockSearchTool(input_keys=["input"])
    result = tool.execute(input="hello")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_async_run_uses_keyword_args():
    tool = MockSearchTool(input_keys=["input"])
    result = await tool.async_run(input="hello")
    assert isinstance(result, str)
    assert len(result) > 0
