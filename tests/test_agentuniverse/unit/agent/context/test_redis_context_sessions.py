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


class PrefixTrackingRedis:
    def __init__(self, keys):
        self.keys = keys
        self.scan_calls = []
        self.deleted = []

    def scan(self, cursor, match, count):
        self.scan_calls.append((cursor, match, count))
        return 0, self.keys

    def delete(self, *keys):
        self.deleted.extend(keys)


def test_scan_escapes_literal_prefix_metacharacters():
    prefix = r"tenant*?[\]:"
    redis = PrefixTrackingRedis([f"{prefix}session:one"])
    store = RedisContextStore(key_prefix=prefix)
    store._redis = redis

    assert store.get_all_sessions() == ["one"]
    assert redis.scan_calls[0][1] == r"tenant\*\?\[\\\]:session:*"

    store.clear_all()
    assert redis.scan_calls[1][1] == r"tenant\*\?\[\\\]:*"
    assert redis.deleted == [f"{prefix}session:one"]
