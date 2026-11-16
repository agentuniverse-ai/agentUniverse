"""SQL tools initialize their wrapped database tool on asynchronous first use."""
import asyncio
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.tools import BaseTool

from agentuniverse.agent.action.tool.common_tool.sql_langchain_tool import SqlLangchainTool
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager


class QueryTool(BaseTool):
    name = "query"
    description = "Query the configured database."
    db: Any

    def _run(self, query):
        return "sync:" + query

    async def _arun(self, query):
        return "async:" + query


class RecordingHandler(BaseCallbackHandler):
    def __init__(self):
        self.outputs = []

    def on_tool_end(self, output, **kwargs):
        self.outputs.append(output)


def make_tool(monkeypatch):
    database = object()
    lookup = Mock(return_value=SimpleNamespace(sql_database=database))
    monkeypatch.setattr(SQLDBWrapperManager(), "get_instance_obj", lookup)
    return SqlLangchainTool(db_wrapper_name="local", clz=QueryTool), database, lookup


def test_async_first_initializes_and_reuses_database_tool(monkeypatch):
    tool, database, lookup = make_tool(monkeypatch)
    handler = RecordingHandler()
    assert asyncio.run(tool.async_execute("select 1", callbacks=[handler])) == "async:select 1"
    wrapped = tool.tool
    assert wrapped.db is database
    assert tool.description == QueryTool.__fields__["description"].default
    assert asyncio.run(tool.async_execute("select 2", callbacks=[handler])) == "async:select 2"
    assert tool.tool is wrapped
    lookup.assert_called_once_with("local")
    assert handler.outputs == ["async:select 1", "async:select 2"]


def test_sync_first_then_async_reuses_tool(monkeypatch):
    tool, database, lookup = make_tool(monkeypatch)
    assert tool.execute("select 1", callbacks=None) == "sync:select 1"
    wrapped = tool.tool
    assert asyncio.run(tool.async_execute("select 2", callbacks=None)) == "async:select 2"
    assert tool.tool is wrapped
    assert wrapped.db is database
    lookup.assert_called_once_with("local")


def test_sync_and_async_execution_accept_ordinary_input_only(monkeypatch):
    tool, database, lookup = make_tool(monkeypatch)

    assert tool.execute("select 1") == "sync:select 1"
    assert asyncio.run(tool.async_execute("select 2")) == "async:select 2"
    assert tool.tool.db is database
    lookup.assert_called_once_with("local")


def test_preconfigured_tool_does_not_resolve_database(monkeypatch):
    tool, database, lookup = make_tool(monkeypatch)
    wrapped = QueryTool(db=database)
    tool.tool = wrapped
    assert asyncio.run(tool.async_execute("select 1", callbacks=None)) == "async:select 1"
    assert tool.tool is wrapped
    lookup.assert_not_called()
