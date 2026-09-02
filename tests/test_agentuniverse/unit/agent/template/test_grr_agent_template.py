# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03
# @Author  : agentuniverse-contributor
# @FileName: test_grr_agent_template.py
"""Unit tests for GRRAgentTemplate pure template helpers."""

import pytest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.grr_agent_template import GRRAgentTemplate


class _StubMemory:
    """Memory stub collecting the messages and kwargs passed to add()."""

    def __init__(self):
        self.added = None

    def add(self, messages, **kwargs):
        self.added = (messages, kwargs)


class TestGRRAgentTemplate:
    """Test GRRAgentTemplate without agents, tools or app configuration."""

    @pytest.fixture
    def agent(self) -> GRRAgentTemplate:
        return GRRAgentTemplate()

    def test_default_configuration_attributes(self, agent):
        assert agent.generating_agent_name == 'GeneratingAgent'
        assert agent.reviewing_agent_name == 'ReviewingAgent'
        assert agent.rewriting_agent_name == 'RewritingAgent'
        assert agent.eval_threshold == 60
        assert agent.retry_count == 2
        assert agent.expert_framework is None

    def test_input_output_keys(self, agent):
        assert agent.input_keys() == ['input']
        assert agent.output_keys() == ['output']

    def test_parse_input_adds_configuration_values(self, agent):
        result = agent.parse_input(InputObject({'input': 'write a report'}), {})
        assert result['input'] == 'write a report'
        assert result['eval_threshold'] == 60
        assert result['retry_count'] == 2

    def test_parse_result_prefers_rewriting_over_generating(self, agent):
        agent_result = {'result': [
            {'generating_result': {'output': 'draft'}},
            {'rewriting_result': {'output': 'polished'}},
        ]}
        assert agent.parse_result(agent_result) == {'output': 'polished'}

    def test_parse_result_falls_back_to_generating_or_empty(self, agent):
        generating_only = {'result': [{'generating_result': {'output': 'draft'}}]}
        assert agent.parse_result(generating_only) == {'output': 'draft'}
        assert agent.parse_result({}) == {'output': ''}

    def test_add_grr_memory_returns_none_without_memory(self, agent):
        assert agent.add_grr_memory(None, {'input': 'q'}, {'result': []}) is None

    def test_add_grr_memory_builds_role_messages(self, agent):
        memory = _StubMemory()
        work_pattern_result = {'result': [{
            'generating_result': {'output': 'G'},
            'reviewing_result': {'score': 90, 'suggestion': 'improve it'},
            'rewriting_result': {'output': 'R'},
        }]}
        agent.add_grr_memory(memory, {'input': 'q'}, work_pattern_result)
        messages, kwargs = memory.added
        assert kwargs == {'input': 'q'}
        assert [m.source for m in messages] == ['GeneratingAgent', 'ReviewingAgent', 'RewritingAgent']
        assert 'GRR work pattern turn 1' in messages[0].content
        assert messages[0].content.endswith('GeneratingAgent, Human: q, AI: G')
        assert 'Score: 90, Suggestion: improve it' in messages[1].content

    def test_build_expert_framework_handles_raw_context(self, agent):
        context = {'generating': 'g', 'reviewing': 'r', 'rewriting': 'rw'}
        agent.expert_framework = {'context': context}
        input_object = InputObject({'input': 'q'})
        agent.build_expert_framework(input_object)
        assert input_object.get_data('expert_framework') == context
        agent.expert_framework = {'context': 'not a dict'}
        with pytest.raises(ValueError, match='must be a dictionary'):
            agent.build_expert_framework(InputObject({'input': 'q'}))
