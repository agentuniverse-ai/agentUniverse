# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/06/30 10:30
# @Author  : agentuniverse
# @FileName: test_expressing_agent.py
"""Unit tests for the ExpressingAgent default agent module."""

import pytest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.default.expressing_agent.expressing_agent import ExpressingAgent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.expressing_agent_template import ExpressingAgentTemplate
from agentuniverse.base.component.component_enum import ComponentEnum


class TestExpressingAgent:
    """Test the ExpressingAgent default agent."""

    @pytest.fixture
    def agent(self):
        """Create an ExpressingAgent instance without any configuration."""
        return ExpressingAgent()

    def test_class_hierarchy(self):
        """ExpressingAgent should inherit from the expressing template chain."""
        assert issubclass(ExpressingAgent, ExpressingAgentTemplate)
        assert issubclass(ExpressingAgent, AgentTemplate)
        assert issubclass(ExpressingAgent, Agent)

    def test_instantiation(self, agent):
        """An ExpressingAgent can be created without a config and is an AGENT component."""
        assert isinstance(agent, ExpressingAgent)
        assert agent.component_type == ComponentEnum.AGENT
        assert agent.agent_model is None

    def test_input_keys(self, agent):
        """The expressing agent consumes input and executing_result."""
        assert agent.input_keys() == ['input', 'executing_result']

    def test_output_keys(self, agent):
        """The expressing agent only produces an output key."""
        assert agent.output_keys() == ['output']

    def test_build_execution_context(self, agent):
        """Execution context lists each question/answer pair."""
        input_object = InputObject({
            'executing_result': OutputObject({
                'executing_result': [
                    {'input': 'what is 2+2?', 'output': '4'},
                    {'input': 'capital of France?', 'output': 'Paris'},
                ]
            }),
        })
        context = agent.build_execution_context(input_object)
        assert context == (
            'question:what is 2+2?\nanswer:4\n\n'
            'question:capital of France?\nanswer:Paris'
        )

    def test_build_execution_context_empty(self, agent):
        """An empty executing result produces an empty context."""
        input_object = InputObject({
            'executing_result': OutputObject({'executing_result': []}),
        })
        assert agent.build_execution_context(input_object) == ''

    def test_parse_input(self, agent):
        """parse_input should carry input, background and expressing framework."""
        input_object = InputObject({
            'input': 'compose an answer',
            'executing_result': OutputObject({
                'executing_result': [{'input': 'q', 'output': 'a'}],
            }),
            'expert_framework': {'expressing': 'be concise'},
        })
        parsed = agent.parse_input(input_object, {'background': 'old'})
        assert parsed['input'] == 'compose an answer'
        assert parsed['background'] == 'question:q\nanswer:a'
        assert parsed['expert_framework'] == 'be concise'

    def test_parse_result(self, agent):
        """parse_result only keeps the produced output."""
        result = agent.parse_result({'output': 'final answer', 'extra': 1})
        assert result == {'output': 'final answer'}
