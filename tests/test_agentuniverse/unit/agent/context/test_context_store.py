# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for ContextStore base-class helpers."""

from datetime import datetime, timedelta
from typing import List, Optional

import pytest

from agentuniverse.agent.context.context_model import (
    ContextMetadata,
    ContextPriority,
    ContextSegment,
    ContextType,
)
from pydantic import Field

from agentuniverse.agent.context.context_store import ContextStore


class MemoryContextStore(ContextStore):
    """Minimal in-memory backend used to exercise base-class helpers."""

    sessions: dict = Field(default_factory=dict)

    def add(self, segments, **kwargs):
        key = kwargs.get("session_id", "default")
        self.sessions.setdefault(key, []).extend(segments)

    def get(self, session_id, context_type=None, limit=100, **kwargs):
        segs = list(self.sessions.get(session_id, []))
        if context_type:
            segs = [s for s in segs if s.type == context_type]
        return segs[:limit]

    def search(self, query, session_id, top_k=10, **kwargs):
        return []

    def delete(self, session_id, segment_ids=None, **kwargs):
        return None

    def prune(self, session_id, **kwargs):
        return 0


def segment(priority=ContextPriority.MEDIUM, hours_ago=0.0,
            context_type=ContextType.TASK):
    created = datetime.now() - timedelta(hours=hours_ago)
    return ContextSegment(
        type=context_type,
        priority=priority,
        content="sample content",
        tokens=4,
        metadata=ContextMetadata(created_at=created, last_accessed=created),
    )


class TestContextStore:
    """Test default helper methods implemented on the base class."""

    def test_count_uses_get_length(self):
        store = MemoryContextStore()
        store.add([segment(), segment()], session_id="s1")
        assert store.count("s1") == 2
        assert store.count("missing") == 0

    def test_metrics_enabled_reports_averages(self):
        store = MemoryContextStore(enable_metrics=True)
        store.initialize_metrics()
        store._metrics.update({"add_count": 2, "total_add_time_ms": 10.0,
                               "get_count": 4, "total_get_time_ms": 20.0})
        metrics = store.get_metrics()
        assert metrics["avg_add_time_ms"] == 5.0
        assert metrics["avg_get_time_ms"] == 5.0

    def test_is_expired_uses_ttl(self):
        store = MemoryContextStore(ttl_hours=1)
        assert store._is_expired(segment(hours_ago=5))
        assert not store._is_expired(segment(hours_ago=0))

    def test_should_prune_never_prunes_critical(self):
        store = MemoryContextStore()
        assert not store._should_prune(segment(priority=ContextPriority.CRITICAL,
                                               hours_ago=50))

    def test_should_prune_respects_priority_threshold(self):
        store = MemoryContextStore()
        low = segment(priority=ContextPriority.LOW)
        assert store._should_prune(low, min_priority=ContextPriority.MEDIUM)
        high = segment(priority=ContextPriority.HIGH)
        assert not store._should_prune(high, min_priority=ContextPriority.MEDIUM)

    def test_should_prune_respects_age_limit(self):
        store = MemoryContextStore()
        old = segment(hours_ago=10)
        assert store._should_prune(old, max_age_hours=2)
        recent = segment(hours_ago=1)
        assert not store._should_prune(recent, max_age_hours=2)
