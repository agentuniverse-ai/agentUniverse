# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 11:20
# @Author  : yuewang
# @FileName: test_work_pattern_manager.py
"""Unit tests for WorkPatternManager."""

import pytest

from agentuniverse.agent.work_pattern.work_pattern import WorkPattern
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.base.component.component_enum import ComponentEnum


class DummyWorkPattern(WorkPattern):
    """Minimal concrete WorkPattern for registration tests."""

    def invoke(self, input_object, work_pattern_input, **kwargs):
        return {}

    async def async_invoke(self, input_object, work_pattern_input, **kwargs):
        return {}


@pytest.fixture
def manager():
    """Return the WorkPatternManager singleton."""
    return WorkPatternManager()


class TestWorkPatternManager:
    """Test WorkPatternManager registration behavior."""

    def test_singleton(self, manager):
        assert manager is WorkPatternManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.WORK_PATTERN

    def test_register_and_get(self, manager):
        pattern = DummyWorkPattern()
        manager.register('app.work_pattern.wp1', pattern)
        assert manager.get_instance_obj('wp1', appname='app', new_instance=False) is pattern

    def test_get_unknown_returns_none(self, manager):
        assert manager.get_instance_obj('absent_wp_xyz', appname='app') is None

    def test_get_unknown_strict_raises(self, manager):
        with pytest.raises(ValueError, match='is not registered'):
            manager.get_instance_obj('absent_wp_xyz', appname='app', strict=True)

    def test_unregister(self, manager):
        manager.register('app.work_pattern.wp2', DummyWorkPattern())
        manager.unregister('app.work_pattern.wp2')
        assert manager.get_instance_obj('wp2', appname='app') is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
