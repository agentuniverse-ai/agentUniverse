# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 12:50
# @Author  : yuewang
# @FileName: test_end_node.py
"""Unit tests for EndNode."""

import pytest

from agentuniverse.workflow.node.end_node import EndNode
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.workflow_output import WorkflowOutput


def _node(prompt_value, input_param=None):
    return EndNode(id='e1', data={
        'inputs': {'prompt': {'name': 'p', 'type': 'str', 'value': prompt_value},
                   'input_param': input_param or []},
        'outputs': [{'name': 'answer', 'type': 'str', 'value': ''}]})


class TestEndNode:
    """Test EndNode template rendering behavior."""

    def test_node_type(self):
        assert _node('static').type == NodeEnum.END

    def test_static_prompt(self):
        out = _node('done').run(WorkflowOutput())
        assert out.status == NodeStatusEnum.SUCCEEDED
        assert out.result[0].value == 'done'

    def test_variable_substitution(self):
        workflow_output = WorkflowOutput()
        node = _node('Hello {{name}}', [
            {'name': 'name', 'type': 'str', 'value': {'type': 'literal', 'content': 'World'}}])
        out = node.run(workflow_output)
        assert out.result[0].value == 'Hello World'
        assert workflow_output.workflow_end_params == {'answer': 'Hello World'}

    def test_missing_variable_raises(self):
        with pytest.raises(ValueError, match='not found in the input params'):
            _node('Hi {{missing}}', [
                {'name': 'other', 'type': 'str', 'value': {'type': 'literal', 'content': 'x'}}]).run(WorkflowOutput())

    def test_dict_prompt_value(self):
        out = _node({'content': 'from dict'}).run(WorkflowOutput())
        assert out.result[0].value == 'from dict'
