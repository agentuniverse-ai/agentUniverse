# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 13:20
# @Author  : yuewang
# @FileName: test_tool_node.py
"""Unit tests for ToolNode."""

import pytest
from types import SimpleNamespace

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.tool_node import ToolNode
from agentuniverse.workflow.workflow_output import WorkflowOutput


def _node(outputs=None):
    return ToolNode(id='t1', data={
        'inputs': {
            'tool_param': [
                {'name': 'id', 'type': 'str', 'value': 'my_tool'},
                {'name': 'name', 'type': 'str', 'value': 'search'}],
            'input_param': [
                {'name': 'q', 'type': 'str', 'value': {'type': 'literal', 'content': 'hi'}}]},
        'outputs': outputs or [{'name': 'result', 'type': 'str', 'value': ''}]})


class TestToolNode:
    """Test ToolNode run behavior."""

    def test_node_type(self):
        assert _node().type == NodeEnum.TOOL

    def test_missing_tool_raises(self, monkeypatch):
        monkeypatch.setattr(ToolManager(), 'get_instance_obj', lambda name: None)
        with pytest.raises(ValueError, match='No tool with id'):
            _node().run(WorkflowOutput())

    def test_string_output(self, monkeypatch):
        tool = SimpleNamespace(run=lambda **kw: 'tool-says-hi')
        monkeypatch.setattr(ToolManager(), 'get_instance_obj', lambda name: tool)
        workflow_output = WorkflowOutput()
        out = _node().run(workflow_output)
        assert out.status == NodeStatusEnum.SUCCEEDED
        assert out.result[0].value == 'tool-says-hi'
        assert workflow_output.workflow_parameters['t1'][0].value == 'tool-says-hi'

    def test_dict_output_mapped_by_name(self, monkeypatch):
        tool = SimpleNamespace(run=lambda **kw: {'answer': 'A', 'score': 9})
        monkeypatch.setattr(ToolManager(), 'get_instance_obj', lambda name: tool)
        node = _node([{'name': 'answer', 'type': 'str', 'value': ''},
                      {'name': 'score', 'type': 'str', 'value': ''}])
        out = node.run(WorkflowOutput())
        assert [p.value for p in out.result] == ['A', 9]

    def test_unsupported_output_type_raises(self, monkeypatch):
        tool = SimpleNamespace(run=lambda **kw: 42)
        monkeypatch.setattr(ToolManager(), 'get_instance_obj', lambda name: tool)
        with pytest.raises(TypeError, match='not supported'):
            _node().run(WorkflowOutput())
