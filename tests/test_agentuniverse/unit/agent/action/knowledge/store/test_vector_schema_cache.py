"""Successful schema setup is reused only for its connection and config."""

# Test doubles use concise built-in errors to exercise failure paths.
# ruff: noqa: TRY003

import asyncio

import pytest

from agentuniverse.agent.action.knowledge.store.pgvector_store import PGVectorStore
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.redis_vector_store import RedisVectorStore


class Connection:
    def __init__(self, *, existing=False, failures=0):
        self.commands = []
        self.existing = existing
        self.failures = failures

    def execute(self, sql, *args):
        return self.execute_command(sql, *args)

    def execute_command(self, *args):
        self.commands.append(args)
        if args[0].startswith("CREATE") or args[0] == "FT.CREATE":
            if self.failures:
                self.failures -= 1
                raise RuntimeError("temporary setup failure")
            if self.existing and args[0] == "FT.CREATE":
                raise RuntimeError("Index already exists")
        return self if args[0].startswith("SELECT") else [0]

    def fetchall(self):
        return []

    @property
    def setup_count(self):
        return sum(args[0].startswith("CREATE") or args[0] == "FT.CREATE" for args in self.commands)


class AsyncConnection(Connection):
    async def execute(self, sql, *args):
        return super().execute_command(sql, *args)

    async def execute_command(self, *args):
        return super().execute_command(*args)

    async def fetchall(self):
        return []


@pytest.fixture(params=[PGVectorStore, RedisVectorStore], ids=["pgvector", "redis"])
def cls(request):
    return request.param


def run_setup(store, dimensions=2):
    if isinstance(store, PGVectorStore):
        store._ensure_table(dimensions)
    else:
        store._ensure_index(dimensions)


async def async_setup(store, dimensions=2):
    if isinstance(store, PGVectorStore):
        await store._async_ensure_table(dimensions)
    else:
        await store._async_ensure_index(dimensions)


def test_repeated_queries_do_not_repeat_successful_setup(cls):
    connection = Connection(existing=True)
    store = cls(client=connection, dimensions=2)
    for _ in range(3):
        assert store.query(Query(embeddings=[[1.0, 0.0]])) == []
    assert connection.setup_count == (3 if cls is PGVectorStore else 1)


def test_async_queries_cache_setup_separately_from_sync(cls):
    connection = Connection(existing=True)
    async_connection = AsyncConnection(existing=True)
    store = cls(client=connection, async_client=async_connection, dimensions=2)
    run_setup(store)

    async def run():
        for _ in range(3):
            assert await store.async_query(Query(embeddings=[[1.0, 0.0]])) == []

    asyncio.run(run())
    assert connection.setup_count == (3 if cls is PGVectorStore else 1)
    assert async_connection.setup_count == (3 if cls is PGVectorStore else 1)


@pytest.mark.parametrize("is_async", [False, True])
def test_failed_setup_is_retried(cls, is_async):
    connection = AsyncConnection(failures=1) if is_async else Connection(failures=1)
    store = cls(**{"async_client" if is_async else "client": connection}, dimensions=2)

    def run():
        return asyncio.run(async_setup(store)) if is_async else run_setup(store)

    with pytest.raises(RuntimeError, match="temporary setup failure"):
        run()
    run()
    run()
    assert connection.setup_count == (4 if cls is PGVectorStore else 2)


@pytest.mark.parametrize("is_async", [False, True])
def test_connection_replacement_invalidates_setup(cls, is_async):
    first = AsyncConnection() if is_async else Connection()
    second = AsyncConnection() if is_async else Connection()
    field = "async_client" if is_async else "client"
    store = cls(**{field: first}, dimensions=2)

    def run():
        return asyncio.run(async_setup(store)) if is_async else run_setup(store)

    run()
    setattr(store, field, second)
    run()
    run()
    assert first.setup_count == second.setup_count == (3 if cls is PGVectorStore else 1)


@pytest.mark.parametrize("is_async", [False, True])
def test_schema_config_changes_invalidate_setup_and_dimensions_still_validate(cls, is_async):
    connection = AsyncConnection() if is_async else Connection()
    store = cls(**{"async_client" if is_async else "client": connection}, dimensions=2)

    def run(dimensions=2):
        return asyncio.run(async_setup(store, dimensions)) if is_async else run_setup(store, dimensions)

    run()
    if cls is PGVectorStore:
        store.table_name = "other_docs"
    else:
        store.index_name = "other_docs"
    run()
    run()
    assert connection.setup_count == (6 if cls is PGVectorStore else 2)
    with pytest.raises(ValueError, match="dimension"):
        run(dimensions=3)
