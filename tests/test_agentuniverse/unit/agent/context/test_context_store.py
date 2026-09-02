# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 14:05
# @Author  : yuewang
# @FileName: test_context_store.py
"""Unit tests for the ContextStore base class."""

import pytest
from datetime import datetime, timedelta
from typing import List

from agentuniverse.agent.context.context_model import (
    ContextPriority,
    ContextSegment,
    ContextType,
)
from agentuniverse.agent.context.context_store import ContextStore


def _segment(priority=ContextPriority.MEDIUM, created_at=None):
    return ContextSegment(
        type=ContextType.CONVERSATION, priority=priority,
        content='hello', tokens=1,
        metadata={'created_at': created_at or datetime.now(),
                  'last_accessed': datetime.now(), 'relevance_score': 1.0})


class RamStore(ContextStore):
    """In-memory ContextStore for exercising base implementations."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data = {}

    def add(self, segments, **kwargs):
        sid = kwargs.get('session_id', 's')
        self._data.setdefault(sid, []).extend(segments)

    def get(self, session_id, context_type=None, limit=100, **kwargs):
        return self._data.get(session_id, [])[:limit]

    def search(self, query, session_id, top_k=10, **kwargs):
        return self.get(session_id, limit=top_k)

    def delete(self, session_id, segment_ids=None, **kwargs):
        self._data.pop(session_id, None)

    def prune(self, session_id, **kwargs):
        return 0


class TestContextStore:
    """Test ContextStore defaults, metrics, and pruning helpers."""

    def test_defaults(self):
        store = RamStore()
        assert (store.storage_tier, store.max_segments, store.ttl_hours) == ('warm', 1000, 24)
        assert store.enable_metrics is False

    def test_initialize_metrics(self):
        store = RamStore()
        store.initialize_metrics()
        assert set(store._metrics) >= {'add_count', 'get_count', 'search_count', 'prune_count'}

    def test_get_metrics_disabled_or_averages(self):
        store = RamStore()
        store.initialize_metrics()
        assert store.get_metrics() == {}
        store.enable_metrics = True
        store._metrics['add_count'] = 2
        store._metrics['total_add_time_ms'] = 10.0
        metrics = store.get_metrics()
        assert metrics['avg_add_time_ms'] == 5.0
        assert 'avg_get_time_ms' not in metrics

    def test_is_expired(self):
        store = RamStore()
        old = datetime.now() - timedelta(hours=48)
        assert store._is_expired(_segment(created_at=old)) is True
        assert store._is_expired(_segment()) is False
        store.ttl_hours = 0
        assert store._is_expired(_segment(created_at=old)) is False

    def test_should_prune_rules(self):
        store = RamStore()
        assert store._should_prune(_segment(ContextPriority.CRITICAL)) is False
        assert store._should_prune(_segment(ContextPriority.LOW),
                                   min_priority=ContextPriority.HIGH) is True
        assert store._should_prune(_segment(created_at=datetime.now() - timedelta(hours=48))) is True
