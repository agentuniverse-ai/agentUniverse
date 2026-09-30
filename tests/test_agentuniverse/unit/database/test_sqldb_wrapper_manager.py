# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/15 13:00
# @Author  : Yue Wang
# @FileName: test_sqldb_wrapper_manager.py
"""Unit tests for SQLDBWrapperManager."""

from unittest.mock import patch

import pytest

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager


class _DummyWrapper(ComponentBase):
    """A minimal component usable as a registered SQLDBWrapper."""

    component_type: ComponentEnum = ComponentEnum.SQLDB_WRAPPER
    name: str = "dummy"


@pytest.fixture
def manager():
    """Get the singleton manager and reset its registry."""
    mgr = SQLDBWrapperManager()
    mgr._instance_obj_map.clear()
    return mgr


class TestSQLDBWrapperManager:
    """Test SQLDBWrapperManager registry behavior."""

    def test_singleton_identity(self):
        """Calling the manager always returns the same instance."""
        assert SQLDBWrapperManager() is SQLDBWrapperManager()

    def test_component_type(self, manager):
        """The manager is bound to the SQLDB_WRAPPER component type."""
        assert manager._component_type is ComponentEnum.SQLDB_WRAPPER

    def test_register_and_list_names(self, manager):
        """Registered names appear in get_instance_name_list."""
        manager.register("my_db", _DummyWrapper(name="my_db"))
        assert manager.get_instance_name_list() == ["my_db"]

    def test_register_duplicate_keeps_first(self, manager):
        """Re-registering the same name keeps the originally stored instance."""
        first, second = _DummyWrapper(name="db"), _DummyWrapper(name="db")
        manager.register("db", first)
        manager.register("db", second)
        assert manager.get_instance_obj_list() == [first]

    def test_default_instance_registration(self, manager):
        """A default_symbol instance is exposed via get_default_instance."""
        default = _DummyWrapper(name="default_db", default_symbol=True)
        manager.register("default_db", default)
        assert manager.get_default_instance() is default
        copy = manager.get_default_instance(new_instance=True)
        assert copy is not default
        assert copy.name == "default_db"

    def test_get_instance_obj_returns_copy(self, manager):
        """get_instance_obj resolves by instance code and returns a copy."""
        wrapper = _DummyWrapper(name="my_db")
        manager.register("test_app.sqldb_wrapper.my_db", wrapper)
        with patch("agentuniverse.base.component.component_manager_base."
                   "ApplicationConfigManager") as mock_app:
            mock_app.return_value.app_configer.base_info_appname = "test_app"
            result = manager.get_instance_obj("my_db")
        assert result is not wrapper
        assert result.name == "my_db"

    def test_get_instance_obj_missing_returns_none(self, manager):
        """A missing component returns None without strict mode."""
        with patch("agentuniverse.base.component.component_manager_base."
                   "ApplicationConfigManager") as mock_app:
            mock_app.return_value.app_configer.base_info_appname = "test_app"
            assert manager.get_instance_obj("nope") is None

    def test_unregister(self, manager):
        """unregister removes the component from the registry."""
        manager.register("db", _DummyWrapper(name="db"))
        manager.unregister("db")
        assert manager.get_instance_name_list() == []
