"""Indexed Redis retrieval should deserialize only the needed pages."""
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

fakeredis = pytest.importorskip('fakeredis')
from agentuniverse.agent.context.context_model import ContextMetadata, ContextPriority, ContextSegment, ContextType
from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


@pytest.fixture
def store():
    instance = RedisContextStore()
    instance._redis = fakeredis.FakeRedis()
    yield instance
    instance._redis.close()


def populate(store, count):
    start = datetime(2026, 1, 1)
    docs = [ContextSegment(id=str(i), type=ContextType.CONVERSATION, priority=ContextPriority.HIGH,
                           content=f'message {i}', tokens=2,
                           metadata=ContextMetadata(created_at=start + timedelta(seconds=i)))
            for i in range(count)]
    store.add(docs, session_id='one')
    return docs


def test_small_limit_does_not_fetch_whole_session(store):
    populate(store, 1000)
    original = store._deserialize_segment
    with patch.object(store._redis, 'hgetall', wraps=store._redis.hgetall) as all_data, \
         patch.object(RedisContextStore, '_deserialize_segment', side_effect=original) as deserialize:
        result = store.get('one', limit=1)
    assert [doc.id for doc in result] == ['999']
    all_data.assert_not_called()
    assert deserialize.call_count == 1


def test_filters_continue_past_nonmatching_and_corrupt_entries(store):
    docs = populate(store, 150)
    docs[3].type = ContextType.REFERENCE
    docs[7].type = ContextType.REFERENCE
    docs[8].type = ContextType.REFERENCE
    docs[8].priority = ContextPriority.LOW
    store.add([docs[3], docs[7], docs[8]], session_id='one')
    store._redis.hset(store._make_session_key('one'), '149', b'broken json')
    with patch.object(store._redis, 'hgetall', wraps=store._redis.hgetall) as all_data:
        result = store.get('one', context_type=ContextType.REFERENCE, priority=ContextPriority.HIGH, limit=2)
    assert [doc.id for doc in result] == ['7', '3']
    all_data.assert_not_called()


@pytest.mark.parametrize('limit', [1, 128, 129, 1000])
def test_page_boundaries_match_newest_first_order(store, limit):
    populate(store, 260)
    with patch.object(store._redis, 'hmget', wraps=store._redis.hmget) as reads:
        result = store.get('one', limit=limit)
    assert [doc.id for doc in result] == [str(i) for i in range(259, max(-1, 259 - limit), -1)]
    assert all(len(call.args[1]) <= 128 for call in reads.call_args_list)


@pytest.mark.parametrize('index_state', ['absent', 'missing_member', 'stale_member'])
def test_legacy_or_incomplete_index_preserves_hash_data(store, index_state):
    populate(store, 3)
    key = store._make_index_key('one')
    if index_state == 'absent':
        store._redis.delete(key)
    elif index_state == 'missing_member':
        store._redis.zrem(key, '2')
    else:
        store._redis.zadd(key, {'stale': 9999999999})
    result = store.get('one', limit=2)
    assert [doc.id for doc in result] == ['2', '1']


def test_update_delete_and_session_isolation(store):
    docs = populate(store, 3)
    docs[0].metadata.created_at = datetime(2027, 1, 1)
    store.add([docs[0]], session_id='one')
    store.add([docs[2]], session_id='two')
    store.delete('one', segment_ids=['1'])
    assert [doc.id for doc in store.get('one', limit=10)] == ['0', '2']
    assert [doc.id for doc in store.get('two', limit=10)] == ['2']
    assert store.get('missing', limit=10) == []


def test_redis_errors_propagate(store):
    populate(store, 1)
    with patch.object(store._redis, 'hmget', side_effect=RuntimeError('disconnected')):
        with pytest.raises(RuntimeError, match='disconnected'):
            store.get('one', limit=1)


def test_equal_timestamps_page_without_losing_records(store):
    docs = populate(store, 130)
    for doc in docs:
        doc.metadata.created_at = datetime(2026, 1, 1)
    store.add(docs, session_id='one')
    result = store.get('one', limit=130)
    assert len(result) == 130
    assert {doc.id for doc in result} == {doc.id for doc in docs}


def test_missing_payload_during_read_continues_to_next_page(store):
    populate(store, 3)
    original = store._redis.hmget
    calls = 0

    def lose_newest(key, ids):
        nonlocal calls
        calls += 1
        if calls == 1:
            return [None for _ in ids]
        return original(key, ids)

    with patch.object(store._redis, 'hmget', side_effect=lose_newest):
        result = store.get('one', limit=1)
    assert [doc.id for doc in result] == ['1']
