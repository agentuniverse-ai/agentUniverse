"""Explicit invalid query limits must not become default database searches."""
import asyncio

import pytest

from agentuniverse.agent.action.knowledge.store.pgvector_store import PGVectorStore
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.redis_vector_store import RedisVectorStore


class Connection:
    def __init__(self):
        self.calls = []

    def execute(self, sql, params=None):
        self.calls.append((sql, params))
        return self

    def fetchall(self):
        return []

    def execute_command(self, *args):
        self.calls.append(args)
        return [0]


class AsyncConnection(Connection):
    async def execute(self, sql, params=None):
        super().execute(sql, params)
        return self

    async def fetchall(self):
        return []

    async def execute_command(self, *args):
        return super().execute_command(*args)


def setup_query(store_type, asynchronous, limit):
    connection = AsyncConnection() if asynchronous else Connection()
    settings = {'dimensions': 2, 'similarity_top_k': 7,
                'async_client' if asynchronous else 'client': connection}
    store = store_type(**settings)
    query = Query(embeddings=[[1.0, 0.0]], similarity_top_k=limit)
    return store, query, connection


@pytest.mark.parametrize('store_type', [PGVectorStore, RedisVectorStore])
@pytest.mark.parametrize('asynchronous', [False, True])
@pytest.mark.parametrize('limit', [0, -1])
def test_invalid_override_fails_before_database_access(store_type, asynchronous, limit):
    store, query, connection = setup_query(store_type, asynchronous, limit)
    with pytest.raises(ValueError, match='similarity_top_k must be a positive integer'):
        if asynchronous:
            asyncio.run(store.async_query(query))
        else:
            store.query(query)
    assert connection.calls == []


@pytest.mark.parametrize('store_type', [PGVectorStore, RedisVectorStore])
@pytest.mark.parametrize('asynchronous', [False, True])
@pytest.mark.parametrize('limit,expected', [(None, 7), (2, 2)])
def test_default_and_positive_override_reach_database_limit(
        store_type, asynchronous, limit, expected):
    store, query, connection = setup_query(store_type, asynchronous, limit)
    result = asyncio.run(store.async_query(query)) if asynchronous else store.query(query)
    assert result == []
    command = connection.calls[-1]
    if store_type is PGVectorStore:
        assert command[1][-1] == expected
    else:
        assert command[0] == 'FT.SEARCH'
        assert command[2].startswith(f'(*)=>[KNN {expected} ')
        assert command[command.index('LIMIT') + 2] == expected
