# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 10:30
# @Author  : yuewang
# @FileName: test_ram_memory_storage.py
"""Unit tests for RamMemoryStorage."""

import pytest

from agentuniverse.agent.memory.memory_storage.ram_memory_storage import RamMemoryStorage
from agentuniverse.agent.memory.message import Message


@pytest.fixture
def storage():
    """Create an empty RamMemoryStorage for testing."""
    return RamMemoryStorage()


@pytest.fixture
def messages():
    """Create sample messages."""
    return [
        Message(type='human', content='hello', source='user'),
        Message(type='ai', content='hi there', source='assistant'),
        Message(type='human', content='bye', source='user'),
    ]


class TestRamMemoryStorage:
    """Test add/get/delete behavior of RamMemoryStorage."""

    def test_add_and_get(self, storage, messages):
        storage.add(messages, session_id='s1', agent_id='a1')
        result = storage.get('s1', 'a1')
        assert [m.content for m in result] == ['hello', 'hi there', 'bye']

    def test_get_returns_last_top_k(self, storage, messages):
        storage.add(messages, session_id='s1', agent_id='a1')
        result = storage.get('s1', 'a1', top_k=2)
        assert [m.content for m in result] == ['hi there', 'bye']

    def test_add_empty_list_is_noop(self, storage):
        storage.add([], session_id='s1', agent_id='a1')
        assert storage.messages == {}

    def test_add_multiple_agents_same_session(self, storage, messages):
        storage.add(messages, session_id='s1', agent_id='a1')
        storage.add(messages, session_id='s1', agent_id='a2')
        assert set(storage.messages['s1'].keys()) == {'a1', 'a2'}
        assert len(storage.get('s1', 'a2')) == 3

    def test_get_unknown_session_returns_empty(self, storage):
        assert storage.get('nope', 'a1') == []

    def test_delete_session_and_agent(self, storage, messages):
        storage.add(messages, session_id='s1', agent_id='a1')
        storage.add(messages, session_id='s1', agent_id='a2')
        storage.delete('s1', 'a1')
        assert 'a1' not in storage.messages['s1']
        assert len(storage.get('s1', 'a2')) == 3

    def test_delete_whole_session(self, storage, messages):
        storage.add(messages, session_id='s1', agent_id='a1')
        storage.delete('s1')
        assert 's1' not in storage.messages

    def test_delete_unknown_session_is_noop(self, storage):
        storage.delete('ghost', 'a1')
        assert storage.messages == {}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
