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
