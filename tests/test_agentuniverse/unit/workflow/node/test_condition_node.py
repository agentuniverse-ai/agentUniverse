# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 12:45
# @Author  : yuewang
# @FileName: test_condition_node.py
"""Unit tests for ConditionNode."""

import pytest

from agentuniverse.workflow.node.condition_node import ConditionNode
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.workflow_output import WorkflowOutput


def _node(compare, left, right=None):
    return ConditionNode(id='c1', data={
        'inputs': {'branches': [{'name': 'match-branch', 'conditions': [
            {'compare': compare, 'left': left, 'right': right}]}]}})


def _literal(content):
    return {'name': 'v', 'type': 'str', 'value': {'type': 'literal', 'content': content}}


class TestConditionNode:
    """Test ConditionNode evaluation behavior."""

    def test_node_type(self):
        assert _node('equal', _literal('a')).type == NodeEnum.CONDITION

    def test_equal_true_uses_branch_name(self):
        out = _node('equal', _literal('a'), _literal('a')).run(WorkflowOutput())
        assert out.status == NodeStatusEnum.SUCCEEDED
        assert out.edge_source_handler == 'match-branch'
        assert out.node_id == 'c1'

    def test_equal_false_falls_back_to_default(self):
        out = _node('equal', _literal('a'), _literal('b')).run(WorkflowOutput())
        assert out.edge_source_handler == 'branch-default'

    def test_not_equal(self):
        assert _node('not_equal', _literal('a'), _literal('b')).run(WorkflowOutput()).edge_source_handler == 'match-branch'
        assert _node('not_equal', _literal('a'), _literal('a')).run(WorkflowOutput()).edge_source_handler == 'branch-default'

    def test_blank_check(self):
        assert _node('blank', _literal(None), None).run(WorkflowOutput()).edge_source_handler == 'match-branch'
        assert _node('blank', _literal('x'), None).run(WorkflowOutput()).edge_source_handler == 'branch-default'

    def test_reference_resolution(self):
        node = ConditionNode(id='c1', data={'inputs': {'branches': [{'name': 'ref-branch', 'conditions': [
            {'compare': 'equal',
             'left': {'name': 'l', 'type': 'str',
                      'value': {'type': 'reference', 'content': ['n1', 'score']}},
             'right': _literal('90')}] }]}})
        workflow_output = WorkflowOutput()
        from agentuniverse.workflow.node.node_config import NodeOutputParams
        workflow_output.workflow_parameters['n1'] = [NodeOutputParams(name='score', value='90')]
        assert node.run(workflow_output).edge_source_handler == 'ref-branch'
