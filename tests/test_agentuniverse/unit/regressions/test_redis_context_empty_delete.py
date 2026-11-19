"""Regression tests for Redis context-store deletion."""

from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


class RecordingRedis:
    def __init__(self):
        self.calls = []

    def hdel(self, *args):
        self.calls.append(("hdel", args))

    def zrem(self, *args):
        self.calls.append(("zrem", args))

    def delete(self, *args):
        self.calls.append(("delete", args))


def test_empty_segment_id_list_does_not_delete_session():
    store = RedisContextStore(name="redis")
    redis = RecordingRedis()
    store._redis = redis

    store.delete("session", segment_ids=[])

    assert redis.calls == []
