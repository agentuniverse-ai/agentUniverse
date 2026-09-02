# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_sqldb_wrapper.py
"""Unit tests for SQLDBWrapper delegation to the underlying sql database."""

from types import SimpleNamespace

import pytest

from agentuniverse.database.sqldb_wrapper import SQLDBWrapper


class FakeSQLDatabase:
    """Record calls without opening a real database connection."""

    def __init__(self):
        self.executed = []
        self.ran = []
        self._engine = "fake-engine"

    def _execute(self, command):
        self.executed.append(command)
        return [("result-row",)]

    def run(self, command, fetch="all"):
        self.ran.append((command, fetch))
        return "query-result-string"


@pytest.fixture
def wrapper():
    """A SQLDBWrapper with a fake underlying sql database injected."""
    db = FakeSQLDatabase()
    w = SQLDBWrapper()
    object.__setattr__(w, "_SQLDBWrapper__sql_database", db)
    return w, db


class TestSQLDBWrapper:
    """Test SQLDBWrapper behavior without a real database."""

    def test_run_delegates_to_sql_database(self, wrapper):
        w, db = wrapper
        assert w.run("select 1") == [("result-row",)]
        assert db.executed == ["select 1"]

    def test_run_with_str_return_returns_string(self, wrapper):
        w, db = wrapper
        assert w.run_with_str_return("select 1") == "query-result-string"
        assert db.ran == [("select 1", "all")]

    def test_sql_database_property_returns_injected_db(self, wrapper):
        w, db = wrapper
        assert w.sql_database is db

    def test_initialize_by_component_configer_sets_attributes(self):
        configer = SimpleNamespace(name="db1", description="test db")
        w = SQLDBWrapper()
        result = w.initialize_by_component_configer(configer)
        assert result is w
        assert w.name == "db1"
        assert w.description == "test db"
        assert w.db_wrapper_configer is configer

    def test_get_session_returns_cached_session(self, wrapper):
        w, _ = wrapper
        session = SimpleNamespace()
        w.db_session = session
        assert w.get_session() is session

    def test_component_type(self):
        from agentuniverse.base.component.component_enum import ComponentEnum
        assert SQLDBWrapper().component_type == ComponentEnum.SQLDB_WRAPPER
