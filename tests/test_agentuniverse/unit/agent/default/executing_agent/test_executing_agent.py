# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/06/30 10:40
# @Author  : agentuniverse
# @FileName: test_executing_agent.py
"""Unit tests for the ExecutingAgent default agent module."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.default.executing_agent.executing_agent import ExecutingAgent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.executing_agent_template import ExecutingAgentTemplate
from agentuniverse.base.component.component_enum import ComponentEnum


class TestExecutingAgent:
    """Test the ExecutingAgent default agent."""

    @pytest.fixture
    def agent(self):
        """Create an ExecutingAgent instance without any configuration."""
        return ExecutingAgent()

    def test_class_hierarchy(self):
        """ExecutingAgent should inherit from the executing template chain."""
        assert issubclass(ExecutingAgent, ExecutingAgentTemplate)
        assert issubclass(ExecutingAgent, AgentTemplate)
        assert issubclass(ExecutingAgent, Agent)

    def test_instantiation(self, agent):
        """An ExecutingAgent can be created without a config and is an AGENT component."""
        assert isinstance(agent, ExecutingAgent)
        assert agent.component_type == ComponentEnum.AGENT
        assert agent.agent_model is None
        assert agent._context_values == {}

    def test_input_keys(self, agent):
        """The executing agent consumes input and planning_result."""
        assert agent.input_keys() == ['input', 'planning_result']

    def test_output_keys(self, agent):
        """The executing agent produces an executing_result key."""
        assert agent.output_keys() == ['executing_result']

    def test_parse_input_framework(self, agent):
        """parse_input should collect the framework planned by the planning agent."""
        input_object = InputObject({
            'input': 'solve it',
            'planning_result': OutputObject({'framework': ['sub task 1', 'sub task 2']}),
            'expert_framework': {'executing': 'step by step'},
        })
        parsed = agent.parse_input(input_object, {'existing': True})
        assert parsed['existing'] is True
        assert parsed['input'] == 'solve it'
        assert parsed['framework'] == ['sub task 1', 'sub task 2']
        assert parsed['expert_framework'] == 'step by step'

    def test_parse_input_empty_framework(self, agent):
        """parse_input tolerates an empty planning framework."""
        input_object = InputObject({
            'input': 'solve it',
            'planning_result': OutputObject({'framework': []}),
        })
        parsed = agent.parse_input(input_object, {})
        assert parsed['framework'] == []

    def test_parse_result_removes_output_stream(self, agent):
        """parse_result drops the transient output_stream but keeps the results."""
        agent.agent_model = SimpleNamespace(info={'name': 'executing_agent'})
        result = agent.parse_result({
            'executing_result': [{'input': 'Q1: a', 'output': 'A1: b'}],
            'output_stream': None,
        })
        assert 'output_stream' not in result
        assert result['executing_result'] == [{'input': 'Q1: a', 'output': 'A1: b'}]

    def test_validate_required_params(self, agent):
        """validate_required_params fails without an llm_name and passes with one."""
        agent.agent_model = SimpleNamespace(info={'name': 'executing_agent'})
        with pytest.raises(ValueError, match='llm_name of the agent'):
            agent.validate_required_params()
        agent.llm_name = 'gpt-4o'
        assert agent.validate_required_params() is None
