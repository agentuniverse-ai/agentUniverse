# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03
# @Author  : agentuniverse-contributor
# @FileName: test_agent_template.py
"""Unit tests for the AgentTemplate base class."""

import pytest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.template.agent_template import AgentTemplate


class _MinimalAgentTemplate(AgentTemplate):
    """Concrete subclass exposing the abstract base template."""

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return agent_result


class TestAgentTemplate:
    """Test AgentTemplate through a minimal concrete subclass."""

    @pytest.fixture
    def agent(self) -> _MinimalAgentTemplate:
        return _MinimalAgentTemplate()

    def test_cannot_instantiate_abstract_base_directly(self):
        with pytest.raises(TypeError):
            AgentTemplate()

    def test_default_field_values(self, agent):
        assert agent.llm_name == ''
        assert agent.memory_name is None
        assert agent.knowledge_names is None
        assert agent.prompt_version is None
        assert agent.conversation_memory_name is None
        assert agent.agent_model is None

    def test_abstract_contract_delegated_to_subclass(self, agent):
        assert agent.input_keys() == ['input']
        assert agent.output_keys() == ['output']
        assert agent.parse_result({'output': 'r'}) == {'output': 'r'}
        assert agent.parse_input(InputObject({'input': 'q'}), {})['input'] == 'q'

    def test_execution_entry_points_are_defined(self, agent):
        assert callable(agent.execute)
        assert callable(agent.async_execute)
        assert callable(agent.customized_execute)

    def test_create_copy_copies_fields_into_new_instance(self, agent):
        agent.llm_name = 'demo_llm'
        agent.memory_name = 'demo_memory'
        agent.prompt_version = 'pv'
        agent.conversation_memory_name = 'cm'
        copied = agent.create_copy()
        assert copied is not agent
        assert copied.llm_name == 'demo_llm'
        assert copied.memory_name == 'demo_memory'
        assert copied.prompt_version == 'pv'
        assert copied.conversation_memory_name == 'cm'

    def test_create_copy_knowledge_names_are_independent(self, agent):
        agent.knowledge_names = ['knowledge_a']
        copied = agent.create_copy()
        assert copied.knowledge_names == ['knowledge_a']
        agent.knowledge_names.append('knowledge_b')
        assert copied.knowledge_names == ['knowledge_a']

    def test_noop_helpers_return_none(self, agent):
        assert agent.validate_required_params() is None
        assert agent.add_output_stream(None, 'output text') is None

    def test_process_memory_short_circuits_existing_chat_history(self, agent):
        assert agent.process_memory({'chat_history': 'plain history'}) is None
        agent_input = {'chat_history': [Message(type='human', content='hi')]}
        assert agent.process_memory(agent_input) is None
        assert isinstance(agent_input['chat_history'], str)
