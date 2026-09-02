# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 13:30
# @Author  : yuewang
# @FileName: test_workflow_output.py
"""Unit tests for WorkflowOutput."""

from agentuniverse.workflow.node.enum import NodeStatusEnum
from agentuniverse.workflow.node.node_config import NodeOutputParams
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_output import WorkflowOutput


class TestWorkflowOutput:
    """Test WorkflowOutput defaults and typed fields."""

    def test_defaults(self):
        out = WorkflowOutput()
        assert out.workflow_id is None
        assert out.metadata == {}
        assert out.workflow_parameters == {}
        assert out.workflow_node_results == {}
        assert out.workflow_start_params == {}
        assert out.workflow_end_params == {}

    def test_explicit_fields(self):
        out = WorkflowOutput(workflow_id='wf-1', metadata={'k': 1},
                             workflow_start_params={'input': 'hi'})
        assert out.workflow_id == 'wf-1'
        assert out.metadata == {'k': 1}
        assert out.workflow_start_params == {'input': 'hi'}

    def test_workflow_parameters_typed_as_output_params(self):
        out = WorkflowOutput(workflow_parameters={
            'n1': [{'name': 'a', 'value': 1}]})
        params = out.workflow_parameters['n1']
        assert isinstance(params[0], NodeOutputParams)
        assert params[0].value == 1

    def test_workflow_node_results_typed(self):
        node_output = NodeOutput(node_id='n1', status=NodeStatusEnum.SUCCEEDED)
        out = WorkflowOutput(workflow_node_results={'n1': node_output})
        assert out.workflow_node_results['n1'] is node_output
