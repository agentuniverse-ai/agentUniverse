# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/05 10:05
# @Author  : kaichuan
# @FileName: test_component_enum.py
"""Unit tests for ComponentEnum in base.component.component_enum."""

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum


class TestComponentEnum:
    """Test ComponentEnum members and helper methods."""

    def test_known_member_values(self):
        """Core members map to their upper-cased string values."""
        assert ComponentEnum.AGENT.value == "AGENT"
        assert ComponentEnum.LLM.value == "LLM"
        assert ComponentEnum.TOOLKIT.value == "TOOLKIT"
        assert ComponentEnum.WORKFLOW.value == "WORKFLOW"
        assert ComponentEnum.LOG_SINK.value == "LOG_SINK"

    def test_member_values_match_names(self):
        """Every member's value equals its member name."""
        for member in ComponentEnum:
            assert member.value == member.name

    def test_to_value_list_contents(self):
        """to_value_list returns each value exactly once."""
        values = ComponentEnum.to_value_list()
        assert isinstance(values, list)
        assert len(values) == len(ComponentEnum)
        assert len(set(values)) == len(values)
        assert "KNOWLEDGE" in values
        assert "MEMORY_STORAGE" in values

    def test_from_value_roundtrip(self):
        """from_value returns the member for every valid value."""
        for member in ComponentEnum:
            assert ComponentEnum.from_value(member.value) is member

    def test_from_value_invalid_raises(self):
        """from_value raises ValueError for an unknown value."""
        with pytest.raises(ValueError, match="No enum member with value NOPE"):
            ComponentEnum.from_value("NOPE")

    def test_from_value_empty_string_raises(self):
        """An empty string is not a valid component value."""
        with pytest.raises(ValueError, match="No enum member with value"):
            ComponentEnum.from_value("")
