# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_wikipedia_query.py
"""Unit tests for WikipediaTool."""

import pytest

from agentuniverse.agent.action.tool.common_tool.langchain_tool import LangChainTool
from agentuniverse.agent.action.tool.common_tool.wikipedia_query import WikipediaTool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


class TestWikipediaTool:
    def test_is_langchain_tool_subclass(self):
        assert isinstance(WikipediaTool(), LangChainTool)

    def test_init_langchain_tool_returns_query_run(self):
        tool = WikipediaTool()
        wrapped = tool.init_langchain_tool(None)
        assert isinstance(wrapped, WikipediaQueryRun)

    def test_wrapped_api_wrapper_type(self):
        tool = WikipediaTool()
        wrapped = tool.init_langchain_tool(None)
        assert isinstance(wrapped.api_wrapper, WikipediaAPIWrapper)

    def test_default_state(self):
        tool = WikipediaTool()
        assert tool.name == ''
        assert tool.tool is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
