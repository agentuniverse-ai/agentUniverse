"""Budget maintenance must not use the default 100-item retrieval page."""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.context_model import (
    ContextMetadata,
    ContextPriority,
    ContextSegment,
    ContextType,
)
from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore
from agentuniverse.agent.context.store.ram_context_store import RamContextStore
from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


def populated_manager(count, *, critical=False):
    """Build a complete window without invoking unrelated budget policies."""
    manager = ContextManager()
    manager._hot_store = RamContextStore(max_segments=count + 10)
    window = manager.create_context_window(
        "session",
        max_tokens=count * 10 + 1000,
        reserved_tokens=1000,
    )
    created = datetime.now() - timedelta(hours=1)
    segments = [
        ContextSegment(
            content=f"segment {index}",
            tokens=10,
            type=ContextType.SYSTEM if critical else ContextType.BACKGROUND,
            priority=ContextPriority.CRITICAL if critical else ContextPriority.HIGH,
            metadata=ContextMetadata(last_accessed=created + timedelta(seconds=index)),
        )
        for index in range(count)
    ]
    manager._hot_store.add(segments, session_id="session")
    window.segment_ids = [segment.id for segment in segments]
    window.total_tokens = count * 10
    return manager, window, segments


@pytest.mark.parametrize("count", [99, 100, 101, 205])
def test_compression_receives_and_preserves_complete_session(count):
    manager, window, segments = populated_manager(count, critical=True)
    # Identity compression isolates snapshot completeness from budget policy.
    manager._compressor = Mock()
    manager._compressor.compress.side_effect = lambda items, *args, **kwargs: (items, None)

    manager._make_room(window, needed_tokens=1)

    original_ids = {segment.id for segment in segments}
    compressed_input = manager._compressor.compress.call_args.args[0]
    assert {segment.id for segment in compressed_input} == original_ids
    assert {segment.id for segment in manager.get_context("session")} == original_ids
    assert set(window.segment_ids) == original_ids
    assert window.total_tokens == count * 10


def test_prune_recounts_every_remaining_segment():
    manager, window, segments = populated_manager(206, critical=True)
    segments[-1].priority = ContextPriority.EPHEMERAL

    manager._make_room(window, needed_tokens=1)

    remaining = manager.get_context("session")
    assert len(remaining) == 205
    assert window.total_tokens == sum(segment.tokens for segment in remaining)
    assert set(window.segment_ids) == {segment.id for segment in remaining}


def test_eviction_can_find_candidates_beyond_first_page():
    manager, window, segments = populated_manager(101, critical=True)
    manager.enable_compression = False
    # The oldest item is the only eligible eviction candidate.
    segments[0].priority = ContextPriority.HIGH

    manager._make_room(window, needed_tokens=1)

    remaining = manager.get_context("session")
    assert len(remaining) == 100
    assert segments[0].id not in {segment.id for segment in remaining}
    assert window.total_tokens == 1000


def test_user_retrieval_keeps_default_page_size():
    manager, _, _ = populated_manager(205)
    assert len(manager._hot_store.get("session")) == 100
    assert len(manager._hot_store.get("session", limit=None)) == 205


def test_redis_unlimited_retrieval_without_external_service():
    _, _, segments = populated_manager(205)
    store = RedisContextStore()
    store._redis = Mock()
    store._redis.hgetall.return_value = {segment.id: store._serialize_segment(segment) for segment in segments}
    assert len(store.get("session")) == 100
    assert len(store.get("session", limit=None)) == 205


def test_chroma_passes_unlimited_retrieval_to_collection():
    _, _, segments = populated_manager(205)
    store = ChromaContextStore()
    store._collection = Mock()
    store.add(segments, session_id="session")
    stored = store._collection.add.call_args.kwargs

    def collection_get(*, where, limit):
        assert where == {"session_id": "session"}
        return {key: values[:limit] for key, values in stored.items()}

    store._collection.get.side_effect = collection_get
    assert len(store.get("session")) == 100
    assert len(store.get("session", limit=None)) == 205
    store._collection.get.assert_called_with(where={"session_id": "session"}, limit=None)
