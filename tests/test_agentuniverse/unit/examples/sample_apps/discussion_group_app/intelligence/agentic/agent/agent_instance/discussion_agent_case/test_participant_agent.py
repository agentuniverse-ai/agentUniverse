# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_participant_agent.py

"""Unit tests for the ParticipantAgent example agent."""

from agentuniverse.agent.input_object import InputObject

from examples.sample_apps.discussion_group_app.intelligence.agentic.agent.agent_instance.discussion_agent_case.participant_agent import (
    ParticipantAgent,
)


class TestParticipantAgent:
    """Tests for ParticipantAgent key/output declarations and parsing."""

    def setup_method(self):
        self.agent = ParticipantAgent()

    def test_input_keys_declares_input(self):
        assert self.agent.input_keys() == ['input']

    def test_output_keys_declares_output(self):
        assert self.agent.output_keys() == ['output']

    def test_parse_input_maps_all_supported_fields(self):
        input_object = InputObject({
            'input': 'discussion topic',
            'agent_name': 'participant_a',
            'total_round': 2,
            'cur_round': 1,
            'participants': 'participant_a and participant_b',
        })
        agent_input = {}
        result = self.agent.parse_input(input_object, agent_input)
        assert result['input'] == 'discussion topic'
        assert result['agent_name'] == 'participant_a'
        assert result['total_round'] == 2
        assert result['cur_round'] == 1
        assert result['participants'] == 'participant_a and participant_b'

    def test_parse_input_keeps_pre_existing_agent_input(self):
        input_object = InputObject({'input': 'topic'})
        agent_input = {'preparsed': 'kept'}
        result = self.agent.parse_input(input_object, agent_input)
        assert result['preparsed'] == 'kept'
        assert result['input'] == 'topic'

    def test_parse_input_missing_fields_default_to_none(self):
        input_object = InputObject({'input': 'topic'})
        result = self.agent.parse_input(input_object, {})
        assert result['agent_name'] is None
        assert result['total_round'] is None
        assert result['cur_round'] is None
        assert result['participants'] is None

    def test_parse_result_returns_agent_result_unchanged(self):
        agent_result = {'output': 'final answer', 'extra': 1}
        assert self.agent.parse_result(agent_result) == agent_result
