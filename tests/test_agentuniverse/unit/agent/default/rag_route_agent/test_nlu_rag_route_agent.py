# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/20 10:00
# @Author  : au_qa
# @FileName: test_nlu_rag_route_agent.py
"""Unit tests for the NluRagRouteAgent default agent."""

import pytest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.default.rag_route_agent.nlu_rag_route_agent import \
    NluRagRouteAgent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum


class TestNluRagRouteAgent:
    """Test cases for NluRagRouteAgent."""

    @pytest.fixture
    def agent(self):
        """Return a fresh NluRagRouteAgent instance."""
        return NluRagRouteAgent()

    def test_instantiation_without_arguments(self, agent):
        """A freshly constructed agent has no agent_model configured."""
        assert agent.agent_model is None

    def test_inheritance_chain(self):
        """NluRagRouteAgent is a concrete RagAgentTemplate component."""
        assert issubclass(NluRagRouteAgent, RagAgentTemplate)
        assert issubclass(NluRagRouteAgent, AgentTemplate)
        assert issubclass(NluRagRouteAgent, Agent)
        assert issubclass(NluRagRouteAgent, ComponentBase)
        assert NluRagRouteAgent.__abstractmethods__ == frozenset()

    def test_component_type(self, agent):
        """NluRagRouteAgent is registered as an Agent component."""
        assert agent.component_type == ComponentEnum.AGENT

    def test_input_keys(self, agent):
        """The agent declares the three nlu routing input keys."""
        assert agent.input_keys() == ['query', 'store_info', 'store_amount']

    def test_output_keys(self, agent):
        """The agent declares a single 'output' key."""
        assert agent.output_keys() == ['output']

    def test_parse_input_maps_input_object_fields(self, agent):
        """parse_input copies query/store_info/store_amount verbatim."""
        agent_input = {}
        result = agent.parse_input(
            InputObject({'query': 'what is rent', 'store_info': 'rental info',
                         'store_amount': 3}), agent_input)
        assert result is agent_input
        assert result == {'query': 'what is rent',
                          'store_info': 'rental info', 'store_amount': 3}

    def test_parse_input_missing_fields_become_none(self, agent):
        """parse_input maps missing fields to None without crashing."""
        result = agent.parse_input(InputObject({}), {})
        assert result == {'query': None, 'store_info': None,
                          'store_amount': None}

    def test_parse_result_passthrough(self, agent):
        """parse_result returns the agent result unchanged."""
        agent_result = {'output': 'routed', 'meta': 'value'}
        assert agent.parse_result(agent_result) is agent_result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
