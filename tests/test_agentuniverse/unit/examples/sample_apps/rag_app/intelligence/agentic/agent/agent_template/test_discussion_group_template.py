# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_discussion_group_template.py

"""Unit tests for DiscussionGroupTemplate pure behaviors."""

import pytest

from agentuniverse.agent.input_object import InputObject
from examples.sample_apps.rag_app.intelligence.agentic.agent.agent_template.discussion_group_template import (
    DiscussionGroupTemplate,
)


def _make_template(**overrides):
    template = DiscussionGroupTemplate()
    template.participant_names = overrides.get('participant_names',
                                               ['lawyer_agent', 'moderator_agent'])
    template.total_round = overrides.get('total_round', 2)
    template.topic = overrides.get('topic', 'default discussion topic')
    return template


def test_input_keys_returns_input():
    assert _make_template().input_keys() == ['input']


def test_output_keys_returns_output():
    assert _make_template().output_keys() == ['output']


def test_default_field_values():
    template = DiscussionGroupTemplate()
    assert template.total_round == 2
    assert template.topic is None
    assert template.participant_names is None


def test_parse_input_takes_user_input():
    template = _make_template(topic='fallback topic')
    agent_input = {'input': 'pre'}
    result = template.parse_input(InputObject({'input': 'user question'}), agent_input)
    assert result['input'] == 'user question'
    assert result['participants'] == ['lawyer_agent', 'moderator_agent']
    assert result['total_round'] == 2


def test_parse_input_falls_back_to_topic():
    template = _make_template(topic='fallback topic')
    agent_input = {'input': 'pre'}
    result = template.parse_input(InputObject({}), agent_input)
    assert result['input'] == 'fallback topic'


def test_parse_input_keeps_configured_rounds_and_participants():
    template = _make_template(participant_names=['agent_a'], total_round=3)
    result = template.parse_input(InputObject({'input': 'q'}), {})
    assert result['participants'] == ['agent_a']
    assert result['total_round'] == 3


def test_parse_result_returns_agent_result():
    template = _make_template()
    agent_result = {'input': 'x', 'output': 'y'}
    assert template.parse_result(agent_result) is agent_result


def test_generate_participant_agents_raises_when_empty():
    template = _make_template(participant_names=[])
    with pytest.raises(ValueError, match='participant agents is empty'):
        template.generate_participant_agents()
