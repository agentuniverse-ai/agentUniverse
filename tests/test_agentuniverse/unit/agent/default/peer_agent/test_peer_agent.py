# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/20 10:00
# @Author  : au_qa
# @FileName: test_peer_agent.py
"""Unit tests for the PeerAgent default agent."""

import pytest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.default.peer_agent.peer_agent import PeerAgent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.peer_agent_template import PeerAgentTemplate
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum


class TestPeerAgent:
    """Test cases for PeerAgent."""

    @pytest.fixture
    def agent(self):
        """Return a fresh PeerAgent instance."""
        return PeerAgent()

    def test_instantiation_without_arguments(self, agent):
        """A freshly constructed agent has no agent_model configured."""
        assert agent.agent_model is None
        assert agent.component_type == ComponentEnum.AGENT

    def test_inheritance_chain(self):
        """PeerAgent is a concrete PeerAgentTemplate component."""
        assert issubclass(PeerAgent, PeerAgentTemplate)
        assert issubclass(PeerAgent, AgentTemplate)
        assert issubclass(PeerAgent, Agent)
        assert issubclass(PeerAgent, ComponentBase)
        assert PeerAgent.__abstractmethods__ == frozenset()

    def test_default_peer_agent_names(self, agent):
        """The four sub-agent names of the default peer workflow."""
        assert agent.planning_agent_name == 'PlanningAgent'
        assert agent.executing_agent_name == 'ExecutingAgent'
        assert agent.expressing_agent_name == 'ExpressingAgent'
        assert agent.reviewing_agent_name == 'ReviewingAgent'

    def test_default_peer_settings(self, agent):
        """Default eval threshold, retry count and jump step."""
        assert agent.eval_threshold == 60
        assert agent.retry_count == 2
        assert agent.jump_step == 'expressing'
        assert agent.expert_framework is None

    def test_input_keys(self, agent):
        """The agent declares a single 'input' key."""
        assert agent.input_keys() == ['input']

    def test_output_keys(self, agent):
        """The agent declares a single 'output' key."""
        assert agent.output_keys() == ['output']

    def test_parse_input_decorates_agent_input(self, agent):
        """parse_input maps the input and injects peer settings."""
        agent_input = {}
        result = agent.parse_input(InputObject({'input': 'solve it'}), agent_input)
        assert result is agent_input
        assert result == {'input': 'solve it', 'eval_threshold': 60,
                          'retry_count': 2, 'jump_step': 'expressing'}

    def test_parse_input_without_input_data(self, agent):
        """A missing input is mapped to None without crashing."""
        result = agent.parse_input(InputObject({}), {})
        assert result['input'] is None
        assert result['jump_step'] == 'expressing'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
