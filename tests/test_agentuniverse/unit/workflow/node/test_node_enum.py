# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 12:55
# @Author  : yuewang
# @FileName: test_node_enum.py
"""Unit tests for the workflow node enums."""

import pytest

from agentuniverse.workflow.node.enum import (
    ConditionComparisonEnum,
    NodeEnum,
    NodeStatusEnum,
)


class TestNodeEnum:
    """Test NodeEnum members and lookups."""

    def test_members(self):
        assert set(m.name for m in NodeEnum) == {
            'START', 'END', 'LLM', 'TOOL', 'KNOWLEDGE', 'AGENT', 'CONDITION'
        }

    def test_to_value_list(self):
        assert NodeEnum.to_value_list() == [m.value for m in NodeEnum]
        assert 'ifelse' in NodeEnum.to_value_list()

    def test_from_value(self):
        assert NodeEnum.from_value('start') is NodeEnum.START
        assert NodeEnum.from_value('ifelse') is NodeEnum.CONDITION

    def test_from_value_invalid(self):
        with pytest.raises(ValueError, match='No enum member'):
            NodeEnum.from_value('nope')


class TestOtherEnums:
    """Test NodeStatusEnum and ConditionComparisonEnum."""

    def test_node_status_values(self):
        assert NodeStatusEnum.RUNNING.value == 'running'
        assert NodeStatusEnum.SUCCEEDED.value == 'succeeded'
        assert NodeStatusEnum.FAILED.value == 'failed'

    def test_condition_comparison_values(self):
        assert ConditionComparisonEnum.EQUAL.value == 'equal'
        assert ConditionComparisonEnum.NOT_EQUAL.value == 'not_equal'
        assert ConditionComparisonEnum.BLANK.value == 'blank'
