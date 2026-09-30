# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 14:10
# @Author  : yuewang
# @FileName: test_context_store_manager.py
"""Unit tests for ContextStoreManager."""

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.context_store import ContextStore
from agentuniverse.agent.context.context_store_manager import ContextStoreManager


class MiniStore(ContextStore):
    """Minimal concrete store for manager tests."""

    def add(self, segments, **kwargs):
        pass

    def get(self, session_id, context_type=None, limit=100, **kwargs):
        return []

    def search(self, query, session_id, top_k=10, **kwargs):
        return []

    def delete(self, session_id, segment_ids=None, **kwargs):
        pass

    def prune(self, session_id, **kwargs):
        return 0


@pytest.fixture
def manager():
    """Return the ContextStoreManager."""
    return ContextStoreManager()


class TestContextStoreManager:
    """Test ContextStoreManager registration behavior."""

    def test_instantiation(self, manager):
        assert isinstance(manager, ContextStoreManager)

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.CONTEXT_STORE

    def test_register_and_get(self, manager):
        store = MiniStore(name='mini_store')
        manager.register('app.context_store.mini_store', store)
        assert manager.get_instance_obj('mini_store', appname='app',
                                        new_instance=False) is store

    def test_get_unknown_returns_none(self, manager):
        assert manager.get_instance_obj('absent_store_xyz', appname='app') is None

    def test_unregister(self, manager):
        manager.register('app.context_store.gone', MiniStore(name='gone'))
        manager.unregister('app.context_store.gone')
        assert manager.get_instance_obj('gone', appname='app') is None
