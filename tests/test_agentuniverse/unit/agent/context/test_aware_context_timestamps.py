"""Regression tests for context timestamps loaded with timezone offsets."""

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from agentuniverse.agent.context.compressor.selective_compressor import SelectiveCompressor
from agentuniverse.agent.context.context_model import ContextMetadata, ContextSegment, ContextType
from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore
from agentuniverse.agent.context.store.ram_context_store import RamContextStore
from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


def segment_at(age_hours: int) -> ContextSegment:
    timestamp = datetime.now(timezone(timedelta(hours=8))) - timedelta(hours=age_hours)
    return ContextSegment(
        type=ContextType.CONVERSATION,
        content="timezone-aware history",
        tokens=3,
        metadata=ContextMetadata(created_at=timestamp, last_accessed=timestamp),
    )


def test_aware_metadata_decay_and_access_preserve_timezone():
    metadata = segment_at(12).metadata

    assert 0 < metadata.calculate_decay() < 1
    metadata.update_access()

    assert metadata.access_count == 1
    assert metadata.last_accessed.utcoffset() == timedelta(hours=8)
    assert metadata.calculate_decay() > 0.99


def test_aware_timestamp_expiration_and_pruning():
    store = RamContextStore(ttl_hours=24)
    old = segment_at(48)
    recent = segment_at(1)

    assert store._is_expired(old)
    assert not store._is_expired(recent)
    assert store._should_prune(old, max_age_hours=24)
    assert not store._should_prune(recent, max_age_hours=24)


def test_selective_compressor_scores_aware_segments():
    compressor = SelectiveCompressor()
    recent = segment_at(1)
    old = segment_at(12)

    assert compressor._score_and_sort([old, recent]) == [recent, old]


@pytest.mark.parametrize("store_type,backend_attribute", [
    (ChromaContextStore, "_collection"),
    (RedisContextStore, "_redis"),
])
def test_backend_prune_handles_aware_timestamps(store_type, backend_attribute, monkeypatch):
    store = store_type(ttl_hours=24)
    setattr(store, backend_attribute, Mock())
    old = segment_at(48)
    recent = segment_at(1)
    get = Mock(return_value=[old, recent])
    delete = Mock()
    monkeypatch.setattr(store_type, "get", get)
    monkeypatch.setattr(store_type, "delete", delete)

    assert store.prune("session") == 1
    delete.assert_called_once_with("session", segment_ids=[old.id])


def test_ram_get_sorts_mixed_naive_and_aware_timestamps():
    store = RamContextStore()
    older = segment_at(2)
    newer = ContextSegment(
        type=ContextType.CONVERSATION, content="newer", tokens=1,
        metadata=ContextMetadata(
            created_at=datetime.now() - timedelta(hours=1),
            last_accessed=datetime.now() - timedelta(hours=1),
        ),
    )
    store.add([older, newer], session_id="session")

    assert [segment.id for segment in store.get("session")] == [newer.id, older.id]


def test_ram_search_breaks_score_ties_with_mixed_timestamps():
    store = RamContextStore()
    older = ContextSegment(
        type=ContextType.CONVERSATION, content="needle", tokens=1,
        metadata=ContextMetadata(
            last_accessed=datetime.now(timezone.utc) - timedelta(hours=2),
            decay_rate=0,
        ),
    )
    newer = ContextSegment(
        type=ContextType.CONVERSATION, content="needle", tokens=1,
        metadata=ContextMetadata(
            last_accessed=datetime.now() - timedelta(hours=1), decay_rate=0,
        ),
    )
    store.add([older, newer], session_id="session")

    assert [segment.id for segment in store.search("needle", "session")] == [newer.id, older.id]


def test_redis_get_sorts_mixed_naive_and_aware_timestamps():
    store = RedisContextStore()
    older = segment_at(2)
    newer = ContextSegment(
        type=ContextType.CONVERSATION, content="newer", tokens=1,
        metadata=ContextMetadata(created_at=datetime.now() - timedelta(hours=1)),
    )
    store._redis = Mock()
    store._redis.hgetall.return_value = {
        segment.id.encode(): store._serialize_segment(segment)
        for segment in (older, newer)
    }

    assert [segment.id for segment in store.get("session")] == [newer.id, older.id]


def test_chroma_get_sorts_mixed_naive_and_aware_timestamps():
    store = ChromaContextStore()
    older = segment_at(2)
    newer = ContextSegment(
        type=ContextType.CONVERSATION, content="newer", tokens=1,
        metadata=ContextMetadata(created_at=datetime.now() - timedelta(hours=1)),
    )
    store._collection = Mock()
    store._collection.get.return_value = {
        "ids": [older.id, newer.id],
        "documents": [older.content, newer.content],
        "metadatas": [
            {
                "segment_id": segment.id,
                "type": segment.type.value,
                "priority": segment.priority.value,
                "tokens": segment.tokens,
                "created_at": segment.metadata.created_at.isoformat(),
                "last_accessed": segment.metadata.last_accessed.isoformat(),
                "access_count": 0,
                "relevance_score": 1.0,
                "decay_rate": 0.1,
                "session_id": "session",
            }
            for segment in (older, newer)
        ],
    }

    assert [segment.id for segment in store.get("session")] == [newer.id, older.id]
