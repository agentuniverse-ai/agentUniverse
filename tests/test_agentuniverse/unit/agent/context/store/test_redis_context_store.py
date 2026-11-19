# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/04 15:00
# @Author  : kaichuan
# @FileName: test_redis_context_store.py
"""Unit tests for RedisContextStore (offline, in-memory fake Redis)."""

import json

import pytest

from agentuniverse.agent.context.context_model import (
    ContextMetadata, ContextPriority, ContextSegment, ContextType)
from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


class _FakeRedis:
    """In-memory stand-in for the redis client used by the store."""

    def __init__(self):
        self.data = {}

    def hset(self, key, field, value):
        self.data.setdefault(key, {})[field] = value

    def hgetall(self, key):
        return self.data.get(key, {})

    def hdel(self, key, *fields):
        for field in fields:
            self.data.get(key, {}).pop(field, None)

    def hlen(self, key):
        return len(self.data.get(key, {}))

    def hmget(self, key, fields):
        bucket = self.data.get(key, {})
        return [bucket.get(field) for field in fields]

    def delete(self, *keys):
        for key in keys:
            self.data.pop(key, None)

    def expire(self, key, ttl): pass

    def zadd(self, key, mapping): pass

    def zrem(self, key, *fields): pass


def _segment(content="Redis warm storage", **kw):
    data = dict(type=ContextType.BACKGROUND, priority=ContextPriority.HIGH,
                content=content, tokens=len(content.split()), session_id="s1")
    data.update(kw)
    return ContextSegment(**data)


class TestRedisContextStore:
    """Test defaults, keys, serialization and CRUD against fake Redis."""

    @pytest.fixture
    def backend(self):
        return RedisContextStore()

    @pytest.fixture
    def store(self):
        store = RedisContextStore()
        store._redis = _FakeRedis()
        return store

    def test_defaults_and_key_generation(self, backend):
        assert backend.storage_tier == "warm"
        assert backend.redis_host == "localhost" and backend.redis_port == 6379
        assert backend.redis_db == 0 and backend.redis_password is None
        assert backend.key_prefix == "agentuniverse:context:"
        assert backend.default_ttl_seconds == 86400 and backend._redis is None
        assert backend._make_session_key("s1") == "agentuniverse:context:session:s1"
        assert backend._make_index_key("s1") == "agentuniverse:context:index:s1"

    def test_serialize_deserialize_roundtrip(self, backend):
        segment = _segment(metadata=ContextMetadata(custom={"knowledge_id": "doc1"}))
        blob = backend._serialize_segment(segment)
        assert isinstance(blob, bytes)
        assert json.loads(blob.decode("utf-8"))["content"] == segment.content
        parsed = backend._deserialize_segment(blob)
        assert parsed.id == segment.id
        assert parsed.type == ContextType.BACKGROUND
        assert parsed.priority == ContextPriority.HIGH
        assert parsed.tokens == 3 and parsed.session_id == "s1"
        assert parsed.metadata.custom["knowledge_id"] == "doc1"

    def test_add_guard_conditions(self, store, backend):
        with pytest.raises(ValueError, match="session_id is required"):
            store.add([_segment()])
        with pytest.raises(RuntimeError, match="not initialized"):
            backend.add([_segment()], session_id="s1")

    def test_add_get_filter_and_limit(self, store):
        store.add([_segment(), _segment("short chat", type=ContextType.CONVERSATION,
                                        priority=ContextPriority.LOW)], session_id="s1")
        all_segments = store.get("s1")
        assert len(all_segments) == 2
        assert {s.content for s in all_segments} == {"Redis warm storage", "short chat"}
        conversations = store.get("s1", context_type=ContextType.CONVERSATION)
        assert len(conversations) == 1 and conversations[0].content == "short chat"
        assert len(store.get("s1", limit=1)) == 1

    def test_get_by_ids_count_and_delete(self, store):
        segment = _segment()
        store.add([segment], session_id="s1")
        assert store.count("s1") == 1
        assert store.get_by_ids("s1", [segment.id])[0].content == segment.content
        assert store.get_by_ids("s1", ["missing"]) == []
        store.delete("s1", segment_ids=[segment.id])
        assert store.count("s1") == 0
        store.add([segment], session_id="s1")
        store.delete("s1")
        assert store.count("s1") == 0

    def test_empty_results_when_uninitialized(self, backend):
        assert backend.get("s1") == []
        assert backend.search("query", "s1") == []
        assert backend.get_by_ids("s1", ["id1"]) == []
        assert backend.count("s1") == 0
        assert backend.prune("s1") == 0
        assert backend.get_all_sessions() == []
        assert backend.delete("s1") is None
        assert backend.clear_all() is None
