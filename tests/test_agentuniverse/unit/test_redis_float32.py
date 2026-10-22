"""Verify actual FLOAT32 bytes; Redis I/O is replaced by a recording boundary."""
import asyncio
import math
import struct
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.redis_vector_store import RedisVectorStore


@pytest.mark.parametrize('value', [1e39, -1e39, 1e300, -1e300])
@pytest.mark.parametrize('operation', ['query', 'upsert', 'async_query', 'async_upsert'])
def test_overflow_is_rejected_before_redis_io(value, operation):
    connection = Mock()
    connection.execute_command.return_value = [0]
    async_connection = AsyncMock()
    async_connection.execute_command.return_value = [0]
    pipeline = MagicMock()
    pipeline.__aenter__.return_value = pipeline
    pipeline.execute = AsyncMock(return_value=[])
    async_connection.pipeline = Mock(return_value=pipeline)
    store = RedisVectorStore(client=connection, async_client=async_connection)
    with pytest.raises(ValueError, match='FLOAT32'):
        if operation == 'query':
            store.query(Query(embeddings=[[value, 1.0]]))
        elif operation == 'upsert':
            store.upsert_document([Document(text='bad', embedding=[value, 1.0])])
        elif operation == 'async_query':
            asyncio.run(store.async_query(Query(embeddings=[[value, 1.0]])))
        else:
            asyncio.run(store.async_upsert_document([Document(text='bad', embedding=[value, 1.0])]))
    assert not connection.mock_calls
    assert not async_connection.mock_calls
    assert store.dimensions is None


@pytest.mark.parametrize('vector', [
    [0.0, -0.0], [1.0, -2.0], [3.4028234663852886e38, -3.4028234663852886e38],
    [1e-40, -1e-40], [1e-100, -1e-100],
])
def test_representable_or_underflowing_floats_keep_existing_wire_format(vector):
    store = RedisVectorStore()
    store._check_vector(vector)
    payload = store._vector_bytes(vector)
    expected = struct.pack('<2f', *vector)
    assert payload == expected
    actual = store._bytes_vector(payload)
    assert all(math.isfinite(x) for x in actual)
    assert actual == list(struct.unpack('<2f', expected))


@pytest.mark.parametrize('value', [float('inf'), float('-inf'), float('nan'), 10 ** 1000],
                         ids=['inf', 'negative-inf', 'nan', 'huge-integer'])
def test_nonfinite_or_unconvertible_scalar_is_a_validation_error(value):
    with pytest.raises(ValueError):
        RedisVectorStore()._check_vector([value])


def test_invalid_second_vector_does_not_queue_partial_batch():
    connection = Mock()
    store = RedisVectorStore(client=connection, dimensions=2)
    with pytest.raises(ValueError, match='FLOAT32'):
        store.upsert_document([Document(text='valid', embedding=[1.0, 2.0]),
                               Document(text='invalid', embedding=[1e40, 0.0])])
    assert not connection.mock_calls
