# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03
# @Author  : agentuniverse-contributor
# @FileName: test_is_agent_template.py
"""Unit tests for ISAgentTemplate pure template helpers."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.is_agent_template import ISAgentTemplate


class TestISAgentTemplate:
    """Test ISAgentTemplate without agents or app configuration."""

    @pytest.fixture
    def agent(self) -> ISAgentTemplate:
        return ISAgentTemplate()

    def test_default_configuration_attributes(self, agent):
        assert agent.implementation_agent_name == 'ImplementationAgent'
        assert agent.supervision_agent_name == 'SupervisionAgent'
        assert agent.checkpoint_count == 3
        assert agent.max_corrections == 2
        assert agent.agent_model is None

    def test_input_output_keys(self, agent):
        assert agent.input_keys() == ['input']
        assert agent.output_keys() == ['output']

    def test_parse_input_uses_class_defaults(self, agent):
        result = agent.parse_input(InputObject({'input': 'build a tool'}), {})
        assert result['input'] == 'build a tool'
        assert result['checkpoint_count'] == 3
        assert result['max_corrections'] == 2

    def test_parse_input_reads_overrides_from_input_object(self, agent):
        input_object = InputObject({'input': 'build a tool',
                                    'checkpoint_count': 5,
                                    'max_corrections': 1})
        result = agent.parse_input(input_object, {})
        assert result['checkpoint_count'] == 5
        assert result['max_corrections'] == 1

    def test_parse_result_formats_checkpoint_summary(self, agent):
        work_pattern_result = {'result': [
            {'implementation_result': {'checkpoint_output': 'impl1'},
             'supervision_result': {'needs_correction': True, 'feedback': 'fix it', 'score': 40}},
            {'implementation_result': {'checkpoint_output': 'impl2'},
             'supervision_result': {'needs_correction': False, 'score': 90},
             'correction_result': {'checkpoint_output': 'corr2'}},
        ], 'execution_context': {'corrections_made': 1}}
        result = agent.parse_result(work_pattern_result)
        assert result['output'] == 'impl2'
        assert result['checkpoint_results'] == work_pattern_result['result']
        assert result['execution_context'] == {'corrections_made': 1}
        assert 'Total Checkpoints: 2' in result['full_output']
        assert 'Corrections Made: 1' in result['full_output']
        assert '=== Final Output ===\nimpl2' in result['full_output']

    def test_parse_result_empty_result(self, agent):
        result = agent.parse_result({})
        assert result['output'] == ''
        assert result['checkpoint_results'] == []
        assert result['execution_context'] == {}
        assert 'Total Checkpoints: 0' in result['full_output']

    def test_build_expert_framework_disabled_returns_empty(self, agent):
        agent.agent_model = SimpleNamespace(profile={})
        result = agent._build_expert_framework({'input': 'q'}, InputObject({'input': 'q'}))
        assert result == {}

    def test_build_expert_framework_merges_input_and_profile(self, agent):
        agent.agent_model = SimpleNamespace(profile={
            'expert_framework_enabled': True,
            'expert_framework': {'implementation': 'implX', 'supervision': 'supX'},
        })
        input_object = InputObject({'expert_framework': {'implementation': 'frominput'}})
        result = agent._build_expert_framework({'input': 'q'}, input_object)
        assert result == {'implementation': 'frominput', 'supervision': 'supX'}
