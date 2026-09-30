# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 11:10
# @Author  : yuewang
# @FileName: test_memory_storage_manager.py
"""Unit tests for MemoryStorageManager."""

import pytest

from agentuniverse.agent.memory.memory_storage.memory_storage_manager import (
    MemoryStorageManager,
)
from agentuniverse.agent.memory.memory_storage.ram_memory_storage import RamMemoryStorage
from agentuniverse.base.component.component_enum import ComponentEnum


@pytest.fixture
def manager():
    """Return the MemoryStorageManager singleton."""
    return MemoryStorageManager()


class TestMemoryStorageManager:
    """Test MemoryStorageManager registration behavior."""

    def test_singleton(self, manager):
        assert manager is MemoryStorageManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.MEMORY_STORAGE

    def test_register_and_get(self, manager):
        storage = RamMemoryStorage()
        manager.register('app.memory_storage.s1', storage)
        assert manager.get_instance_obj('s1', appname='app', new_instance=False) is storage

    def test_get_unknown_returns_none(self, manager):
        assert manager.get_instance_obj('absent_s_xyz', appname='app') is None

    def test_get_unknown_strict_raises(self, manager):
        with pytest.raises(ValueError, match='is not registered'):
            manager.get_instance_obj('absent_s_xyz', appname='app', strict=True)

    def test_unregister(self, manager):
        manager.register('app.memory_storage.s2', RamMemoryStorage())
        manager.unregister('app.memory_storage.s2')
        assert manager.get_instance_obj('s2', appname='app') is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
