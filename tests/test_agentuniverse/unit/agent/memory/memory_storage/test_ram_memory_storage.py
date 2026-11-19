# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/02/10 10:00
# @Author  : agentuniverse
# @FileName: test_ram_memory_storage.py
"""Unit tests for the in-memory RamMemoryStorage."""

import pytest

from agentuniverse.agent.memory.memory_storage.ram_memory_storage import RamMemoryStorage
from agentuniverse.agent.memory.message import Message


@pytest.fixture
def storage():
    """A fresh storage with isolated message buckets."""
    instance = RamMemoryStorage()
    instance.messages = {}
    return instance


@pytest.fixture
def messages():
    """Sample messages used across the tests."""
    return [
        Message(type='human', content='hello'),
        Message(type='ai', content='hi there'),
        Message(type='human', content='again'),
    ]


class TestRamMemoryStorage:
    """Test the RamMemoryStorage implementation."""

    def test_initial_state_empty(self, storage):
        assert storage.messages == {}
        assert storage.get('session_1', 'agent_1') == []

    def test_add_and_get_roundtrip(self, storage, messages):
        """Messages added for a session/agent are returned in order."""
        storage.add(messages, session_id='session_1', agent_id='agent_1')
        retrieved = storage.get('session_1', 'agent_1')
        assert retrieved == messages
        assert retrieved[0] is messages[0]

    def test_messages_nested_by_session_then_agent(self, storage, messages):
        storage.add(messages[:1], session_id='session_1', agent_id='agent_1')
        storage.add(messages[1:], session_id='session_1', agent_id='agent_2')
        assert storage.messages['session_1']['agent_1'] == messages[:1]
        assert storage.messages['session_1']['agent_2'] == messages[1:]
        # buckets are isolated from each other
        assert storage.get('session_1', 'agent_1') == messages[:1]

    def test_add_appends_to_existing_bucket(self, storage, messages):
        storage.add(messages[:1], session_id='session_1', agent_id='agent_1')
        storage.add(messages[1:], session_id='session_1', agent_id='agent_1')
        assert storage.get('session_1', 'agent_1') == messages

    def test_top_k_returns_last_messages(self, storage):
        """top_k slicing returns only the most recent messages."""
        added = [Message(type='human', content=f'msg {i}') for i in range(5)]
        storage.add(added, session_id='session_1', agent_id='agent_1')
        assert storage.get('session_1', 'agent_1', top_k=3) == added[-3:]
        assert storage.get('session_1', 'agent_1') == added

    def test_add_empty_list_is_noop(self, storage):
        storage.add([], session_id='session_1', agent_id='agent_1')
        assert storage.messages == {}
        assert storage.get('session_1', 'agent_1') == []

    def test_delete_removes_whole_session(self, storage, messages):
        """Deleting with only a session_id removes every bucket of it."""
        storage.add(messages, session_id='session_1', agent_id='agent_1')
        storage.add(messages, session_id='session_1', agent_id='agent_2')
        storage.add(messages, session_id='session_2', agent_id='agent_1')
        storage.delete(session_id='session_1')
        assert 'session_1' not in storage.messages
        assert storage.get('session_2', 'agent_1') == messages

    def test_delete_single_agent_bucket(self, storage, messages):
        """Deleting with an agent_id removes only that agent's bucket."""
        storage.add(messages, session_id='session_1', agent_id='agent_1')
        storage.add(messages, session_id='session_1', agent_id='agent_2')
        storage.delete(session_id='session_1', agent_id='agent_1')
        assert storage.get('session_1', 'agent_1') == []
        assert storage.get('session_1', 'agent_2') == messages

