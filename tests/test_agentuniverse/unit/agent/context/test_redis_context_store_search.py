"""Keyword search should exclude context with no textual match."""

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
