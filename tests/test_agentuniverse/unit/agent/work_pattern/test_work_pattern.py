# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : btlqql
# @FileName: test_work_pattern.py
"""Unit tests for the abstract WorkPattern component."""

import asyncio
import types

import pytest

from agentuniverse.agent.work_pattern.work_pattern import WorkPattern
from agentuniverse.base.component.component_enum import ComponentEnum


class EchoWorkPattern(WorkPattern):
    """A concrete WorkPattern implementation used to drive the abstract API."""

    def invoke(self, input_object, work_pattern_input: dict, **kwargs) -> dict:
        return work_pattern_input

    async def async_invoke(self, input_object, work_pattern_input: dict, **kwargs) -> dict:
        return work_pattern_input


class TestWorkPattern:
    """Test the WorkPattern component."""

    @pytest.fixture
    def work_pattern(self):
        """Create a concrete WorkPattern instance for testing."""
        return EchoWorkPattern()

    def test_component_type_is_work_pattern(self, work_pattern):
        assert work_pattern.component_type == ComponentEnum.WORK_PATTERN

    def test_default_name_and_description(self, work_pattern):
        assert work_pattern.name is None
        assert work_pattern.description is None

    def test_initialize_by_component_configer(self, work_pattern):
        configer = types.SimpleNamespace(name="echo_pattern", description="an echo work pattern")
        returned = work_pattern.initialize_by_component_configer(configer)
        assert returned is work_pattern
        assert work_pattern.name == "echo_pattern"
        assert work_pattern.description == "an echo work pattern"

    def test_set_by_agent_model_is_a_noop(self, work_pattern):
        assert work_pattern.set_by_agent_model(name="x", description="y") is None

    def test_invoke_passes_through_input(self, work_pattern):
        work_pattern_input = {"query": "hello"}
        result = work_pattern.invoke({"raw": "input"}, work_pattern_input)
        assert result == work_pattern_input

    def test_async_invoke_passes_through_input(self, work_pattern):
        work_pattern_input = {"query": "world"}
        result = asyncio.run(work_pattern.async_invoke({"raw": "input"}, work_pattern_input))
        assert result == work_pattern_input
