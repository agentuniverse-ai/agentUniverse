# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_langchain_instance.py
"""Unit tests for the AuConversation*BufferMemory langchain adapters."""

import pytest
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from agentuniverse.agent.memory.langchain_instance import (
    AuConversationSummaryBufferMemory,
    AuConversationTokenBufferMemory,
)
from agentuniverse.agent.memory.message import Message


class _CountingLLM:
    def get_num_tokens_from_messages(self, messages):
        return sum(len(m.content) for m in messages)


def _build(kind, messages=None):
    """Build one of the Au langchain memory adapters offline."""
    cls = AuConversationSummaryBufferMemory if kind == 'summary' else AuConversationTokenBufferMemory
    return cls.construct(llm=_CountingLLM(), chat_memory=InMemoryChatMessageHistory(),
                         input_key='input', output_key='output', memory_key='chat_history',
                         max_token_limit=2000, messages=messages)


class TestAuConversationMemory:
    """Test the AuConversation langchain memory adapters."""

    @pytest.fixture
    def conversation_messages(self):
        """Create system/human/ai messages for memory building."""
        return [Message(type='system', content='You are a helpful assistant.'),
                Message(type='human', content='What is my name?'),
                Message(type='ai', content='Your name is Edwin.')]

    def test_token_buffer_discards_system_message(self, conversation_messages):
        """Test the token buffer drops the system message."""
        memory = _build('token', messages=list(conversation_messages))
        memory.build_memory()
        assert [m.type for m in memory.chat_memory.messages] == ['human', 'ai']
        assert memory.messages == conversation_messages[1:]
        assert memory.load_memory_str == 'Human: What is my name?\nAI: Your name is Edwin.'

    def test_empty_memory_is_inert(self):
        """Test empty memories stay empty after building."""
        token, summary = _build('token'), _build('summary')
        token.build_memory()
        summary.build_memory()
        assert token.load_memory == []
        assert token.load_memory_str == ''
        assert summary.moving_summary_buffer == ''

    def test_summary_buffer_moves_system_to_summary(self, conversation_messages):
        """Test the summary buffer keeps the system message as summary."""
        memory = _build('summary', messages=list(conversation_messages))
        memory.build_memory()
        assert memory.moving_summary_buffer == 'You are a helpful assistant.'
        assert memory.messages == conversation_messages[1:]
        loaded = memory.load_memory
        assert isinstance(loaded[0], SystemMessage)
        assert isinstance(loaded[1], HumanMessage)
        assert isinstance(loaded[2], AIMessage)

    def test_generate_chat_messages(self):
        """Test generate_chat_messages builds input/output dicts."""
        human, ai = _build('token').generate_chat_messages(
            Message(type='human', content='Hi'), Message(type='ai', content='Hello'))
        assert human == {'input': 'Hi'}
        assert ai == {'output': 'Hello'}
        human, ai = _build('summary').generate_chat_messages(
            Message(type='system', content='sys'), Message(type='HUMAN', content='Yo'),
            Message(type='ai', content='Hi'))
        assert human == {'input': 'Yo'}
        assert ai == {'output': 'Hi'}

    def test_save_context_updates_inputs(self):
        """Test save_context stores message dicts under the memory key."""
        memory = _build('summary')
        inputs = {'input': 'Hi there'}
        memory.save_context(inputs, {'output': 'Hello'})
        assert inputs['chat_history'] == [{'content': 'Hi there', 'type': 'human'},
                                          {'content': 'Hello', 'type': 'ai'}]
