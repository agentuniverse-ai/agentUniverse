# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_message.py
"""Unit tests for the Message data model."""

import pytest

from langchain_core.messages import HumanMessage
from langchain_core.prompts.chat import (
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from agentuniverse.agent.memory.message import Message


class TestMessage:
    """Test the Message data model and its conversions."""

    def test_default_field_values(self):
        """Test all Message fields default to None."""
        message = Message()
        assert message.id is None
        assert message.type is None
        assert message.content is None
        assert message.source is None
        assert message.metadata is None

    def test_to_dict_returns_expected_keys(self):
        """Test to_dict serialises the meaningful fields."""
        message = Message(type='human', content='hello', source='test', metadata={'k': 'v'})
        assert message.to_dict() == {
            'type': 'human', 'content': 'hello', 'metadata': {'k': 'v'}, 'source': 'test'}

    def test_from_dict_round_trip(self):
        """Test a message survives a dict round trip."""
        message = Message(type='ai', content='hello', source='source_a', metadata={'m': 1})
        assert Message.from_dict(message.to_dict()) == message

    def test_from_dict_maps_role_to_type(self):
        """Test the role key is mapped onto the type field."""
        restored = Message.from_dict({'id': '1', 'role': 'user', 'content': 'question',
                                      'source': 's', 'metadata': {'a': 1}})
        assert restored.type == 'user'
        assert restored.id == '1'
        assert restored.content == 'question'
        assert restored.source == 's'
        assert restored.metadata == {'a': 1}

    def test_from_dict_none_or_empty_returns_default(self):
        """Test empty or missing dicts produce a default message."""
        assert Message.from_dict(None) == Message()
        assert Message.from_dict({}) == Message()

    def test_as_langchain_templates(self):
        """Test type based conversion to langchain prompt templates."""
        system = Message(type='system', content='be nice').as_langchain()
        assert isinstance(system, SystemMessagePromptTemplate)
        assert system.prompt.template == 'be nice'
        human = Message(type='human', content='hi').as_langchain()
        assert isinstance(human, HumanMessagePromptTemplate)
        assert human.prompt.template == 'hi'
        ai = Message(type='ai', content='yo').as_langchain()
        assert isinstance(ai, AIMessagePromptTemplate)
        assert ai.prompt.template == 'yo'

    def test_as_langchain_human_list_content(self):
        """Test human list content becomes a langchain HumanMessage."""
        content = [{'type': 'text', 'text': 'a'}, {'type': 'text', 'text': 'b'}]
        converted = Message(type='human', content=content).as_langchain()
        assert isinstance(converted, HumanMessage)
        assert converted.content == content

    def test_as_langchain_list(self):
        """Test converting a whole message list, including None."""
        assert Message.as_langchain_list(None) == []
        converted = Message.as_langchain_list([
            Message(type='system', content='s'), Message(type='human', content='h')])
        assert len(converted) == 2
        assert isinstance(converted[0], SystemMessagePromptTemplate)
        assert isinstance(converted[1], HumanMessagePromptTemplate)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
