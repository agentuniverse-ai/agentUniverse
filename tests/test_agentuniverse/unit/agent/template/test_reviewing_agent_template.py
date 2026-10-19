# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03
# @Author  : agentuniverse-contributor
# @FileName: test_reviewing_agent_template.py
"""Unit tests for ReviewingAgentTemplate pure template helpers."""

import json
from queue import Queue
from types import SimpleNamespace

import pytest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate


class TestReviewingAgentTemplate:
    """Test ReviewingAgentTemplate without LLM or app configuration."""

    @pytest.fixture
    def agent(self) -> ReviewingAgentTemplate:
        return ReviewingAgentTemplate()

    def test_input_output_keys(self, agent):
        assert agent.input_keys() == ['input', 'expressing_result']
        assert agent.output_keys() == ['output', 'score', 'suggestion']

    def test_defaults_without_agent_model(self, agent):
        assert agent.agent_model is None
        assert agent.llm_name == ''

    def test_parse_input_reads_expressing_and_expert_framework(self, agent):
        input_object = InputObject({
            'input': 'review it',
            'expressing_result': InputObject({'output': 'draft answer'}),
            'expert_framework': {'reviewing': 'check grammar'},
        })
        result = agent.parse_input(input_object, {})
        assert result['input'] == 'review it'
        assert result['expressing_result'] == 'draft answer'
        assert result['expert_framework'] == 'check grammar'

    def test_parse_result_scores_according_to_is_useful(self, agent):
        usable = agent.parse_result({'output': json.dumps({'is_useful': True, 'suggestion': 'ok'})})
        assert usable['score'] == 80
        assert usable['suggestion'] == 'ok'
        assert usable['output'] == {'is_useful': True, 'suggestion': 'ok'}
        unusable = agent.parse_result({'output': json.dumps({'is_useful': False})})
        assert unusable['score'] == 0
        missing = agent.parse_result({'output': '{"suggestion": "vague"}'})
        assert missing['score'] == 0
        assert missing['output']['suggestion'] == 'vague'

    def test_validate_required_params_depends_on_llm_name(self, agent):
        agent.agent_model = SimpleNamespace(info={'name': 'ReviewingAgent'})
        with pytest.raises(ValueError, match='llm_name of the agent ReviewingAgent'):
            agent.validate_required_params()
        agent.llm_name = 'reviewing_llm'
        assert agent.validate_required_params() is None

    def test_add_output_stream_noop_without_stream(self, agent):
        assert agent.add_output_stream(None, 'output text') is None

    def test_add_output_stream_streams_review_output(self, agent):
        agent.agent_model = SimpleNamespace(info={'name': 'ReviewingAgent'})
        stream = Queue()
        agent.add_output_stream(stream, 'final review')
        item = stream.get_nowait()
        assert item['type'] == 'reviewing'
        assert item['data']['output'] == 'final review'
        assert item['data']['agent_info'] == {'name': 'ReviewingAgent'}
