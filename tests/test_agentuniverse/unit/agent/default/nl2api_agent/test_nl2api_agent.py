# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/06/30 10:50
# @Author  : agentuniverse
# @FileName: test_nl2api_agent.py
"""Unit tests for the Nl2ApiAgent default agent module."""

import pytest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.default.nl2api_agent.nl2api_agent import Nl2ApiAgent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.nl2api_agent_template import Nl2ApiAgentTemplate
from agentuniverse.base.component.component_enum import ComponentEnum


class TestNl2ApiAgent:
    """Test the Nl2ApiAgent default agent."""

    @pytest.fixture
    def agent(self):
        """Create an Nl2ApiAgent with an empty tool action for offline tests."""
        agent = Nl2ApiAgent()
        agent.agent_model = AgentModel(
            info={'name': 'nl2api_agent'},
            action={'tool': [], 'toolkit': []},
        )
        return agent

    def test_class_hierarchy(self):
        """Nl2ApiAgent should inherit from the nl2api template chain."""
        assert issubclass(Nl2ApiAgent, Nl2ApiAgentTemplate)
        assert issubclass(Nl2ApiAgent, AgentTemplate)
        assert issubclass(Nl2ApiAgent, Agent)

    def test_instantiation(self):
        """An Nl2ApiAgent can be created without a config and is an AGENT component."""
        agent = Nl2ApiAgent()
        assert isinstance(agent, Nl2ApiAgent)
        assert agent.component_type == ComponentEnum.AGENT
        assert agent.agent_model is None

    def test_input_keys(self, agent):
        """The only input key is 'input'."""
        assert agent.input_keys() == ['input']

    def test_output_keys(self, agent):
        """The only output key is 'output'."""
        assert agent.output_keys() == ['output']

    def test_tools_context_without_tools(self, agent):
        """No tools configured yields an empty tool list and empty tools context."""
        assert agent.tool_names == []
        assert agent.build_tools_context() == ''

    def test_parse_input(self, agent):
        """parse_input should carry the input and a tools context."""
        input_object = InputObject({'input': 'convert my query to an api call'})
        parsed = agent.parse_input(input_object, {'chat_history': ''})
        assert parsed['chat_history'] == ''
        assert parsed['input'] == 'convert my query to an api call'
        assert parsed['tools'] == ''

    def test_parse_result(self, agent):
        """parse_result should keep the raw result and copy the output."""
        result = agent.parse_result({'input': 'q', 'output': 'api json'})
        assert result == {'input': 'q', 'output': 'api json'}

    def test_parse_result_requires_output(self, agent):
        """parse_result should fail when the result has no output key."""
        with pytest.raises(KeyError):
            agent.parse_result({'input': 'q'})
