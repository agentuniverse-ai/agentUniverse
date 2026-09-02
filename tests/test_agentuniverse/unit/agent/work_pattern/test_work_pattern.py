# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 11:15
# @Author  : yuewang
# @FileName: test_work_pattern.py
"""Unit tests for the WorkPattern base class."""

import asyncio

import pytest

from agentuniverse.agent.work_pattern.work_pattern import WorkPattern
from agentuniverse.base.component.component_enum import ComponentEnum


class EchoWorkPattern(WorkPattern):
    """Concrete WorkPattern used for testing."""

    def invoke(self, input_object, work_pattern_input, **kwargs):
        return {'result': 'sync'}

    async def async_invoke(self, input_object, work_pattern_input, **kwargs):
        return {'result': 'async'}


@pytest.fixture
def pattern():
    """Create an EchoWorkPattern instance."""
    return EchoWorkPattern()


class TestWorkPattern:
    """Test WorkPattern behavior."""

    def test_component_type(self, pattern):
        assert pattern.component_type == ComponentEnum.WORK_PATTERN

    def test_defaults(self, pattern):
        assert pattern.name is None
        assert pattern.description is None

    def test_base_is_abstract(self):
        with pytest.raises(TypeError):
            WorkPattern()

    def test_invoke_and_async_invoke(self, pattern):
        assert pattern.invoke(None, {}) == {'result': 'sync'}
        assert asyncio.run(pattern.async_invoke(None, {})) == {'result': 'async'}

    def test_initialize_by_component_configer(self):
        configer = type('C', (), {'name': 'wp1', 'description': 'dp1'})()
        pattern = EchoWorkPattern()
        assert pattern.initialize_by_component_configer(configer) is pattern
        assert pattern.name == 'wp1'
        assert pattern.description == 'dp1'

    def test_set_by_agent_model_is_noop(self, pattern):
        assert pattern.set_by_agent_model(anything='x') is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
