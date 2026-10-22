"""Redis glob characters in a configured prefix must remain literal.

Run with: pip install fakeredis; python -m pytest <this file> -q
"""

import json

import pytest

from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.redis_context_store import RedisContextStore

fakeredis = pytest.importorskip("fakeredis")

PREFIXES = [
    ("tenant*:", "tenant-other:"),
    ("tenant?:", "tenantX:"),
    ("tenant[ab]:", "tenanta:"),
    ("tenant\\:", "tenant:"),
    ("tenant]:", "tenant-other:"),
    ("租户:", "other:"),
]


@pytest.fixture(params=[False, True], ids=["bytes", "decoded"])
def client(request):
    connection = fakeredis.FakeRedis(decode_responses=request.param)
    yield connection
    connection.close()


def make_store(client, prefix):
    store = RedisContextStore(key_prefix=prefix)
    store._redis = client
    return store


def add_session(store, session):
    segment = ContextSegment(type=ContextType.CONVERSATION, content="hello", tokens=1)
    store.add([segment], session_id=session)
    return segment


@pytest.mark.parametrize("prefix,neighbor", PREFIXES)
def test_list_sessions_matches_literal_prefix(client, prefix, neighbor):
    store = make_store(client, prefix)
    other = make_store(client, neighbor)
    add_session(store, "own?[1]")
    add_session(other, "unrelated")
    assert store.get_all_sessions() == ["own?[1]"]
    assert other.count("unrelated") == 1


@pytest.mark.parametrize("prefix,neighbor", PREFIXES)
def test_clear_all_removes_only_literal_namespace(client, prefix, neighbor):
    store = make_store(client, prefix)
    other = make_store(client, neighbor)
    add_session(store, "own")
    retained = add_session(other, "unrelated")
    before = {key: client.dump(key) for key in client.scan_iter(match="*")}
    store.clear_all()
    assert store.count("own") == 0
    assert not client.exists(store._make_index_key("own"))
    assert json.loads(client.hget(other._make_session_key("unrelated"), retained.id))["content"] == "hello"
    assert client.exists(other._make_index_key("unrelated"))
    remaining = {key: client.dump(key) for key in client.scan_iter(match="*")}
    expected = {key: value for key, value in before.items()
                if (key.decode() if isinstance(key, bytes) else key).startswith(neighbor)}
    assert remaining == expected
