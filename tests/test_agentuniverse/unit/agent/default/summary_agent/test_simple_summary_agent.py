# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/20 10:00
# @Author  : au_qa
# @FileName: test_simple_summary_agent.py
"""Unit tests for the SimpleSummaryAgent default agent."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.default.summary_agent.simple_summary_agent import \
    SimpleSummaryAgent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum


class TestSimpleSummaryAgent:
    """Test cases for SimpleSummaryAgent."""

    @pytest.fixture
    def agent(self):
        """Return a SimpleSummaryAgent with a stub agent model."""
        agent = SimpleSummaryAgent()
        agent.agent_model = SimpleNamespace(profile={})
        return agent

    def test_instantiation_without_arguments(self):
        """A freshly constructed agent has no agent_model configured."""
        agent = SimpleSummaryAgent()
        assert agent.agent_model is None

    def test_is_concrete_agent_component(self):
        """The agent is a concrete Agent component."""
        agent = SimpleSummaryAgent()
        assert isinstance(agent, ComponentBase)
        assert isinstance(agent, Agent)
        assert agent.component_type == ComponentEnum.AGENT
        assert SimpleSummaryAgent.__abstractmethods__ == frozenset()

    def test_input_keys(self):
        """The agent declares a single 'input' key."""
        assert SimpleSummaryAgent().input_keys() == ['input']

    def test_output_keys(self):
        """The agent declares a single 'output' key."""
        assert SimpleSummaryAgent().output_keys() == ['output']

    def test_parse_input_maps_input_data(self, agent):
        """parse_input copies the input data into the agent input."""
        agent_input = {}
        result = agent.parse_input(InputObject({'input': 'summarize the doc'}),
                                   agent_input)
        assert result is agent_input
        assert result == {'input': 'summarize the doc'}

    def test_parse_input_sets_default_prompt_version(self, agent):
        """The default prompt version is applied when profile has no version."""
        agent.parse_input(InputObject({'input': 'summarize the doc'}), {})
        assert agent.agent_model.profile.get(
            'prompt_version') == 'simple_summary_agent.cn'

    def test_parse_input_keeps_custom_prompt_version(self):
        """An explicit prompt version is never overwritten."""
        agent = SimpleSummaryAgent()
        agent.agent_model = SimpleNamespace(
            profile={'prompt_version': 'custom_summary_agent.cn'})
        agent.parse_input(InputObject({'input': 'summarize the doc'}), {})
        assert agent.agent_model.profile.get(
            'prompt_version') == 'custom_summary_agent.cn'

    def test_parse_result_passthrough(self, agent):
        """parse_result returns the planner result unchanged."""
        planner_result = {'output': 'the summary', 'extra': 1}
        assert agent.parse_result(planner_result) is planner_result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
