# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_chat_memory.py
"""Unit tests for ChatMemory."""

import pytest

from agentuniverse.agent.memory import memory as memory_module
from agentuniverse.agent.memory.chat_memory import ChatMemory
from agentuniverse.agent.memory.message import Message


class TestChatMemory:
    """Test ChatMemory implementation."""

    @pytest.fixture
    def chat_memory(self):
        """Create a ChatMemory instance for testing."""
        return ChatMemory()

    @pytest.fixture
    def sample_messages(self):
        """Create sample conversation messages."""
        return [
            Message(type='human', content='Hi, my name is Edwin'),
            Message(type='ai', content='Hello Edwin, nice to meet you.'),
        ]

    def test_default_attributes(self, chat_memory):
        """Test the default field values of ChatMemory."""
        assert chat_memory.llm is None
        assert chat_memory.input_key == 'input'
        assert chat_memory.output_key == 'output'
        assert chat_memory.messages is None
        assert chat_memory.memory_key == 'chat_history'

    def test_add_and_get_round_trip(self, chat_memory, sample_messages, monkeypatch):
        """Test messages added can be fetched back via get."""
        monkeypatch.setattr(memory_module, 'get_memory_tokens',
                            lambda memories, agent_llm_name=None: 3)
        chat_memory.add(sample_messages)
        assert chat_memory.messages == sample_messages
        assert chat_memory.get() == sample_messages

    def test_add_empty_list_is_noop(self, chat_memory, sample_messages):
        """Test adding an empty list keeps the existing messages."""
        chat_memory.add(sample_messages)
        chat_memory.add([])
        assert chat_memory.messages == sample_messages

    def test_get_without_messages_returns_empty(self, chat_memory):
        """Test getting from an empty memory returns an empty list."""
        assert chat_memory.get() == []

    def test_set_by_agent_model(self, chat_memory):
        """Test set_by_agent_model updates a copy and keeps falsy defaults."""
        copy = chat_memory.set_by_agent_model(memory_key='history', input_key='query',
                                              output_key='', max_tokens=1024)
        assert copy.memory_key == 'history'
        assert copy.input_key == 'query'
        assert copy.output_key == 'output'
        assert copy.max_tokens == 1024
        assert copy is not chat_memory
        assert chat_memory.memory_key == 'chat_history'
        assert chat_memory.input_key == 'input'

    def test_as_langchain_without_llm_raises(self, chat_memory):
        """Test as_langchain requires a configured llm."""
        with pytest.raises(ValueError, match="Must set `llm`"):
            chat_memory.as_langchain()
