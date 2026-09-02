# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_workflow_output.py
"""Unit tests for WorkflowOutput."""

import pytest

from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_output import WorkflowOutput


class TestWorkflowOutput:
    def test_defaults(self):
        output = WorkflowOutput()
        assert output.workflow_id is None
        assert output.metadata == {}
        assert output.workflow_parameters == {}
        assert output.workflow_node_results == {}
        assert output.workflow_start_params == {}
        assert output.workflow_end_params == {}

    def test_workflow_id_assignment(self):
        output = WorkflowOutput(workflow_id='wf_1')
        assert output.workflow_id == 'wf_1'

    def test_workflow_start_and_end_params(self):
        output = WorkflowOutput(workflow_id='wf_2', workflow_start_params={'input': 'x'},
                                workflow_end_params={'result': 'y'})
        assert output.workflow_start_params == {'input': 'x'}
        assert output.workflow_end_params == {'result': 'y'}

    def test_store_node_results(self):
        output = WorkflowOutput()
        node_output = NodeOutput(node_id='n1', result='done')
        output.workflow_node_results['n1'] = node_output
        assert output.workflow_node_results['n1'].result == 'done'

    def test_model_dump_keys(self):
        output = WorkflowOutput(workflow_id='wf_3')
        data = output.model_dump()
        assert 'workflow_id' in data and 'workflow_node_results' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
