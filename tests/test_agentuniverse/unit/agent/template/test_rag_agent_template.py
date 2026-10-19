# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03
# @Author  : agentuniverse-contributor
# @FileName: test_rag_agent_template.py
"""Unit tests for RagAgentTemplate pure template-level helpers."""

import pytest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate


class TestRagAgentTemplate:
    """Test RagAgentTemplate without any app configuration."""

    @pytest.fixture
    def agent(self) -> RagAgentTemplate:
        """Create an empty RagAgentTemplate instance."""
        return RagAgentTemplate()

    def test_input_keys(self, agent):
        """The template requires a single `input` key."""
        assert agent.input_keys() == ['input']

    def test_output_keys(self, agent):
        """The template produces a single `output` key."""
        assert agent.output_keys() == ['output']

    def test_parse_input_reads_input_data(self, agent):
        """parse_input copies the `input` data into the agent input dict."""
        agent_input = {'agent_id': 'rag_agent'}
        result = agent.parse_input(InputObject({'input': 'What is agentUniverse?'}), agent_input)
        assert result['input'] == 'What is agentUniverse?'
        assert result is agent_input

    def test_parse_input_missing_input_defaults_to_none(self, agent):
        """A missing `input` data key is resolved to None, not an error."""
        result = agent.parse_input(InputObject({'other': 1}), {})
        assert result['input'] is None

    def test_parse_result_passthrough_output(self, agent):
        """parse_result keeps the raw output and any extra keys."""
        result = agent.parse_result({'input': 'q', 'output': 'an answer'})
        assert result['output'] == 'an answer'
        assert result['input'] == 'q'

    def test_defaults_without_agent_model(self, agent):
        """An empty instance is valid and exposes default field values."""
        assert agent.agent_model is None
        assert agent.llm_name == ''

    def test_is_an_agent_template_subclass(self, agent):
        """RagAgentTemplate derives from AgentTemplate."""
        assert isinstance(agent, AgentTemplate)
