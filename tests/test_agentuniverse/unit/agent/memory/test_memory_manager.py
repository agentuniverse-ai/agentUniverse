# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_memory_manager.py
"""Unit tests for MemoryManager."""

import pytest
from types import SimpleNamespace

from agentuniverse.agent.memory.memory_manager import MemoryManager
from agentuniverse.base.component.component_enum import ComponentEnum


class TestMemoryManager:
    """Test the MemoryManager singleton manager."""

    @pytest.fixture(autouse=True)
    def clean_manager(self):
        """Reset the shared singleton pool before and after each test."""
        manager = MemoryManager()
        manager._instance_obj_map.clear()
        yield manager
        manager._instance_obj_map.clear()

    @staticmethod
    def _make_component(name='test_memory', default_symbol=False):
        """Create a lightweight fake memory component."""
        return SimpleNamespace(name=name, component_type=ComponentEnum.MEMORY,
                               component_config_path=None, default_symbol=default_symbol)

    def test_singleton_returns_same_instance(self):
        """Test MemoryManager behaves as a singleton."""
        assert MemoryManager() is MemoryManager()

    def test_initial_state(self, clean_manager):
        """Test the initial component type and empty component pool."""
        assert clean_manager._component_type == ComponentEnum.MEMORY
        assert clean_manager._instance_obj_map == {}

    def test_register_adds_component(self, clean_manager):
        """Test registering a component stores it in the pool."""
        component = self._make_component('my_memory')
        clean_manager.register('my_memory', component)
        assert clean_manager._instance_obj_map['my_memory'] is component

    def test_register_default_component(self, clean_manager):
        """Test a default component is also stored under the default key."""
        component = self._make_component(default_symbol=True)
        clean_manager.register('my_memory', component)
        assert clean_manager._instance_obj_map['__default_instance__'] is component

    def test_register_duplicate_keeps_first(self, clean_manager):
        """Test registering a duplicate name does not overwrite the first one."""
        first = self._make_component('dup')
        second = self._make_component('dup')
        clean_manager.register('dup', first)
        clean_manager.register('dup', second)
        assert clean_manager._instance_obj_map['dup'] is first

    def test_unregister_removes_component(self, clean_manager):
        """Test unregistering removes the component from the pool."""
        component = self._make_component()
        clean_manager.register('my_memory', component)
        clean_manager.unregister('my_memory')
        assert 'my_memory' not in clean_manager._instance_obj_map
