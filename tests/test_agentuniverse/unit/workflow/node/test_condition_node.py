# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_condition_node.py
"""Unit tests for ConditionNode."""

import pytest

from agentuniverse.workflow.node.condition_node import ConditionNode, ConditionNodeData
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.workflow_output import WorkflowOutput


def make_node(branch_name='yes', compare='equal', left=None, right=None):
    condition = {'compare': compare}
    if left is not None:
        condition['left'] = left
    if right is not None:
        condition['right'] = right
    return ConditionNode(
        id='cond_1',
        data={
            'inputs': {
                'branches': [{'name': branch_name, 'conditions': [condition]}]
            },
        },
    )


def literal(content):
    return {'name': 'v', 'value': {'type': 'literal', 'content': content}}


def reference(node_id, param_name):
    return {'name': 'v', 'value': {'type': 'reference', 'content': [node_id, param_name]}}


class TestConditionNode:
    def test_node_type(self):
        node = ConditionNode(id='cond_2')
        assert node.type == NodeEnum.CONDITION
        assert isinstance(node._data, ConditionNodeData)

    def test_equal_match_selects_branch(self):
        node = make_node(branch_name='match-branch', compare='equal',
                         left=literal('a'), right=literal('a'))
        output = node._run(WorkflowOutput())
        assert output.edge_source_handler == 'match-branch'
        assert output.status == NodeStatusEnum.SUCCEEDED

    def test_equal_mismatch_selects_default(self):
        node = make_node(branch_name='match-branch', compare='equal',
                         left=literal('a'), right=literal('b'))
        output = node._run(WorkflowOutput())
        assert output.edge_source_handler == 'branch-default'

    def test_not_equal_match(self):
        node = make_node(branch_name='diff', compare='not_equal',
                         left=literal('1'), right=literal('2'))
        assert node._run(WorkflowOutput()).edge_source_handler == 'diff'

    def test_blank_matches_none(self):
        node = make_node(branch_name='no-value', compare='blank',
                         left=literal(None))
        assert node._run(WorkflowOutput()).edge_source_handler == 'no-value'

    def test_reference_resolved_from_workflow_parameters(self):
        workflow_output = WorkflowOutput()
        from agentuniverse.workflow.node.node_config import NodeOutputParams
        workflow_output.workflow_parameters['upstream'] = [NodeOutputParams(name='score', value='7')]
        node = make_node(branch_name='big', compare='equal',
                         left=reference('upstream', 'score'), right=literal('7'))
        assert node._run(workflow_output).edge_source_handler == 'big'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
