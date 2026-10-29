"""Regular SQL tool calls should not require a callbacks business argument."""
import asyncio
import json
import sqlite3
from types import SimpleNamespace

import pytest
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.callbacks import BaseCallbackHandler

from agentuniverse.agent.action.tool.common_tool.sql_langchain_tool import SqlLangchainTool
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager


SQL = 'SELECT name FROM items ORDER BY name'
EXPECTED = "[('alpha',)]"


@pytest.fixture
def sql_tool(tmp_path, monkeypatch):
    path = tmp_path / 'offline.sqlite'
    with sqlite3.connect(path) as connection:
        connection.execute('CREATE TABLE items (name TEXT)')
        connection.execute("INSERT INTO items VALUES ('alpha')")
    database = SQLDatabase.from_uri(f'sqlite:///{path}')
    monkeypatch.setattr(ApplicationConfigManager(), '_ApplicationConfigManager__app_configer', AppConfiger())
    monkeypatch.setattr(SQLDBWrapperManager(), 'get_instance_obj',
                        lambda name: SimpleNamespace(sql_database=database))
    tool = SqlLangchainTool(name='offline_sql', description='Offline SQL query', input_keys=['input'],
                           db_wrapper_name='offline', clz=QuerySQLDataBaseTool)
    try:
        yield tool
    finally:
        database._engine.dispose()


@pytest.mark.parametrize('entry', ['execute', 'async_execute', 'run', 'async_run', 'invoke', 'ainvoke'])
def test_sql_entry_points_accept_only_sql_input(sql_tool, entry):
    if entry == 'invoke':
        result = sql_tool.as_langchain().invoke(json.dumps({'input': SQL}))
    elif entry == 'ainvoke':
        async def run():
            converted = await sql_tool.async_as_langchain()
            return await converted.ainvoke(json.dumps({'input': SQL}))
        result = asyncio.run(run())
    elif entry in ('async_execute', 'async_run'):
        result = asyncio.run(getattr(sql_tool, entry)(input=SQL))
    else:
        result = getattr(sql_tool, entry)(input=SQL)
    assert result == EXPECTED
    assert isinstance(sql_tool.tool, QuerySQLDataBaseTool)


class RecordingHandler(BaseCallbackHandler):
    def __init__(self):
        self.outputs = []

    def on_tool_end(self, output, **kwargs):
        self.outputs.append(output)


@pytest.mark.parametrize('is_async', [False, True])
def test_explicit_callbacks_still_reach_native_tool(sql_tool, is_async):
    handler = RecordingHandler()
    if is_async:
        result = asyncio.run(sql_tool.async_execute(input=SQL, callbacks=[handler]))
    else:
        result = sql_tool.execute(input=SQL, callbacks=[handler])
    assert result == EXPECTED
    assert handler.outputs == [EXPECTED]
