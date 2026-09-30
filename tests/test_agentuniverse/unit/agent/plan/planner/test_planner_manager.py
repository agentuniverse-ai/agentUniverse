# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 11:25
# @Author  : yuewang
# @FileName: test_planner_manager.py
"""Unit tests for PlannerManager."""

import pytest

from agentuniverse.agent.plan.planner.planner_manager import PlannerManager
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum


class DummyPlanner(ComponentBase):
    """Minimal component object for registration tests."""
    component_type: ComponentEnum = ComponentEnum.PLANNER


@pytest.fixture
def manager():
    """Return the PlannerManager singleton."""
    return PlannerManager()


class TestPlannerManager:
    """Test PlannerManager registration behavior."""

    def test_singleton(self, manager):
        assert manager is PlannerManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.PLANNER

    def test_register_and_get(self, manager):
        planner = DummyPlanner()
        manager.register('app.planner.p1', planner)
        assert manager.get_instance_obj('p1', appname='app', new_instance=False) is planner

    def test_get_unknown_returns_none(self, manager):
        assert manager.get_instance_obj('absent_p_xyz', appname='app') is None

    def test_get_unknown_strict_raises(self, manager):
        with pytest.raises(ValueError, match='is not registered'):
            manager.get_instance_obj('absent_p_xyz', appname='app', strict=True)

    def test_unregister(self, manager):
        manager.register('app.planner.p2', DummyPlanner())
        manager.unregister('app.planner.p2')
        assert manager.get_instance_obj('p2', appname='app') is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
