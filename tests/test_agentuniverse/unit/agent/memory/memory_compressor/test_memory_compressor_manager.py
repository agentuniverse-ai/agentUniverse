# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_memory_compressor_manager.py
"""Unit tests for the singleton MemoryCompressorManager."""

import pytest

from agentuniverse.agent.memory.memory_compressor.memory_compressor import MemoryCompressor
from agentuniverse.agent.memory.memory_compressor.memory_compressor_manager import MemoryCompressorManager
from agentuniverse.base.component.component_enum import ComponentEnum


class TestMemoryCompressorManager:
    """Test the MemoryCompressorManager singleton and its component pool."""

    @pytest.fixture
    def manager(self):
        """Provide the manager singleton and restore its pool afterwards."""
        mgr = MemoryCompressorManager()
        before = set(mgr.get_instance_name_list())
        yield mgr
        for name in set(mgr.get_instance_name_list()) - before:
            mgr.unregister(name)

    @pytest.fixture
    def compressor(self):
        """Create an offline MemoryCompressor instance for registration."""
        return MemoryCompressor(name="test_compressor")

    def test_singleton_returns_same_instance(self):
        """Repeated access returns the same shared manager object."""
        assert MemoryCompressorManager() is MemoryCompressorManager()

    def test_default_state(self, manager):
        """A fresh manager is empty and manages memory compressors."""
        assert manager.get_instance_name_list() == []
        assert manager._component_type == ComponentEnum.MEMORY_COMPRESSOR

    def test_get_instance_obj_missing(self, manager):
        """Unregistered compressors resolve to None, or raise when strict."""
        assert manager.get_instance_obj("missing", appname="unit_app") is None
        with pytest.raises(ValueError) as exc:
            manager.get_instance_obj("missing", appname="unit_app", strict=True)
        assert "missing" in str(exc.value)
        assert ComponentEnum.MEMORY_COMPRESSOR.value in str(exc.value)

    def test_register_and_unregister(self, manager, compressor):
        """register()/unregister() keep the instance pool consistent."""
        manager.register("my_compressor", compressor)
        assert manager.get_instance_name_list() == ["my_compressor"]
        assert manager.get_instance_obj_list() == [compressor]
        manager.unregister("my_compressor")
        assert manager.get_instance_name_list() == []

    def test_duplicate_registration_keeps_original(self, manager, compressor):
        """Registering an existing name again does not replace it."""
        manager.register("dup_compressor", compressor)
        manager.register("dup_compressor", MemoryCompressor(name="other"))
        assert manager.get_instance_name_list() == ["dup_compressor"]
        assert manager.get_instance_obj_list() == [compressor]

    def test_default_symbol_registers_default_instance(self, manager, compressor):
        """A default compressor is exposed via get_default_instance."""
        default_compressor = MemoryCompressor(name="default_compressor", default_symbol=True)
        manager.register("default_compressor", default_compressor)
        assert manager.get_default_instance() is default_compressor
        copied = manager.get_default_instance(new_instance=True)
        assert copied is not default_compressor
        assert copied.name == default_compressor.name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
