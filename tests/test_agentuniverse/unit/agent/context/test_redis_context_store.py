"""Tests for the Redis-backed context store."""

from agentuniverse.agent.context.context_model import (
    ContextPriority,
    ContextSegment,
    ContextType,
)
from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


class _FakeRedis:
    def __init__(self, entries):
        self._entries = entries

    def hgetall(self, key):
        return self._entries


def test_search_excludes_segments_without_query_matches():
    store = RedisContextStore()
    matching = ContextSegment(
        type=ContextType.CONVERSATION,
        priority=ContextPriority.LOW,
        content="contains the needle",
        tokens=3,
        session_id="session-1",
    )
    unrelated = ContextSegment(
        type=ContextType.SYSTEM,
        priority=ContextPriority.CRITICAL,
        content="completely unrelated",
        tokens=2,
        session_id="session-1",
    )
    store._redis = _FakeRedis({
        matching.id.encode(): store._serialize_segment(matching),
        unrelated.id.encode(): store._serialize_segment(unrelated),
    })

    results = store.search("needle", "session-1")

    assert [segment.id for segment in results] == [matching.id]
