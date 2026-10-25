"""Multiple configured SQL memory tables must have independent indexes."""
import os
import uuid

import pytest
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine, inspect

from agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage import (
    DefaultMemoryConverter, SqlAlchemyMemoryStorage,
)
from agentuniverse.agent.memory.message import Message
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


@pytest.fixture(params=["sqlite", "postgresql"])
def database(request, tmp_path):
    if request.param == "postgresql":
        url = os.getenv("AU_TEST_POSTGRES_URL")
        if not url:
            pytest.skip("set AU_TEST_POSTGRES_URL to an isolated PostgreSQL database")
    else:
        url = "sqlite:///" + str(tmp_path / "memory.db")
    engine = create_engine(url)
    wrapper = SQLDBWrapper()
    wrapper._SQLDBWrapper__sql_database = SQLDatabase(engine)
    tables = []

    def make_storage(name, legacy=False):
        converter = DefaultMemoryConverter(name)
        table = converter.model_class.__table__
        tables.append(table)
        if legacy:
            names = {
                "session_id": "idx_session_id_source",
                "agent_id": "idx_agent_id_source",
                "gmt_created": "idx_gmt_created",
            }
            for index in table.indexes:
                index.name = names[list(index.columns)[0].name]
        # Commit schema creation explicitly to isolate index naming from the
        # separate transactional-DDL issue addressed by upstream PR #4022.
        table.create(engine)
        memory = SqlAlchemyMemoryStorage(
            sqldb_table_name=name, memory_converter=converter,
        )
        memory._sqldb_wrapper = wrapper
        return memory

    try:
        yield make_storage, engine
    finally:
        for table in reversed(tables):
            table.drop(engine, checkfirst=True)
        engine.dispose()


@pytest.mark.parametrize("suffix", ["", " Space", "_" + "long_name_" * 3])
def test_two_tables_keep_indexes_and_messages_separate(database, suffix):
    make_storage, engine = database
    prefix = "memory_" + uuid.uuid4().hex[:12]
    first = make_storage(prefix + suffix + "_a")
    second = make_storage(prefix + suffix + "_b")
    first.add([Message(type="human", content="first")], session_id="same")
    second.add([Message(type="human", content="second")], session_id="same")
    assert [m.content for m in first.get(session_id="same")] == ["first"]
    assert [m.content for m in second.get(session_id="same")] == ["second"]
    inspector = inspect(engine)
    first_indexes = inspector.get_indexes(first.sqldb_table_name)
    second_indexes = inspector.get_indexes(second.sqldb_table_name)
    expected_columns = {
        ("session_id", "agent_id", "source"), ("agent_id", "source"),
        ("gmt_created",),
    }
    for indexes in (first_indexes, second_indexes):
        assert {tuple(i["column_names"]) for i in indexes} == expected_columns
    assert {i["name"] for i in first_indexes}.isdisjoint(
        {i["name"] for i in second_indexes})


def test_new_table_coexists_with_legacy_index_names(database):
    make_storage, engine = database
    prefix = "memory_" + uuid.uuid4().hex[:12]
    legacy = make_storage(prefix + "_legacy", legacy=True)
    legacy.add([Message(type="human", content="kept")], session_id="s")
    before = inspect(engine).get_indexes(legacy.sqldb_table_name)
    current = make_storage(prefix + "_new")
    current.add([Message(type="ai", content="new")], session_id="s")
    assert [m.content for m in legacy.get(session_id="s")] == ["kept"]
    assert [m.content for m in current.get(session_id="s")] == ["new"]
    assert inspect(engine).get_indexes(legacy.sqldb_table_name) == before


def test_configured_storages_initialize_lazily_in_one_sqlite_database(tmp_path, monkeypatch):
    engine = create_engine("sqlite:///" + str(tmp_path / "public.db"))
    wrapper = SQLDBWrapper()
    wrapper._SQLDBWrapper__sql_database = SQLDatabase(engine)
    manager = SQLDBWrapperManager()
    monkeypatch.setattr(manager, "_instance_obj_map", {})
    manager.register("__default_instance__", wrapper)

    def configured(name):
        config = ComponentConfiger()
        config.sqldb_table_name = name
        config.sqldb_wrapper_name = "__default_instance__"
        return SqlAlchemyMemoryStorage().initialize_by_component_configer(config)

    try:
        first = configured("memory_a")
        second = configured("memory_b")
        first.add([Message(type="human", content="first")], session_id="same")
        second.add([Message(type="ai", content="second")], session_id="same")
        assert [m.content for m in first.get(session_id="same")] == ["first"]
        assert [m.content for m in second.get(session_id="same")] == ["second"]
        assert [m.content for m in configured("memory_a").get(session_id="same")] == ["first"]
    finally:
        engine.dispose()
