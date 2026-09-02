# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : btlqql
# @FileName: test_planner_manager.py
"""Unit tests for the singleton PlannerManager."""

import pytest

from agentuniverse.agent.plan.planner.planner_manager import PlannerManager
from agentuniverse.base.component.component_enum import ComponentEnum


class FakePlanner:
    """Minimal planner stand-in exposing the attributes the manager touches."""

    def __init__(self):
        self.default_symbol = False
        self.component_type = ComponentEnum.PLANNER
        self.component_config_path = None


class TestPlannerManager:
    """Test the singleton PlannerManager."""

    NAME_PREFIX = "test_planner_"

    @pytest.fixture
    def manager(self):
        """Yield the singleton manager, cleaning up names registered by the test."""
        manager = PlannerManager()
        initial_names = set(manager.get_instance_name_list())
        yield manager
        for name in list(manager.get_instance_name_list()):
            if name not in initial_names and name.startswith(self.NAME_PREFIX):
                manager.unregister(name)

    def test_singleton_identity(self):
        assert PlannerManager() is PlannerManager()

    def test_component_type_is_planner(self, manager):
        assert manager._component_type == ComponentEnum.PLANNER

    def test_register_adds_instance_name(self, manager):
        manager.register("test_planner_one", FakePlanner())
        assert "test_planner_one" in manager.get_instance_name_list()

    def test_duplicate_register_keeps_first(self, manager):
        first = FakePlanner()
        manager.register("test_planner_dup", first)
        manager.register("test_planner_dup", FakePlanner())
        assert manager.get_instance_name_list().count("test_planner_dup") == 1
        assert manager._instance_obj_map["test_planner_dup"] is first

    def test_unregister_removes_instance_name(self, manager):
        manager.register("test_planner_remove", FakePlanner())
        manager.unregister("test_planner_remove")
        assert "test_planner_remove" not in manager.get_instance_name_list()

    def test_name_list_empty_after_unregister(self, manager):
        manager.register("test_planner_clean", FakePlanner())
        manager.unregister("test_planner_clean")
        assert manager.get_instance_name_list() == []
