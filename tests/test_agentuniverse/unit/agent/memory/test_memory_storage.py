# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 10:55
# @Author  : yuewang
# @FileName: test_memory_storage.py
"""Unit tests for the MemoryStorage base class."""

import pytest

from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.component.component_enum import ComponentEnum


@pytest.fixture
def storage():
    """Create a bare MemoryStorage instance."""
    return MemoryStorage()


class TestMemoryStorage:
    """Test the abstract MemoryStorage contract."""

    def test_component_type(self, storage):
        assert storage.component_type == ComponentEnum.MEMORY_STORAGE

    def test_defaults(self, storage):
        assert storage.name is None
        assert storage.description is None

    def test_initialize_by_component_configer(self):
        config = type('C', (), {'name': 'ms1', 'description': 'd1',
                                'extra_attr': 'ignored'})()
        storage = MemoryStorage()
        result = storage._initialize_by_component_configer(config)
        assert result is storage
        assert storage.name == 'ms1'
        assert storage.description == 'd1'

    def test_initialize_ignores_missing_attrs(self):
        storage = MemoryStorage(name='keep')
        storage._initialize_by_component_configer(type('C', (), {})())
        assert storage.name == 'keep'
        assert storage.description is None

    def test_base_add_delete_get_are_noops(self, storage):
        assert storage.add([Message(type='human', content='c')], 's1', 'a1') is None
        assert storage.delete('s1', 'a1') is None
        assert storage.get('s1', 'a1') is None

    def test_create_copy_returns_self(self, storage):
        assert storage.create_copy() is storage

    def test_subclass_override(self):
        class InMem(MemoryStorage):
            stored: list = []

            def add(self, message_list, session_id=None, agent_id=None, **kwargs):
                self.stored.extend(message_list)

            def get(self, session_id=None, agent_id=None, top_k=10, **kwargs):
                return self.stored[-top_k:]

        sub = InMem()
        sub.add([Message(type='human', content='x')], 's')
        assert [m.content for m in sub.get('s', top_k=5)] == ['x']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
