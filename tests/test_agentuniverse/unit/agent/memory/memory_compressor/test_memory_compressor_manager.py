# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 11:05
# @Author  : yuewang
# @FileName: test_memory_compressor_manager.py
"""Unit tests for MemoryCompressorManager."""

import pytest

from agentuniverse.agent.memory.memory_compressor.memory_compressor import MemoryCompressor
from agentuniverse.agent.memory.memory_compressor.memory_compressor_manager import (
    MemoryCompressorManager,
)
from agentuniverse.base.component.component_enum import ComponentEnum


@pytest.fixture
def manager():
    """Return the MemoryCompressorManager singleton."""
    return MemoryCompressorManager()


class TestMemoryCompressorManager:
    """Test MemoryCompressorManager registration behavior."""

    def test_singleton(self, manager):
        assert manager is MemoryCompressorManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.MEMORY_COMPRESSOR

    def test_register_and_get(self, manager):
        compressor = MemoryCompressor(name='c1')
        manager.register('app.memory_compressor.c1', compressor)
        assert manager.get_instance_obj('c1', appname='app', new_instance=False) is compressor

    def test_get_unknown_returns_none(self, manager):
        assert manager.get_instance_obj('absent_c_xyz', appname='app') is None

    def test_get_unknown_strict_raises(self, manager):
        with pytest.raises(ValueError, match='is not registered'):
            manager.get_instance_obj('absent_c_xyz', appname='app', strict=True)

    def test_unregister(self, manager):
        manager.register('app.memory_compressor.c2', MemoryCompressor(name='c2'))
        manager.unregister('app.memory_compressor.c2')
        assert manager.get_instance_obj('c2', appname='app') is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
