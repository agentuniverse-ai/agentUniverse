# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 13:15
# @Author  : yuewang
# @FileName: test_start_node.py
"""Unit tests for StartNode."""

from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.start_node import StartNode
from agentuniverse.workflow.workflow_output import WorkflowOutput


class TestStartNode:
    """Test StartNode run behavior."""

    def test_node_type(self):
        assert StartNode(id='s1', data={}).type == NodeEnum.START

    def test_run_publishes_start_params(self):
        node = StartNode(id='s1', data={
            'outputs': [{'name': 'input', 'type': 'str', 'value': ''}]})
        workflow_output = WorkflowOutput()
        workflow_output.workflow_start_params = {'input': 'hi'}
        out = node.run(workflow_output)
        assert out.status == NodeStatusEnum.SUCCEEDED
        assert out.result[0].value == 'hi'
        assert workflow_output.workflow_parameters['s1'][0].value == 'hi'

    def test_run_without_params_uses_empty(self):
        node = StartNode(id='s2', data={
            'outputs': [{'name': 'input', 'type': 'str', 'value': ''}]})
        out = node.run(WorkflowOutput())
        assert out.result[0].value == ''

    def test_run_output_carries_node_id(self):
        node = StartNode(id='s3', data={
            'outputs': [{'name': 'input', 'type': 'str', 'value': ''}]})
        out = node.run(WorkflowOutput())
        assert out.node_id == 's3'

    def test_multiple_outputs_only_first_filled(self):
        node = StartNode(id='s4', data={
            'outputs': [{'name': 'input', 'type': 'str', 'value': ''},
                        {'name': 'extra', 'type': 'str', 'value': ''}]})
        workflow_output = WorkflowOutput()
        workflow_output.workflow_start_params = {'input': 'v'}
        node.run(workflow_output)
        assert [p.value for p in workflow_output.workflow_parameters['s4']] == ['v', '']
