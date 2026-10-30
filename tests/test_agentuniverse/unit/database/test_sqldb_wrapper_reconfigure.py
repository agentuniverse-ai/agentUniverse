"""Reconfiguration must replace cached database handles, using real SQLite."""

import sqlite3
from unittest.mock import patch

import pytest
import yaml
from sqlalchemy import text

from agentuniverse.database.sqldb_wrapper import SQLDBWrapper, SQLDatabase
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.component_configer.configers.sqldb_wrapper_config import SQLDBWrapperConfiger


@pytest.fixture
def configuration(tmp_path):
    for name in ("first", "second"):
        with sqlite3.connect(tmp_path / f"{name}.db") as connection:
            connection.execute("CREATE TABLE marker (value TEXT)")
            connection.execute("INSERT INTO marker VALUES (?)", (name,))
            connection.execute("CREATE TABLE allowed_a (id INTEGER)")
            connection.execute("CREATE TABLE allowed_b (id INTEGER)")

    def load(database, **options):
        path = tmp_path / "wrapper.yaml"
        path.write_text(yaml.safe_dump({
            "name": "configured_db",
            "description": "test database",
            "db_uri": f"sqlite:///{tmp_path / (database + '.db')}",
            **options,
        }), encoding="utf-8")
        return SQLDBWrapperConfiger().load_by_configer(Configer().load_by_path(str(path)))

    return load


@pytest.fixture
def database_factory():
    factory = SQLDatabase.from_uri
    databases = []

    def create(*args, **kwargs):
        database = factory(*args, **kwargs)
        databases.append(database)
        return database

    with patch.object(SQLDatabase, "from_uri", side_effect=create) as recorded:
        yield recorded
    for database in databases:
        database._engine.dispose()


def test_reconfigured_queries_use_new_database(configuration, database_factory):
    wrapper = SQLDBWrapper().initialize_by_component_configer(configuration("first"))
    assert wrapper.run("SELECT value FROM marker") == [{"value": "first"}]
    wrapper.initialize_by_component_configer(configuration("second"))
    # Keep connection initialization lazy after changing configuration too.
    assert database_factory.call_count == 1
    assert wrapper.run("SELECT value FROM marker") == [{"value": "second"}]
    assert database_factory.call_count == 2


def test_reconfigured_sessions_use_new_bind_without_closing_existing_session(configuration, database_factory):
    wrapper = SQLDBWrapper().initialize_by_component_configer(configuration("first"))
    original_factory = wrapper.get_session()
    with original_factory() as original_session:
        assert original_session.execute(text("SELECT value FROM marker")).scalar_one() == "first"
        wrapper.initialize_by_component_configer(configuration("second"))
        replacement_factory = wrapper.get_session()
        with replacement_factory() as session:
            assert session.execute(text("SELECT value FROM marker")).scalar_one() == "second"
        assert original_session.execute(text("SELECT value FROM marker")).scalar_one() == "first"
    assert replacement_factory is not original_factory


def test_same_uri_applies_updated_schema_options(configuration, database_factory):
    wrapper = SQLDBWrapper().initialize_by_component_configer(
        configuration("first", sql_database_args={"include_tables": ["allowed_a"]}))
    assert set(wrapper.sql_database.get_usable_table_names()) == {"allowed_a"}
    wrapper.initialize_by_component_configer(
        configuration("first", sql_database_args={"include_tables": ["allowed_b"]}))
    assert set(wrapper.sql_database.get_usable_table_names()) == {"allowed_b"}


def test_cold_configuration_stays_lazy_and_caches_within_configuration(configuration, database_factory):
    wrapper = SQLDBWrapper().initialize_by_component_configer(configuration("first"))
    database_factory.assert_not_called()
    assert wrapper.run("SELECT value FROM marker") == [{"value": "first"}]
    assert wrapper.run("SELECT value FROM marker") == [{"value": "first"}]
    assert wrapper.get_session() is wrapper.get_session()
    assert database_factory.call_count == 1
