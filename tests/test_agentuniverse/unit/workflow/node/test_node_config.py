# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 12:05
# @Author  : yuewang
# @FileName: test_node_config.py
"""Unit tests for the workflow node config models."""

import pytest
from pydantic import ValidationError

from agentuniverse.workflow.node.node_config import (
    AgentNodeInputParams,
    ConditionNodeInputParams,
    EndNodeInputParams,
    InputValueParams,
    LLMNodeInputParams,
    NodeInputParams,
    NodeOutputParams,
)


class TestBasicParams:
    """Test the flat param models."""

    def test_node_output_params_defaults(self):
        p = NodeOutputParams()
        assert p.name is None and p.type is None and p.value is None

    def test_node_input_params_nested_value(self):
        p = NodeInputParams(name='q', type='str',
                            value=InputValueParams(type='literal', content='hello'))
        assert p.value.content == 'hello'
        assert p.value.type == 'literal'


class TestNodeInputParamContainers:
    """Test the per-node-type input param containers."""

    def test_llm_node_input_params_defaults(self):
        p = LLMNodeInputParams()
        assert p.llm_param == []
        assert p.input_param == []

    def test_agent_node_input_params_accepts_dicts(self):
        p = AgentNodeInputParams(
            agent_param=[{'name': 'a1', 'type': 'agent', 'value': None}],
            input_param=[{'name': 'q', 'type': 'str',
                          'value': {'type': 'literal', 'content': 'hi'}}],
        )
        assert p.agent_param[0].name == 'a1'
        assert p.input_param[0].value.content == 'hi'

    def test_invalid_nested_type_raises(self):
        with pytest.raises(ValidationError):
            LLMNodeInputParams(llm_param='not-a-list')


class TestConditionAndEndParams:
    """Test condition and end node param models."""

    def test_condition_node_input_params(self):
        p = ConditionNodeInputParams(branches=[
            {'name': 'b1', 'conditions': [
                {'compare': '==',
                 'left': {'name': 'l', 'type': 'str'},
                 'right': {'name': 'r', 'type': 'str'}}]}])
        branch = p.branches[0]
        assert branch.name == 'b1'
        assert branch.conditions[0].compare == '=='
        assert branch.conditions[0].left.name == 'l'

    def test_end_node_input_params(self):
        p = EndNodeInputParams(
            prompt={'name': 'prompt', 'type': 'str', 'value': 'tpl'},
            input_param=[{'name': 'x', 'type': 'str'}])
        assert p.prompt.value == 'tpl'
        assert p.input_param[0].name == 'x'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
