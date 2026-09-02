# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/02/10 10:00
# @Author  : agentuniverse
# @FileName: test_memory_storage_manager.py
"""Unit tests for the singleton MemoryStorageManager."""

import pytest

from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.agent.memory.memory_storage.memory_storage_manager import (
    MemoryStorageManager,
)


@pytest.fixture
def manager():
    """Return the shared manager and roll back names added by the test."""
    mgr = MemoryStorageManager()
    original_names = set(mgr.get_instance_name_list())
    yield mgr
    for name in list(mgr.get_instance_name_list()):
        if name not in original_names:
            mgr.unregister(name)


class TestMemoryStorageManager:
    """Test the memory storage component manager."""

    def test_singleton_returns_same_instance(self):
        """Two instantiations return the identical singleton object."""
        assert MemoryStorageManager() is MemoryStorageManager()

    def test_initial_instance_list_empty(self, manager):
        """A fresh manager starts without registered components."""
        assert manager.get_instance_name_list() == []

    def test_register_component(self, manager):
        """Registering a storage adds its name to the manager."""
        storage = MemoryStorage(name='mem_a', description='storage a')
        manager.register('mem_a', storage)
        assert 'mem_a' in manager.get_instance_name_list()
        assert manager._instance_obj_map['mem_a'] is storage

    def test_register_duplicate_name_keeps_first(self, manager):
        """Registering a second object under an existing name is a no-op."""
        first = MemoryStorage(name='mem_b')
        second = MemoryStorage(name='mem_b')
        manager.register('mem_b', first)
        manager.register('mem_b', second)
        assert manager._instance_obj_map['mem_b'] is first
        assert manager.get_instance_name_list().count('mem_b') == 1

    def test_register_default_symbol_adds_default_instance(self, manager):
        """Registering a default storage also registers the default slot."""
        storage = MemoryStorage(name='mem_c', default_symbol=True)
        manager.register('mem_c', storage)
        assert 'mem_c' in manager.get_instance_name_list()
        assert '__default_instance__' in manager.get_instance_name_list()

    def test_unregister_removes_component(self, manager):
        """Unregistering removes the component name from the manager."""
        manager.register('mem_d', MemoryStorage(name='mem_d'))
        assert 'mem_d' in manager.get_instance_name_list()
        manager.unregister('mem_d')
        assert 'mem_d' not in manager.get_instance_name_list()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
