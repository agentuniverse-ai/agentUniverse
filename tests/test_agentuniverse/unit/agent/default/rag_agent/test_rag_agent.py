# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/06/30 10:00
# @Author  : agentuniverse
# @FileName: test_rag_agent.py
"""Unit tests for the RagAgent default agent module."""

import pytest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.default.rag_agent.rag_agent import RagAgent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate
from agentuniverse.base.component.component_enum import ComponentEnum


class TestRagAgent:
    """Test the RagAgent default agent."""

    @pytest.fixture
    def agent(self):
        """Create a RagAgent instance without any configuration."""
        return RagAgent()

    def test_class_hierarchy(self):
        """RagAgent should inherit from the rag agent template chain."""
        assert issubclass(RagAgent, RagAgentTemplate)
        assert issubclass(RagAgent, AgentTemplate)
        assert issubclass(RagAgent, Agent)

    def test_instantiation(self, agent):
        """A RagAgent can be created without a config and is an AGENT component."""
        assert isinstance(agent, RagAgent)
        assert agent.component_type == ComponentEnum.AGENT
        assert agent.agent_model is None
        assert agent.is_default_object() is False

    def test_input_keys(self, agent):
        """The only input key is 'input'."""
        assert agent.input_keys() == ['input']

    def test_output_keys(self, agent):
        """The only output key is 'output'."""
        assert agent.output_keys() == ['output']

    def test_parse_input(self, agent):
        """parse_input should take the raw input from the InputObject."""
        input_object = InputObject({'input': 'what is agentUniverse?'})
        parsed = agent.parse_input(input_object, {'background': 'bg'})
        assert parsed == {'background': 'bg', 'input': 'what is agentUniverse?'}

    def test_parse_input_missing_key(self, agent):
        """A missing input key should default to None."""
        parsed = agent.parse_input(InputObject({}), {})
        assert parsed == {'input': None}

    def test_parse_result(self, agent):
        """parse_result should keep the raw result and copy the output."""
        result = agent.parse_result({'input': 'q', 'output': 'answer'})
        assert result == {'input': 'q', 'output': 'answer'}

    def test_parse_result_requires_output(self, agent):
        """parse_result should fail when the result has no output key."""
        with pytest.raises(KeyError):
            agent.parse_result({'input': 'q'})
