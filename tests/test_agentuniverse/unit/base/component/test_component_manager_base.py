from types import SimpleNamespace

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for agentuniverse.base.component.component_manager_base."""

import pytest

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


def test_unregister_removes_default_alias_for_same_component():
    manager = ComponentManagerBase(ComponentEnum.TOOL)
    component = SimpleNamespace(default_symbol=True)
    component_code = "test_app.tool.default_tool"
    manager.register(component_code, component)

    manager.unregister(component_code)

    assert manager.get_default_instance() is None
    assert manager.get_instance_name_list() == []


def test_unregister_non_default_component_preserves_default_alias():
    manager = ComponentManagerBase(ComponentEnum.TOOL)
    default_component = SimpleNamespace(default_symbol=True)
    other_component = SimpleNamespace(default_symbol=False)
    manager.register("test_app.tool.default_tool", default_component)
    manager.register("test_app.tool.other_tool", other_component)

    manager.unregister("test_app.tool.other_tool")

    assert manager.get_default_instance() is default_component
class _DummyComponent(ComponentBase):
    component_type: ComponentEnum = ComponentEnum.AGENT


class _DummyManager(ComponentManagerBase[_DummyComponent]):
    def __init__(self):
        super().__init__(ComponentEnum.AGENT)


@pytest.fixture
def manager():
    """Return an empty _DummyManager instance."""
    return _DummyManager()


class TestComponentManagerBase:
    """Tests for the base component manager registration logic."""

    def test_register_adds_instance(self, manager):
        instance = _DummyComponent()
        manager.register("mock_agent", instance)
        assert "mock_agent" in manager.get_instance_name_list()
        assert instance in manager.get_instance_obj_list()

    def test_register_duplicate_keeps_first_instance(self, manager):
        first = _DummyComponent()
        manager.register("mock_agent", first)
        manager.register("mock_agent", _DummyComponent())
        assert manager.get_instance_obj_list().count(first) == 1

    def test_register_default_symbol_sets_default_instance(self, manager):
        instance = _DummyComponent(default_symbol=True)
        manager.register("mock_agent", instance)
        assert "__default_instance__" in manager.get_instance_name_list()
        assert manager.get_default_instance() is instance

    def test_get_instance_obj_default_returns_same_object(self, manager):
        instance = _DummyComponent(default_symbol=True)
        manager.register("mock_agent", instance)
        assert manager.get_instance_obj("__default_instance__", new_instance=False) is instance

    def test_get_instance_obj_default_returns_copy(self, manager):
        instance = _DummyComponent(default_symbol=True)
        manager.register("mock_agent", instance)
        copy = manager.get_instance_obj("__default_instance__")
        assert copy is not instance
        assert copy == instance

    def test_unregister_removes_instance(self, manager):
        manager.register("mock_agent", _DummyComponent())
        manager.unregister("mock_agent")
        assert "mock_agent" not in manager.get_instance_name_list()

    def test_register_builtin_conflict_is_skipped(self, manager, monkeypatch):
        first = _DummyComponent()
        manager.register("mock_agent", first)
        monkeypatch.setattr(
            "agentuniverse.base.component.component_manager_base.is_system_builtin",
            lambda obj: True,
        )
        manager.register("mock_agent", _DummyComponent(default_symbol=True))
        assert manager._instance_obj_map["mock_agent"] is first
        assert "__default_instance__" not in manager.get_instance_name_list()
