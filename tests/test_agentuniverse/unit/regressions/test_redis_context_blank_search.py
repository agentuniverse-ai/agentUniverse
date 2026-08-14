import pytest

from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


class UnexpectedRedisAccess:
    def hgetall(self, key):
        raise AssertionError("Redis should not be queried for a blank search")


@pytest.mark.parametrize("query", [None, "", "   "])
def test_blank_search_skips_redis(query):
    store = RedisContextStore(name="redis")
    store._redis = UnexpectedRedisAccess()

    assert store.search(query, "session") == []
