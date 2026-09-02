# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 13:00
# @Author  : yuewang
# @FileName: test_llm_node.py
"""Unit tests for LLMNode."""

import pytest
from types import SimpleNamespace

from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.llm_node import LLMNode
from agentuniverse.workflow.workflow_output import WorkflowOutput


def _node(prompt='answer {{q}}'):
    return LLMNode(id='l1', data={
        'inputs': {
            'llm_param': [
                {'name': 'id', 'type': 'str', 'value': 'my_llm'},
                {'name': 'prompt', 'type': 'str', 'value': prompt}],
            'input_param': [
                {'name': 'q', 'type': 'str', 'value': {'type': 'literal', 'content': 'why'}}]},
        'outputs': [{'name': 'answer', 'type': 'str', 'value': ''}]})


def _fake_llm():
    captured = {}

    def call(messages=None, streaming=None):
        captured['messages'] = messages
        return LLMOutput(text='resp')

    return SimpleNamespace(set_by_agent_model=lambda **kw: captured.update(kw), call=call), captured


class TestLLMNode:
    """Test LLMNode run behavior."""

    def test_node_type(self):
        assert _node().type == NodeEnum.LLM

    def test_run_substitutes_variables(self, monkeypatch):
        llm, captured = _fake_llm()
        monkeypatch.setattr(LLMManager(), 'get_instance_obj', lambda name: llm)
        workflow_output = WorkflowOutput()
        out = _node().run(workflow_output)
        assert out.status == NodeStatusEnum.SUCCEEDED
        assert captured['messages'] == [{'role': 'user', 'content': 'answer why'}]
        assert out.result[0].value == 'resp'
        assert workflow_output.workflow_parameters['l1'][0].value == 'resp'

    def test_run_without_llm_raises(self, monkeypatch):
        monkeypatch.setattr(LLMManager(), 'get_instance_obj', lambda name: None)
        with pytest.raises(ValueError, match='No llm with id'):
            _node().run(WorkflowOutput())

    def test_run_missing_variable_raises(self, monkeypatch):
        llm, _ = _fake_llm()
        monkeypatch.setattr(LLMManager(), 'get_instance_obj', lambda name: llm)
        with pytest.raises(ValueError, match='not found in the input params'):
            _node(prompt='need {{missing}}').run(WorkflowOutput())
