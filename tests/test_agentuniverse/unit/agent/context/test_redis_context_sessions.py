from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


class FakeRedis:
    def __init__(self, keys):
        self.keys = keys

    def scan(self, cursor, match, count):
        assert cursor == 0
        assert match == "agentuniverse:context:session:*"
        assert count == 100
        return 0, self.keys


def test_get_all_sessions_accepts_bytes_keys():
    store = RedisContextStore()
    store._redis = FakeRedis([b"agentuniverse:context:session:one"])

    assert store.get_all_sessions() == ["one"]


def test_get_all_sessions_accepts_decoded_string_keys():
    store = RedisContextStore()
    store._redis = FakeRedis(["agentuniverse:context:session:two"])

    assert store.get_all_sessions() == ["two"]
