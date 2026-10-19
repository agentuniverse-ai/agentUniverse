# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03
# @Author  : agentuniverse-contributor
# @FileName: test_planning_agent_template.py
"""Unit tests for PlanningAgentTemplate pure helpers."""

import json
from queue import Queue
from types import SimpleNamespace

import pytest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.planning_agent_template import PlanningAgentTemplate


class TestPlanningAgentTemplate:
    """Test PlanningAgentTemplate without LLM or app configuration."""

    @pytest.fixture
    def agent(self) -> PlanningAgentTemplate:
        """Create an empty PlanningAgentTemplate instance."""
        return PlanningAgentTemplate()

    def test_input_keys(self, agent):
        """The planning template requires a single `input` key."""
        assert agent.input_keys() == ['input']

    def test_output_keys(self, agent):
        """The planning template produces `framework` and `thought` keys."""
        assert agent.output_keys() == ['framework', 'thought']

    def test_parse_input_extracts_expert_framework(self, agent):
        """parse_input reads the planning expert framework from the input."""
        input_object = InputObject({'input': 'plan me',
                                    'expert_framework': {'planning': 'step by step'}})
        result = agent.parse_input(input_object, {})
        assert result['input'] == 'plan me'
        assert result['expert_framework'] == 'step by step'

    def test_parse_result_parses_framework_and_thought(self, agent):
        """parse_result converts the JSON output into a framework dict."""
        raw_output = json.dumps({'framework': [{'name': 'step1', 'description': 'do it'}],
                                 'thought': 'a plan'})
        result = agent.parse_result({'output': raw_output})
        assert result['thought'] == 'a plan'
        assert result['framework'] == [{'name': 'step1', 'description': 'do it'}]

    def test_parse_result_defaults_missing_thought(self, agent):
        """A missing `thought` key defaults to an empty string."""
        raw_output = json.dumps({'framework': [{'name': 'step1'}]})
        result = agent.parse_result({'output': raw_output})
        assert result['thought'] == ''
        assert result['framework'] == [{'name': 'step1'}]

    def test_validate_required_params_raises_without_llm_name(self, agent):
        """validate_required_params raises ValueError when llm_name is empty."""
        agent.agent_model = SimpleNamespace(info={'name': 'PlanningAgent'})
        with pytest.raises(ValueError, match='llm_name of the agent PlanningAgent'):
            agent.validate_required_params()

    def test_validate_required_params_passes_with_llm_name(self, agent):
        """validate_required_params is a no-op once llm_name is configured."""
        agent.llm_name = 'planning_llm'
        assert agent.validate_required_params() is None

    def test_add_output_stream_noop_without_stream(self, agent):
        """A missing output stream is ignored."""
        assert agent.add_output_stream(None, 'some output') is None

    def test_add_output_stream_streams_framework(self, agent):
        """A planning framework is pushed onto the output stream queue."""
        agent.agent_model = SimpleNamespace(info={'name': 'PlanningAgent'})
        stream = Queue()
        raw_output = json.dumps({'framework': [{'name': 'step1'}], 'thought': 'a plan'})
        agent.add_output_stream(stream, raw_output)
        item = stream.get_nowait()
        assert item['type'] == 'planning'
        assert item['data']['agent_info'] == {'name': 'PlanningAgent'}
        assert item['data']['output'] == [{'name': 'step1'}]
