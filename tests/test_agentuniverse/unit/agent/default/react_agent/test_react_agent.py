# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/20 10:00
# @Author  : au_qa
# @FileName: test_react_agent.py
"""Unit tests for the ReActAgent default agent."""

import pytest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.default.react_agent.react_agent import ReActAgent
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.react_agent_template import ReActAgentTemplate
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum


class TestReActAgent:
    """Test cases for ReActAgent."""

    @pytest.fixture
    def agent(self):
        """Return a fresh ReActAgent instance."""
        return ReActAgent()

    def test_instantiation_without_arguments(self, agent):
        """A freshly constructed agent has no agent_model configured."""
        assert agent.agent_model is None

    def test_inheritance_chain(self):
        """ReActAgent is a concrete ReActAgentTemplate component."""
        assert issubclass(ReActAgent, ReActAgentTemplate)
        assert issubclass(ReActAgent, AgentTemplate)
        assert issubclass(ReActAgent, Agent)
        assert issubclass(ReActAgent, ComponentBase)
        assert ReActAgent.__abstractmethods__ == frozenset()

    def test_component_type(self, agent):
        """ReActAgent is registered as an Agent component."""
        assert agent.component_type == ComponentEnum.AGENT

    def test_input_keys(self, agent):
        """The agent declares a single 'input' key."""
        assert agent.input_keys() == ['input']

    def test_output_keys(self, agent):
        """The agent declares a single 'output' key."""
        assert agent.output_keys() == ['output']

    def test_default_react_settings(self, agent):
        """The react workflow knobs default to None until configured."""
        assert agent.agent_names is None
        assert agent.stop_sequence is None
        assert agent.max_iterations is None

    def test_parse_result_passthrough(self, agent):
        """parse_result keeps every key and forces the output field."""
        agent_result = {'output': 'final answer', 'thought': 'think step'}
        result = agent.parse_result(agent_result)
        assert result == agent_result
        assert result['output'] == 'final answer'
        assert agent_result == {'output': 'final answer',
                                'thought': 'think step'}

    def test_parse_result_requires_output_key(self, agent):
        """parse_result raises KeyError when the output key is missing."""
        with pytest.raises(KeyError):
            agent.parse_result({'thought': 'no output given'})


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
