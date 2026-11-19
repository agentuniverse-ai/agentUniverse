"""Keyword search should exclude context with no textual match."""

from datetime import datetime, timedelta

from agentuniverse.agent.context.context_model import ContextPriority, ContextSegment, ContextType
from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


class FakeRedis:
    def __init__(self, data):
        self.data = data

    def hgetall(self, key):
        return self.data.get(key, {})


def test_search_requires_a_text_match_even_for_high_priority_segments():
    store = RedisContextStore()
    unrelated = ContextSegment(type=ContextType.SYSTEM, priority=ContextPriority.CRITICAL,
                               content="unrelated system instruction", tokens=3)
    relevant = ContextSegment(type=ContextType.CONVERSATION, priority=ContextPriority.LOW,
                              content="the needle is here", tokens=5)
    store._redis = FakeRedis({store._make_session_key("one"): {
        unrelated.id.encode(): store._serialize_segment(unrelated),
        relevant.id.encode(): store._serialize_segment(relevant),
    }})

    assert [segment.id for segment in store.search("needle", "one")] == [relevant.id]
    assert store.search("missing", "one") == []
    assert store.search("  ", "one") == []


def test_search_finds_match_beyond_default_result_limit():
    store = RedisContextStore()
    now = datetime.now()
    segments = [
        ContextSegment(type=ContextType.CONVERSATION, content="unrelated", tokens=1,
                       metadata={"created_at": now - timedelta(minutes=index)})
        for index in range(1000)
    ]
    older_match = ContextSegment(
        type=ContextType.CONVERSATION, content="needle", tokens=1,
        metadata={"created_at": now - timedelta(days=2)},
    )
    segments.append(older_match)
    store._redis = FakeRedis({store._make_session_key("one"): {
        segment.id.encode(): store._serialize_segment(segment) for segment in segments
    }})

    assert [segment.id for segment in store.search("needle", "one")] == [older_match.id]
