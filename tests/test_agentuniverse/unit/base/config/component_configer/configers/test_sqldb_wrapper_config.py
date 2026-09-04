# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_sqldb_wrapper_config.py

"""Unit tests for the SQLDBWrapperConfiger."""

from types import SimpleNamespace

from agentuniverse.base.config.component_configer.configers.sqldb_wrapper_config import \
    SQLDBWrapperConfiger


class TestSQLDBWrapperConfiger:
    """Test sqldb wrapper configuration loading."""

    def test_defaults(self):
        configer = SQLDBWrapperConfiger()
        assert configer.name is None
        assert configer.db_uri is None
        assert configer.sql_database_args == {}
        assert configer.engine_args == {}
        assert configer.metadata_module == "agentuniverse.database.sqldb_wrapper"
        assert configer.metadata_class == "SQLDBWrapper"

    def test_load_by_configer(self):
        configer = SQLDBWrapperConfiger()
        value = {"name": "db1", "description": "main db",
                 "db_uri": "sqlite:///x.db",
                 "engine_args": {"echo": True},
                 "sql_database_args": {"pool_size": 5}}
        returned = configer.load_by_configer(SimpleNamespace(value=value,
                                                             path="x.yaml"))
        assert returned is configer
        assert configer.name == "db1"
        assert configer.db_uri == "sqlite:///x.db"
        assert configer.engine_args == {"echo": True}
        assert configer.sql_database_args == {"pool_size": 5}
        assert configer.metadata_module == "agentuniverse.database.sqldb_wrapper"
