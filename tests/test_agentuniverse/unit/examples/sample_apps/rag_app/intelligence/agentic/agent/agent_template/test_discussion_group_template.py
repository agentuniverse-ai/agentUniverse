# !/usr/bin/env python3
# -*- coding:utf-8 -*-


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


@pytest.mark.parametrize('user_input', [None, ''])
def test_parse_input_empty_value_uses_topic_without_losing_other_fields(user_input):
    template = _make_template(topic='fallback')
    agent_input = {'metadata': {'request_id': 'request-1'}}
    result = template.parse_input(InputObject({'input': user_input}), agent_input)
    assert result is agent_input
    assert result['input'] == 'fallback'
    assert result['metadata'] == {'request_id': 'request-1'}


def test_generate_participant_agents_resolves_configured_names(monkeypatch):
    from unittest.mock import Mock
    from examples.sample_apps.rag_app.intelligence.agentic.agent.agent_template import discussion_group_template as module

    agents = {'agent_a': object(), 'agent_b': object()}
    manager = Mock()
    manager.get_instance_obj.side_effect = agents.__getitem__
    monkeypatch.setattr(module, 'AgentManager', lambda: manager)
    result = _make_template(participant_names=list(agents)).generate_participant_agents()
    assert result == agents
    assert [call.args[0] for call in manager.get_instance_obj.call_args_list] == list(agents)


def test_agents_run_passes_rounds_and_bounded_history_to_participants(monkeypatch):
    from types import SimpleNamespace
    from unittest.mock import Mock
    from agentuniverse.agent.agent_model import AgentModel
    from agentuniverse.agent.output_object import OutputObject
    from examples.sample_apps.rag_app.intelligence.agentic.agent.agent_template import discussion_group_template as module

    template = _make_template(participant_names=['agent_a', 'agent_b'], total_round=2)
    template.agent_model = AgentModel(info={'name': 'host'})
    calls = []

    def run(**kwargs):
        calls.append((kwargs['agent_name'], kwargs['cur_round'],
                      kwargs['total_round'], kwargs['participants'],
                      list(kwargs['chat_history'])))
        return OutputObject({'output': f"{kwargs['agent_name']}:{kwargs['cur_round']}"})

    def append_memory(memory, agent_input, content, agent_name, history):
        history.append(agent_name)
        return history

    host_result = {'output': 'summary'}
    host_run = Mock(return_value=host_result)
    monkeypatch.setattr(DiscussionGroupTemplate, 'process_memory', lambda *args: None)
    monkeypatch.setattr(DiscussionGroupTemplate, 'host_agent_run', host_run)
    monkeypatch.setattr(module, 'assemble_memory_output', append_memory)
    stream = Mock()
    monkeypatch.setattr(module, 'stream_output', stream)
    agents = {name: SimpleNamespace(run=run) for name in template.participant_names}
    agent_input = {'input': 'topic'}
    input_object = InputObject({'input': 'topic'})

    assert template.agents_run(agents, agent_input, input_object) is host_result
    assert calls == [
        ('agent_a', 1, 2, 'agent_a and agent_b', []),
        ('agent_b', 1, 2, 'agent_a and agent_b', ['agent_a']),
        ('agent_a', 2, 2, 'agent_a and agent_b', ['agent_b']),
        ('agent_b', 2, 2, 'agent_a and agent_b', ['agent_a']),
    ]
    host_run.assert_called_once_with(agent_input, input_object)
    assert agent_input['total_round'] == 2
    assert agent_input['participants'] == 'agent_a and agent_b'
    assert stream.call_count == 4
    assert [call.args[1]['data']['output'] for call in stream.call_args_list] == [
        'agent_a:1', 'agent_b:1', 'agent_a:2', 'agent_b:2',
    ]
