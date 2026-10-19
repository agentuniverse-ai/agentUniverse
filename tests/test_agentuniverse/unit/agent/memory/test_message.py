# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 10:40
# @Author  : yuewang
# @FileName: test_message.py
"""Unit tests for the base Message class."""

import pytest
from langchain_core.messages import HumanMessage
from langchain_core.prompts import (
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from agentuniverse.agent.memory.message import Message


class TestMessageAsLangchain:
    """Test as_langchain mapping for each message type."""

    def test_system_message(self):
        msg = Message(type='system', content='sys')
        assert isinstance(msg.as_langchain(), SystemMessagePromptTemplate)

    def test_human_string_content(self):
        msg = Message(type='human', content='hi')
        assert isinstance(msg.as_langchain(), HumanMessagePromptTemplate)

    def test_human_list_content(self):
        msg = Message(type='human', content=[{'type': 'text', 'text': 'hi'}])
        result = msg.as_langchain()
        assert isinstance(result, HumanMessage)
        assert result.content == [{'type': 'text', 'text': 'hi'}]

    def test_ai_message(self):
        msg = Message(type='ai', content='answer')
        assert isinstance(msg.as_langchain(), AIMessagePromptTemplate)

    def test_unknown_type_raises(self):
        # unknown type falls back to the abstract prompt template base class
        msg = Message(type='robot', content='x')
        with pytest.raises(TypeError):
            msg.as_langchain()

    def test_as_langchain_list_none_and_conversion(self):
        assert Message.as_langchain_list(None) == []
        result = Message.as_langchain_list([
            Message(type='system', content='s'),
            Message(type='ai', content='a'),
        ])
        assert len(result) == 2
        assert isinstance(result[0], SystemMessagePromptTemplate)
        assert isinstance(result[1], AIMessagePromptTemplate)


class TestMessageDict:
    """Test to_dict / from_dict round trip."""

    def test_to_dict_keys(self):
        msg = Message(id='1', type='human', content='c', source='s', metadata={'k': 1})
        d = msg.to_dict()
        assert d == {'type': 'human', 'content': 'c', 'metadata': {'k': 1}, 'source': 's'}

    def test_from_dict_empty(self):
        msg = Message.from_dict({})
        assert msg.content is None
        assert msg.type is None

    def test_from_dict_role_maps_to_type(self):
        msg = Message.from_dict({'role': 'user', 'content': 'c'})
        assert msg.type == 'user'
        assert msg.content == 'c'

    def test_from_dict_ignores_unknown_keys(self):
        msg = Message.from_dict({'type': 'ai', 'content': 'c', 'weird': 'x'})
        assert not hasattr(msg, 'weird')

    def test_round_trip(self):
        msg = Message(type='ai', content='c', source='s', metadata={'m': 2})
        restored = Message.from_dict(msg.to_dict())
        assert restored == msg


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
