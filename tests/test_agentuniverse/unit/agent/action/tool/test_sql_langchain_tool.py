# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_sql_langchain_tool.py
"""Unit tests for SqlLangchainTool configuration."""

import pytest

from agentuniverse.agent.action.tool.common_tool.langchain_tool import LangChainTool
from agentuniverse.agent.action.tool.common_tool.sql_langchain_tool import SqlLangchainTool
from langchain_core.tools import BaseTool


class FakeSqlCls:
    """Minimal stand-in for the SQL langchain tool class."""

    def __init__(self, db=None):
        self.db = db


class FakeExecTool:
    """In-memory tool stand-in exposing run()."""

    def run(self, input, callbacks=None):
        return f'exec:{input}'


class TestSqlLangchainTool:
    def test_defaults(self):
        tool = SqlLangchainTool()
        assert tool.db_wrapper_name == ''
        assert tool.clz is BaseTool
        assert tool.tool is None

    def test_is_langchain_tool_subclass(self):
        assert isinstance(SqlLangchainTool(), LangChainTool)

    def test_get_langchain_tool_stores_wrapper_name(self):
        tool = SqlLangchainTool()
        tool.get_langchain_tool({'db_wrapper': 'default_db'}, FakeSqlCls)
        assert tool.db_wrapper_name == 'default_db'
        assert tool.clz is FakeSqlCls

    def test_execute_delegates_to_wrapped_tool_when_set(self):
        tool = SqlLangchainTool()
        tool.tool = FakeExecTool()
        assert tool.execute('select 1', None) == 'exec:select 1'

    def test_description_default_none(self):
        assert SqlLangchainTool().description is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
