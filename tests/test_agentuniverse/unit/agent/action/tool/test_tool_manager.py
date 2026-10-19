# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_tool_manager.py

"""Unit tests for the singleton ToolManager registry."""

import pytest

from agentuniverse.agent.action.tool.api_tool import APITool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum


@pytest.fixture
def manager():
    return ToolManager()


@pytest.fixture
def tool():
    return APITool(name="test_tool", description="tool docs")


@pytest.fixture(autouse=True)
def clean_manager(manager):
    """Restore the singleton registry after every test."""
    baseline = set(manager.get_instance_name_list())
    yield
    for name in list(manager.get_instance_name_list()):
        if name not in baseline:
            manager.unregister(name)


class TestToolManager:
    """Test ToolManager registry semantics."""

    def test_singleton_identity(self):
        assert ToolManager() is ToolManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.TOOL

    def test_register_and_list(self, manager, tool):
        manager.register("tool1", tool)
        manager.register("tool2", APITool(name="other"))
        assert manager.get_instance_name_list() == ["tool1", "tool2"]
        assert manager.get_instance_obj_list()[-1].name == "other"

    def test_duplicate_register_keeps_first(self, manager, tool):
        manager.register("tool1", tool)
        manager.register("tool1", APITool(name="replacement"))
        assert manager.get_instance_name_list() == ["tool1"]
        assert manager.get_instance_obj_list()[0] is tool

    def test_unregister_removes_instance(self, manager, tool):
        manager.register("tool1", tool)
        manager.unregister("tool1")
        assert manager.get_instance_name_list() == []

    def test_default_symbol_registers_default_instance(self, manager):
        default = APITool(name="default_tool", default_symbol=True)
        manager.register("tool1", default)
        assert "__default_instance__" in manager.get_instance_name_list()
        assert manager.get_default_instance() is default

    def test_non_default_symbol_skips_default_instance(self, manager, tool):
        manager.register("tool1", tool)
        assert "__default_instance__" not in manager.get_instance_name_list()
        assert manager.get_default_instance() is None

    def test_get_instance_obj_list_returns_registered_objects(self, manager,
                                                              tool):
        manager.register("tool1", tool)
        assert manager.get_instance_obj_list() == [tool]
