from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


class FakeRedis:
    def __init__(self):
        self.payload = None

    def hset(self, key, field, value):
        self.payload = value

    def expire(self, *args):
        return None

    def zadd(self, *args):
        return None


def test_redis_add_persists_missing_segment_session_id():
    store = RedisContextStore()
    redis = FakeRedis()
    store._redis = redis
    segment = ContextSegment(type=ContextType.TASK, content="text", tokens=1)

    store.add([segment], session_id="session-a")

    restored = store._deserialize_segment(redis.payload)
    assert restored.session_id == "session-a"
    assert segment.session_id == "session-a"
