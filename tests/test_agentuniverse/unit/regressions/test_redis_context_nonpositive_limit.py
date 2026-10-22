from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


class UnexpectedRedisAccess:
    def hgetall(self, key):
        raise AssertionError("Redis should not be queried for an empty result window")


def test_get_with_nonpositive_limit_skips_redis():
    store = RedisContextStore(name="redis")
    store._redis = UnexpectedRedisAccess()

    assert store.get("session", limit=-1) == []
    assert store.get("session", limit=0) == []
