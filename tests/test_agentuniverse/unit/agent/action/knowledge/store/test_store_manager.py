# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_store_manager.py

"""Unit tests for the singleton StoreManager registry."""

import pytest

from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent.action.knowledge.store.store_manager \
    import StoreManager
from agentuniverse.base.component.component_enum import ComponentEnum


@pytest.fixture
def manager():
    return StoreManager()


@pytest.fixture
def store():
    return Store(name="test_store", description="store docs")


@pytest.fixture(autouse=True)
def clean_manager(manager):
    """Restore the singleton registry after every test."""
    baseline = set(manager.get_instance_name_list())
    yield
    for name in list(manager.get_instance_name_list()):
        if name not in baseline:
            manager.unregister(name)


class TestStoreManager:
    """Test StoreManager registry semantics."""

    def test_singleton_identity(self):
        assert StoreManager() is StoreManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.STORE

    def test_register_and_list(self, manager, store):
        manager.register("s1", store)
        manager.register("s2", Store(name="other"))
        assert manager.get_instance_name_list() == ["s1", "s2"]
        assert manager.get_instance_obj_list()[-1].name == "other"

    def test_duplicate_register_keeps_first(self, manager, store):
        manager.register("s1", store)
        manager.register("s1", Store(name="replacement"))
        assert manager.get_instance_name_list() == ["s1"]
        assert manager.get_instance_obj_list()[0] is store

    def test_unregister_removes_instance(self, manager, store):
        manager.register("s1", store)
        manager.unregister("s1")
        assert manager.get_instance_name_list() == []

    def test_default_symbol_registers_default_instance(self, manager):
        default = Store(name="default_store", default_symbol=True)
        manager.register("s1", default)
        assert "__default_instance__" in manager.get_instance_name_list()
        assert manager.get_default_instance() is default

    def test_non_default_symbol_skips_default_instance(self, manager, store):
        manager.register("s1", store)
        assert "__default_instance__" not in manager.get_instance_name_list()
        assert manager.get_default_instance() is None

    def test_get_instance_obj_list_returns_registered_objects(self, manager,
                                                              store):
        manager.register("s1", store)
        assert manager.get_instance_obj_list() == [store]
