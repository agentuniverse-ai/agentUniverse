# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03
# @Author  : agentuniverse-contributor
# @FileName: test_peer_agent_template.py
"""Unit tests for PeerAgentTemplate pure template helpers."""

import pytest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.peer_agent_template import PeerAgentTemplate


class TestPeerAgentTemplate:
    """Test PeerAgentTemplate without agents, tools or app configuration."""

    @pytest.fixture
    def agent(self) -> PeerAgentTemplate:
        return PeerAgentTemplate()

    def test_default_configuration_attributes(self, agent):
        assert agent.planning_agent_name == 'PlanningAgent'
        assert agent.executing_agent_name == 'ExecutingAgent'
        assert agent.expressing_agent_name == 'ExpressingAgent'
        assert agent.reviewing_agent_name == 'ReviewingAgent'
        assert agent.eval_threshold == 60
        assert agent.retry_count == 2
        assert agent.jump_step == 'expressing'
        assert agent.expert_framework is None

    def test_input_output_keys(self, agent):
        assert agent.input_keys() == ['input']
        assert agent.output_keys() == ['output']

    def test_parse_input_adds_configuration_values(self, agent):
        result = agent.parse_input(InputObject({'input': 'plan and solve'}), {})
        assert result['input'] == 'plan and solve'
        assert result['eval_threshold'] == 60
        assert result['retry_count'] == 2
        assert result['jump_step'] == 'expressing'

    def test_parse_result_returns_latest_expressing_output(self, agent):
        agent_result = {'result': [
            {'expressing_result': {'output': 'first'}},
            {'planning_result': {'framework': 'f'}},
            {'expressing_result': {'output': 'latest'}},
        ]}
        assert agent.parse_result(agent_result) == {'output': 'latest'}

    def test_parse_result_returns_none_without_expressing_result(self, agent):
        agent_result = {'result': [
            {'planning_result': {'framework': 'f'}},
            {'reviewing_result': {'suggestion': 's'}},
        ]}
        assert agent.parse_result(agent_result) is None

    def test_add_peer_memory_returns_none_without_memory(self, agent):
        result = agent.add_peer_memory(None, {'input': 'q'}, {'result': []})
        assert result is None

    def test_build_expert_framework_injects_raw_context(self, agent):
        context = {'planning': 'p', 'executing': 'e'}
        agent.expert_framework = {'context': context}
        input_object = InputObject({'input': 'q'})
        agent.build_expert_framework(input_object)
        assert input_object.get_data('expert_framework') == context

    def test_build_expert_framework_rejects_non_dict_context(self, agent):
        agent.expert_framework = {'context': 'not a dict'}
        with pytest.raises(ValueError, match='must be a dictionary'):
            agent.build_expert_framework(InputObject({'input': 'q'}))
