# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/02/10 10:00
# @Author  : agentuniverse
# @FileName: test_memory_storage.py
"""Unit tests for the MemoryStorage base class."""

import pytest

from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.component.component_enum import ComponentEnum


class TestMemoryStorage:
    """Test the MemoryStorage component base class."""

    @pytest.fixture
    def storage(self):
        """Create a MemoryStorage instance for testing."""
        return MemoryStorage(name='test_memory_storage', description='A test storage')

    def test_initialization(self, storage):
        """The storage stores its name and description."""
        assert storage.name == 'test_memory_storage'
        assert storage.description == 'A test storage'

    def test_default_field_values(self, storage):
        """The storage uses the memory storage component type and defaults."""
        assert storage.component_type == ComponentEnum.MEMORY_STORAGE
        assert storage.default_symbol is False
        assert storage.component_config_path is None

    def test_defaults_when_no_arguments(self):
        """All fields fall back to their defaults without arguments."""
        storage = MemoryStorage()
        assert storage.name is None
        assert storage.description is None

    def test_add_returns_none(self, storage):
        """The base add method is a no-op returning None."""
        message = Message(type='human', content='hello')
        result = storage.add([message], session_id='session_1', agent_id='agent_1')
        assert result is None

    def test_delete_returns_none(self, storage):
        """The base delete method is a no-op returning None."""
        result = storage.delete(session_id='session_1', agent_id='agent_1')
        assert result is None

    def test_get_returns_none(self, storage):
        """The base get method is a no-op returning None."""
        result = storage.get(session_id='session_1', agent_id='agent_1')
        assert result is None

    def test_create_copy_returns_self(self, storage):
        """The base storage reuses the same instance when copied."""
        assert storage.create_copy() is storage

    def test_is_default_object_false(self, storage):
        """A plain instance is never considered the default object."""
        assert storage.is_default_object() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
