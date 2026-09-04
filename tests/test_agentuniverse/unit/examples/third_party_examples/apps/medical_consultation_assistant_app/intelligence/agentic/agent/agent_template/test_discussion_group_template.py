# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the discussion group agent template of the medical app."""

import pytest

from agentuniverse.agent.input_object import InputObject
from examples.third_party_examples.apps.medical_consultation_assistant_app.intelligence.agentic.agent.agent_template.discussion_group_template import (
    DiscussionGroupTemplate,
)


class TestDiscussionGroupTemplate:
    def _make_template(self):
        template = DiscussionGroupTemplate()
        template.participant_names = ['doctor_a', 'doctor_b']
        template.total_round = 3
        template.topic = 'discuss the fever case'
        return template

    def test_input_keys(self):
        assert self._make_template().input_keys() == ['input']

    def test_output_keys(self):
        assert self._make_template().output_keys() == ['output']

    def test_parse_input_maps_user_input(self):
        template = self._make_template()
        agent_input = template.parse_input(InputObject({'input': 'patient question'}), {})
        assert agent_input['input'] == 'patient question'
        assert agent_input['participants'] == ['doctor_a', 'doctor_b']
        assert agent_input['total_round'] == 3

    def test_parse_input_falls_back_to_topic(self):
        template = self._make_template()
        agent_input = template.parse_input(InputObject({}), {})
        assert agent_input['input'] == 'discuss the fever case'

    def test_parse_result_passthrough(self):
        result = self._make_template().parse_result({'output': 'summary'})
        assert result == {'output': 'summary'}

    def test_generate_participant_agents_raises_when_empty(self):
        template = DiscussionGroupTemplate()
        template.participant_names = []
        with pytest.raises(ValueError, match='participant agents is empty'):
            template.generate_participant_agents()

    def test_generate_participant_agents_builds_mapping(self, monkeypatch):
        template = self._make_template()

        class _FakeManager:
            def get_instance_obj(self, name):
                return f'agent:{name}'

        monkeypatch.setattr(
            'examples.third_party_examples.apps.medical_consultation_assistant_app.intelligence.agentic.agent.agent_template.discussion_group_template.AgentManager',
            _FakeManager,
        )
        agents = template.generate_participant_agents()
        assert set(agents.keys()) == {'doctor_a', 'doctor_b'}
        assert agents['doctor_a'] == 'agent:doctor_a'
