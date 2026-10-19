# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_sqldb_wrapper_manager.py
"""Unit tests for the SQLDBWrapperManager component registry."""

from types import SimpleNamespace

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager


@pytest.fixture
def manager():
    """Return the singleton manager with an isolated instance map."""
    mgr = SQLDBWrapperManager()
    saved = dict(mgr._instance_obj_map)
    mgr._instance_obj_map.clear()
    yield mgr
    mgr._instance_obj_map.clear()
    mgr._instance_obj_map.update(saved)


def instance_code(mgr, appname, name):
    return f"{appname}.{mgr._component_type.value.lower()}.{name}"


def make_wrapper(name="db", default_symbol=False):
    return SimpleNamespace(default_symbol=default_symbol, name=name,
                           create_copy=lambda: "copied")


class TestSQLDBWrapperManager:
    """Test the SQLDBWrapper manager registry."""

    def test_singleton_returns_same_instance(self, manager):
        assert manager is SQLDBWrapperManager()

    def test_component_type_is_sqldb_wrapper(self, manager):
        assert manager._component_type == ComponentEnum.SQLDB_WRAPPER

    def test_register_and_get_existing_instance(self, manager):
        wrapper = make_wrapper()
        manager.register(instance_code(manager, "testapp", "db"), wrapper)
        got = manager.get_instance_obj("db", appname="testapp", new_instance=False)
        assert got is wrapper

    def test_get_with_new_instance_returns_copy(self, manager):
        wrapper = make_wrapper()
        manager.register(instance_code(manager, "testapp", "db"), wrapper)
        assert manager.get_instance_obj("db", appname="testapp",
                                        new_instance=True) == "copied"

    def test_default_instance_is_registered(self, manager):
        wrapper = make_wrapper(default_symbol=True)
        manager.register(instance_code(manager, "testapp", "db"), wrapper)
        assert manager.get_default_instance() is wrapper

    def test_unregister_removes_instance(self, manager):
        wrapper = make_wrapper()
        code = instance_code(manager, "testapp", "db")
        manager.register(code, wrapper)
        manager.unregister(code)
        assert code not in manager.get_instance_name_list()
