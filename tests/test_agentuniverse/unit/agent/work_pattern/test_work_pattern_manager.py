# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : btlqql
# @FileName: test_work_pattern_manager.py
"""Unit tests for the singleton WorkPatternManager."""

import pytest

from agentuniverse.agent.work_pattern.work_pattern import WorkPattern
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.base.component.component_enum import ComponentEnum


class EchoWorkPattern(WorkPattern):
    """A concrete WorkPattern implementation used by the manager tests."""

    def invoke(self, input_object, work_pattern_input: dict, **kwargs) -> dict:
        return work_pattern_input

    async def async_invoke(self, input_object, work_pattern_input: dict, **kwargs) -> dict:
        return work_pattern_input


class TestWorkPatternManager:
    """Test the singleton WorkPatternManager."""

    NAME_PREFIX = "test_wp_"

    @pytest.fixture
    def manager(self):
        """Yield the singleton manager, cleaning up names registered by the test."""
        manager = WorkPatternManager()
        initial_names = set(manager.get_instance_name_list())
        yield manager
        for name in list(manager.get_instance_name_list()):
            if name not in initial_names and name.startswith(self.NAME_PREFIX):
                manager.unregister(name)

    def test_singleton_identity(self):
        assert WorkPatternManager() is WorkPatternManager()

    def test_component_type_is_work_pattern(self, manager):
        assert manager._component_type == ComponentEnum.WORK_PATTERN

    def test_register_adds_instance_name(self, manager):
        manager.register("test_wp_echo", EchoWorkPattern())
        assert "test_wp_echo" in manager.get_instance_name_list()

    def test_duplicate_register_keeps_original(self, manager):
        original = EchoWorkPattern()
        manager.register("test_wp_dup", original)
        manager.register("test_wp_dup", EchoWorkPattern())
        assert manager.get_instance_name_list().count("test_wp_dup") == 1
        assert manager._instance_obj_map["test_wp_dup"] is original

    def test_unregister_removes_instance_name(self, manager):
        manager.register("test_wp_remove", EchoWorkPattern())
        manager.unregister("test_wp_remove")
        assert "test_wp_remove" not in manager.get_instance_name_list()

    def test_name_list_empty_after_unregister(self, manager):
        manager.register("test_wp_clean", EchoWorkPattern())
        manager.unregister("test_wp_clean")
        assert manager.get_instance_name_list() == []
