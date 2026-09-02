# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 11:00
# @Author  : yuewang
# @FileName: test_memory_manager.py
"""Unit tests for MemoryManager."""

import pytest

from agentuniverse.agent.memory.memory_manager import MemoryManager
from agentuniverse.agent.memory.memory_storage.ram_memory_storage import RamMemoryStorage
from agentuniverse.base.component.component_enum import ComponentEnum


@pytest.fixture
def manager():
    """Return the MemoryManager singleton."""
    return MemoryManager()


class TestMemoryManager:
    """Test MemoryManager registration behavior."""

    def test_singleton(self, manager):
        assert manager is MemoryManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.MEMORY

    def test_register_and_get(self, manager):
        storage = RamMemoryStorage()
        code = 'app.memory.mem1'
        manager.register(code, storage)
        assert manager.get_instance_obj('mem1', appname='app', new_instance=False) is storage

    def test_get_unknown_returns_none(self, manager):
        assert manager.get_instance_obj('definitely_absent_xyz', appname='app') is None

    def test_get_unknown_strict_raises(self, manager):
        with pytest.raises(ValueError, match='is not registered'):
            manager.get_instance_obj('definitely_absent_xyz', appname='app', strict=True)

    def test_unregister(self, manager):
        code = 'app.memory.mem2'
        manager.register(code, RamMemoryStorage())
        manager.unregister(code)
        assert manager.get_instance_obj('mem2', appname='app') is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
