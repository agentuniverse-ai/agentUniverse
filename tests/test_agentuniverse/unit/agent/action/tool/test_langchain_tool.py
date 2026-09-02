# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_langchain_tool.py
"""Unit tests for LangChainTool wrapper behaviour."""

import asyncio

import pytest

from agentuniverse.agent.action.tool.common_tool.langchain_tool import LangChainTool


class FakeLangchainTool:
    """In-memory stand-in for a langchain tool."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def run(self, input, callbacks=None):
        return f'run:{input}:{callbacks}'

    async def arun(self, input, callbacks=None):
        return f'arun:{input}:{callbacks}'


class TestLangChainTool:
    def test_default_state(self):
        tool = LangChainTool()
        assert tool.name == ''
        assert tool.tool is None

    def test_get_langchain_tool_with_params(self):
        tool = LangChainTool()
        tool.get_langchain_tool({'size': 3}, FakeLangchainTool)
        assert isinstance(tool.tool, FakeLangchainTool)
        assert tool.tool.kwargs == {'size': 3}

    def test_get_langchain_tool_without_params(self):
        tool = LangChainTool()
        tool.get_langchain_tool(None, FakeLangchainTool)
        assert isinstance(tool.tool, FakeLangchainTool)
        assert tool.tool.kwargs == {}

    def test_execute_delegates_to_run(self):
        tool = LangChainTool()
        tool.tool = FakeLangchainTool()
        assert tool.execute('hello', 'cb') == 'run:hello:cb'

    def test_async_execute_delegates_to_arun(self):
        tool = LangChainTool()
        tool.tool = FakeLangchainTool()
        assert asyncio.run(tool.async_execute('hello', None)) == 'arun:hello:None'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
