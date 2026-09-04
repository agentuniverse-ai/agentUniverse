# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_enum.py

"""Unit tests for workflow node enums."""

import pytest

from agentuniverse.workflow.node.enum import (
    ConditionComparisonEnum,
    NodeEnum,
    NodeStatusEnum,
)


class TestNodeEnum:
    """Test the NodeEnum members and helpers."""

    def test_member_values(self):
        assert NodeEnum.START.value == "start"
        assert NodeEnum.END.value == "end"
        assert NodeEnum.LLM.value == "llm"
        assert NodeEnum.TOOL.value == "tool"
        assert NodeEnum.KNOWLEDGE.value == "knowledge"
        assert NodeEnum.AGENT.value == "agent"
        assert NodeEnum.CONDITION.value == "ifelse"

    def test_to_value_list(self):
        assert NodeEnum.to_value_list() == [
            "start", "end", "llm", "tool", "knowledge", "agent", "ifelse"]

    def test_from_value(self):
        assert NodeEnum.from_value("start") is NodeEnum.START
        assert NodeEnum.from_value("ifelse") is NodeEnum.CONDITION

    def test_from_value_invalid_raises(self):
        with pytest.raises(ValueError, match="No enum member"):
            NodeEnum.from_value("unknown")


class TestStatusAndComparisonEnums:
    """Test the NodeStatusEnum and ConditionComparisonEnum members."""

    def test_node_status_values(self):
        assert NodeStatusEnum.RUNNING.value == "running"
        assert NodeStatusEnum.SUCCEEDED.value == "succeeded"
        assert NodeStatusEnum.FAILED.value == "failed"

    def test_comparison_values(self):
        assert ConditionComparisonEnum.EQUAL.value == "equal"
        assert ConditionComparisonEnum.NOT_EQUAL.value == "not_equal"
        assert ConditionComparisonEnum.BLANK.value == "blank"
