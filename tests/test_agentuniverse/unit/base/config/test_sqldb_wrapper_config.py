# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/05 10:15
# @Author  : kaichuan
# @FileName: test_sqldb_wrapper_config.py
"""Unit tests for SQLDBWrapperConfiger in base.config.component_configer.configers."""

import pytest
from agentuniverse.base.config.component_configer.configers.sqldb_wrapper_config import (
    SQLDBWrapperConfiger,
)
from agentuniverse.base.config.configer import Configer


def _configer_with(value):
    """Build a Configer whose value is the given dict."""
    configer = Configer()
    configer.value = value
    return configer

DB_CONFIG = {
    "name": "demo_db",
    "description": "demo database",
    "metadata": {"type": "SQLDB_WRAPPER", "module": "pkg.db", "class": "DemoDB"},
    "db_uri": "sqlite-memory",
    "engine_args": {"echo": True},
    "sql_database_args": {"pool_size": 5},
}


class TestSQLDBWrapperConfiger:
    """Test SQLDBWrapperConfiger defaults and configuration loading."""

    def test_default_metadata_points_to_sqldb_wrapper(self):
        """A fresh instance defaults to the built-in SQLDBWrapper metadata."""
        configer = SQLDBWrapperConfiger()
        assert configer.metadata_module == "agentuniverse.database.sqldb_wrapper"
        assert configer.metadata_class == "SQLDBWrapper"

    def test_initial_section_defaults(self):
        """Constructor initializes empty sections and empty args dicts."""
        configer = SQLDBWrapperConfiger()
        assert configer.name is None
        assert configer.description is None
        assert configer.db_uri is None
        assert configer.engine_args == {}
        assert configer.sql_database_args == {}

    def test_load_returns_same_instance(self):
        """load() is a fluent operation returning the same object."""
        configer = SQLDBWrapperConfiger(_configer_with(DB_CONFIG))
        assert configer.load() is configer

    def test_load_populates_fields(self):
        """All configured fields are available after load()."""
        configer = SQLDBWrapperConfiger(_configer_with(DB_CONFIG)).load()
        assert configer.name == "demo_db"
        assert configer.description == "demo database"
        assert configer.db_uri == "sqlite-memory"
        assert configer.engine_args == {"echo": True}
        assert configer.sql_database_args == {"pool_size": 5}
        assert configer.metadata_module == "pkg.db"
        assert configer.metadata_class == "DemoDB"

    def test_load_missing_optional_fields(self):
        """Missing optional fields fall back to None or empty dicts."""
        configer = SQLDBWrapperConfiger(_configer_with({"name": "only-name"})).load()
        assert configer.name == "only-name"
        assert configer.description is None
        assert configer.db_uri is None
        assert configer.engine_args == {}
        assert configer.sql_database_args == {}

    def test_args_are_copies_not_shared(self):
        """Loaded arg dicts are copies of the config value."""
        configer = SQLDBWrapperConfiger(_configer_with(DB_CONFIG)).load()
        DB_CONFIG["engine_args"]["extra"] = "shared"
        assert "extra" not in configer.engine_args
        configer.sql_database_args["mine"] = 1
        assert "mine" not in DB_CONFIG["sql_database_args"]

    def test_load_by_configer_replaces_configer(self):
        """load_by_configer binds the passed Configer to the instance."""
        configer = SQLDBWrapperConfiger()
        other = _configer_with(DB_CONFIG)
        result = configer.load_by_configer(other)
        assert result is configer
        assert configer.configer is other
        assert configer.name == "demo_db"
