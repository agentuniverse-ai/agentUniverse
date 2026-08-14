import json

from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


class RecordingRedis:
    def __init__(self):
        self.payload = None

    def hset(self, key, segment_id, payload):
        self.payload = payload

    def expire(self, key, ttl):
        pass

    def zadd(self, key, values):
        pass


def test_add_serializes_the_redis_session_scope():
    segment = ContextSegment(
        type=ContextType.CONVERSATION,
        content="context",
        tokens=1,
        session_id="stale-session",
    )
    redis = RecordingRedis()
    store = RedisContextStore(name="redis")
    store._redis = redis

    store.add([segment], session_id="current-session")

    assert segment.session_id == "current-session"
    assert json.loads(redis.payload.decode("utf-8"))["session_id"] == "current-session"
