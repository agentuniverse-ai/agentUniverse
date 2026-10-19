# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/20 10:00
# @Author  : au_qa
# @FileName: test_planning_agent.py
"""Unit tests for the PlanningAgent default agent."""

import pytest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.default.planning_agent.planning_agent import \
    PlanningAgent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.planning_agent_template import \
    PlanningAgentTemplate
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum


class TestPlanningAgent:
    """Test cases for PlanningAgent."""

    @pytest.fixture
    def agent(self):
        """Return a fresh PlanningAgent instance."""
        return PlanningAgent()

    def test_instantiation_without_arguments(self, agent):
        """A freshly constructed agent has no agent_model configured."""
        assert agent.agent_model is None
        assert agent.component_type == ComponentEnum.AGENT
        assert agent.llm_name == ''
        assert agent.prompt_version is None

    def test_inheritance_chain(self):
        """PlanningAgent is a concrete PlanningAgentTemplate component."""
        assert issubclass(PlanningAgent, PlanningAgentTemplate)
        assert issubclass(PlanningAgent, AgentTemplate)
        assert issubclass(PlanningAgent, Agent)
        assert issubclass(PlanningAgent, ComponentBase)
        assert PlanningAgent.__abstractmethods__ == frozenset()

    def test_input_keys(self, agent):
        """The agent declares a single 'input' key."""
        assert agent.input_keys() == ['input']

    def test_output_keys(self, agent):
        """The agent declares framework and thought output keys."""
        assert agent.output_keys() == ['framework', 'thought']

    def test_parse_input_maps_input_and_framework(self, agent):
        """parse_input maps input and picks the planning framework."""
        agent_input = {}
        result = agent.parse_input(
            InputObject({'input': 'plan a trip',
                         'expert_framework': {'planning': 'split by day'}}),
            agent_input)
        assert result is agent_input
        assert result == {'input': 'plan a trip',
                          'expert_framework': 'split by day'}

    def test_parse_input_without_expert_framework(self, agent):
        """parse_input maps a missing expert_framework to None."""
        result = agent.parse_input(InputObject({'input': 'plan a trip'}), {})
        assert result == {'input': 'plan a trip', 'expert_framework': None}

    def test_parse_result_extracts_framework_and_thought(self, agent):
        """parse_result unpacks the framework JSON into the result dict."""
        result = agent.parse_result(
            {'output': '{"framework": ["step 1", "step 2"], '
                       '"thought": "the thought"}'})
        assert result == {'framework': ['step 1', 'step 2'],
                          'thought': 'the thought'}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
