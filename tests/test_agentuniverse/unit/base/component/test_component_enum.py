# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the ComponentEnum enumeration."""

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum


class TestComponentEnum:
    """Tests for the ComponentEnum enumeration."""

    def test_members_have_expected_values(self):
        assert ComponentEnum.AGENT.value == "AGENT"
        assert ComponentEnum.KNOWLEDGE.value == "KNOWLEDGE"
        assert ComponentEnum.LLM.value == "LLM"
        assert ComponentEnum.TOOL.value == "TOOL"
        assert ComponentEnum.WORKFLOW.value == "WORKFLOW"
        assert ComponentEnum.LOG_SINK.value == "LOG_SINK"

    def test_to_value_list_contains_all_members(self):
        values = ComponentEnum.to_value_list()
        assert len(values) == len(list(ComponentEnum))
        assert set(values) == {member.value for member in ComponentEnum}
        assert "AGENT" in values
        assert "DEFAULT" in values

    def test_from_value_returns_matching_member(self):
        assert ComponentEnum.from_value("AGENT") is ComponentEnum.AGENT
        assert ComponentEnum.from_value("PLANNER") is ComponentEnum.PLANNER
        assert ComponentEnum.from_value("PROMPT") is ComponentEnum.PROMPT

    def test_from_value_unknown_value_raises(self):
        with pytest.raises(ValueError):
            ComponentEnum.from_value("UNKNOWN_COMPONENT")

    def test_member_iteration_order(self):
        members = [member.value for member in ComponentEnum]
        assert members[0] == "AGENT"
        assert members[-1] == "CONTEXT_ROUTER"

    def test_enum_members_are_distinct(self):
        assert len({member.value for member in ComponentEnum}) == len(list(ComponentEnum))
