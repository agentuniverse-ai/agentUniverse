# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_toolkit_manager.py

"""Unit tests for the singleton ToolkitManager registry."""

import pytest

from agentuniverse.agent.action.toolkit.toolkit import Toolkit
from agentuniverse.agent.action.toolkit.toolkit_manager import ToolkitManager
from agentuniverse.base.component.component_enum import ComponentEnum


@pytest.fixture
def manager():
    return ToolkitManager()


@pytest.fixture
def toolkit():
    return Toolkit(name="test_toolkit", description="toolkit docs",
                   include=["t1"])


@pytest.fixture(autouse=True)
def clean_manager(manager):
    """Restore the singleton registry after every test."""
    baseline = set(manager.get_instance_name_list())
    yield
    for name in list(manager.get_instance_name_list()):
        if name not in baseline:
            manager.unregister(name)


class TestToolkitManager:
    """Test ToolkitManager registry semantics."""

    def test_singleton_identity(self):
        assert ToolkitManager() is ToolkitManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.TOOLKIT

    def test_register_and_list(self, manager, toolkit):
        manager.register("tk1", toolkit)
        manager.register("tk2", Toolkit(name="other"))
        assert manager.get_instance_name_list() == ["tk1", "tk2"]
        assert manager.get_instance_obj_list()[-1].name == "other"

    def test_duplicate_register_keeps_first(self, manager, toolkit):
        manager.register("tk1", toolkit)
        manager.register("tk1", Toolkit(name="replacement"))
        assert manager.get_instance_name_list() == ["tk1"]
        assert manager.get_instance_obj_list()[0] is toolkit

    def test_unregister_removes_instance(self, manager, toolkit):
        manager.register("tk1", toolkit)
        manager.unregister("tk1")
        assert manager.get_instance_name_list() == []

    def test_default_symbol_registers_default_instance(self, manager):
        default = Toolkit(name="default_tk", default_symbol=True)
        manager.register("tk1", default)
        assert "__default_instance__" in manager.get_instance_name_list()
        assert manager.get_default_instance() is default

    def test_non_default_symbol_skips_default_instance(self, manager, toolkit):
        manager.register("tk1", toolkit)
        assert "__default_instance__" not in manager.get_instance_name_list()
        assert manager.get_default_instance() is None

    def test_get_instance_obj_list_returns_registered_objects(self, manager,
                                                              toolkit):
        manager.register("tk1", toolkit)
        assert manager.get_instance_obj_list() == [toolkit]
