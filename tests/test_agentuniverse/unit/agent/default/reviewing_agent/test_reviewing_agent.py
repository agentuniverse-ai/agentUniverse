# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/06/30 10:20
# @Author  : agentuniverse
# @FileName: test_reviewing_agent.py
"""Unit tests for the ReviewingAgent default agent module."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.default.reviewing_agent.reviewing_agent import ReviewingAgent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate
from agentuniverse.base.component.component_enum import ComponentEnum


class TestReviewingAgent:
    """Test the ReviewingAgent default agent."""

    @pytest.fixture
    def agent(self):
        """Create a ReviewingAgent instance without any configuration."""
        return ReviewingAgent()

    def test_class_hierarchy(self):
        """ReviewingAgent should inherit from the reviewing template chain."""
        assert issubclass(ReviewingAgent, ReviewingAgentTemplate)
        assert issubclass(ReviewingAgent, AgentTemplate)
        assert issubclass(ReviewingAgent, Agent)

    def test_instantiation(self, agent):
        """A ReviewingAgent can be created without a config and is an AGENT component."""
        assert isinstance(agent, ReviewingAgent)
        assert agent.component_type == ComponentEnum.AGENT
        assert agent.agent_model is None

    def test_input_keys(self, agent):
        """The reviewing agent consumes input and expressing_result."""
        assert agent.input_keys() == ['input', 'expressing_result']

    def test_output_keys(self, agent):
        """The reviewing agent produces output, score and suggestion."""
        assert agent.output_keys() == ['output', 'score', 'suggestion']

    def test_parse_input(self, agent):
        """parse_input should read the drafted output and reviewing framework."""
        input_object = InputObject({
            'input': 'a question',
            'expressing_result': OutputObject({'output': 'the draft answer'}),
            'expert_framework': {'reviewing': 'check for clarity'},
        })
        parsed = agent.parse_input(input_object, {'chat_history': ''})
        assert parsed['input'] == 'a question'
        assert parsed['expressing_result'] == 'the draft answer'
        assert parsed['expert_framework'] == 'check for clarity'

    @pytest.mark.parametrize(
        'raw_output, expected_score',
        [
            ('{"is_useful": true, "suggestion": "keep"}', 80),
            ('{"is_useful": false, "suggestion": "rewrite"}', 0),
            ('{"suggestion": "neutral"}', 0),
        ],
    )
    def test_parse_result_score(self, agent, raw_output, expected_score):
        """A useful result scores 80, everything else scores 0."""
        result = agent.parse_result({'output': raw_output})
        assert result['score'] == expected_score
        assert result['suggestion'] is not None

    def test_parse_result_output_is_json(self, agent):
        """The raw output string should be parsed into a dict."""
        result = agent.parse_result({'output': '{"is_useful": true, "suggestion": "keep"}'})
        assert result['output'] == {'is_useful': True, 'suggestion': 'keep'}

    def test_validate_required_params(self, agent):
        """validate_required_params fails without an llm_name and passes with one."""
        agent.agent_model = SimpleNamespace(info={'name': 'reviewing_agent'})
        with pytest.raises(ValueError, match='llm_name of the agent'):
            agent.validate_required_params()
        agent.llm_name = 'gpt-4o'
        assert agent.validate_required_params() is None
