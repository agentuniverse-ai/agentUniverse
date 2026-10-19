# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_discussion_group_template.py

"""Unit tests for the DiscussionGroupTemplate example agent template."""

import pytest
from agentuniverse.agent.input_object import InputObject

from examples.sample_apps.discussion_group_app.intelligence.agentic.agent.agent_template.discussion_group_template import (
    DiscussionGroupTemplate,
)


class TestDiscussionGroupTemplate:
    """Tests for DiscussionGroupTemplate keys, parsing and guards."""

    def setup_method(self):
        self.template = DiscussionGroupTemplate()

    def test_input_keys_declares_input(self):
        assert self.template.input_keys() == ['input']

    def test_output_keys_declares_output(self):
        assert self.template.output_keys() == ['output']

    def test_parse_input_maps_input_participants_and_round(self):
        self.template.participant_names = ['alice', 'bob']
        self.template.total_round = 3
        input_object = InputObject({'input': 'discuss topic'})
        result = self.template.parse_input(input_object, {})
        assert result['input'] == 'discuss topic'
        assert result['participants'] == ['alice', 'bob']
        assert result['total_round'] == 3

    def test_parse_input_falls_back_to_topic_when_input_missing(self):
        self.template.topic = 'default topic'
        input_object = InputObject({})
        result = self.template.parse_input(input_object, {})
        assert result['input'] == 'default topic'

    def test_parse_result_returns_agent_result_unchanged(self):
        agent_result = {'output': 'summary', 'rounds': 2}
        assert self.template.parse_result(agent_result) == agent_result

    def test_generate_participant_agents_raises_on_empty_names(self):
        self.template.participant_names = []
        with pytest.raises(ValueError, match='The participant agents is empty'):
            self.template.generate_participant_agents()

    def test_default_total_round_is_two(self):
        assert self.template.total_round == 2
