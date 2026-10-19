"""Async vector operations must await the embedding component's async API."""

# Test doubles use concise built-in errors to exercise failure paths.
# ruff: noqa: TRY003

import asyncio
from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.pgvector_store import PGVectorStore
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.redis_vector_store import RedisVectorStore
from tests.test_agentuniverse.unit.agent.action.knowledge.store.test_redis_vector_store import FakeAsyncConnection


class PGCursor:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def executemany(self, sql, rows):
        pass


class PGConnection:
    async def execute(self, *args):
        return self

    async def fetchall(self):
        return []

    def cursor(self):
        return PGCursor()


class AsyncEmbedding(Embedding):
    def get_embeddings(self, texts, **kwargs):
        raise AssertionError("async store called the synchronous embedding API")

    async def async_get_embeddings(self, texts, **kwargs):
        await asyncio.sleep(0)
        return [[float(len(text)), 0.0] for text in texts]


@pytest.fixture(params=[PGVectorStore, RedisVectorStore], ids=["pgvector", "redis"])
def store(request, monkeypatch):
    cls = request.param
    connection = PGConnection() if cls is PGVectorStore else FakeAsyncConnection()
    model = AsyncEmbedding()
    monkeypatch.setattr(
        cls.__module__ + ".EmbeddingManager",
        lambda: SimpleNamespace(get_instance_obj=lambda *args, **kwargs: model),
    )
    return cls(async_client=connection, embedding_model="async", dimensions=2)


def test_query_awaits_embedding_and_preserves_query_type(store, monkeypatch):
    calls = []

    async def embed(self, texts, **kwargs):
        calls.append((texts, kwargs))
        await asyncio.sleep(0)
        return [[1.0, 0.0]]

    monkeypatch.setattr(AsyncEmbedding, "async_get_embeddings", embed)
    assert asyncio.run(store.async_query(Query(query_str="hello"))) == []
    assert calls == [(["hello"], {"text_type": "query"})]


@pytest.mark.parametrize("method", ["async_upsert_document", "async_insert_document", "async_update_document"])
def test_async_writes_fill_only_missing_vectors_in_order(store, method):
    documents = [
        Document(id="one", text="a"),
        Document(id="two", text="ignore", embedding=[7.0, 8.0]),
        Document(id="three", text="abc"),
    ]
    asyncio.run(getattr(store, method)(documents))
    assert [document.embedding for document in documents] == [[1.0, 0.0], [7.0, 8.0], [3.0, 0.0]]


def test_precomputed_query_does_not_require_embedding_component(store, monkeypatch):
    def unexpected(*args, **kwargs):
        raise AssertionError("precomputed vectors must bypass the embedding manager")

    monkeypatch.setattr(type(store).__module__ + ".EmbeddingManager", unexpected)
    assert asyncio.run(store.async_query(Query(embeddings=[[1.0, 0.0]]))) == []


def test_waiting_embedding_allows_other_tasks_and_propagates_cancellation(store, monkeypatch):
    async def run():
        started = asyncio.Event()
        release = asyncio.Event()

        async def embed(self, texts, **kwargs):
            started.set()
            await release.wait()
            return [[1.0, 0.0]]

        monkeypatch.setattr(AsyncEmbedding, "async_get_embeddings", embed)
        task = asyncio.create_task(store.async_query(Query(query_str="hello")))
        # Avoid timing thresholds: the embedding must reach its await before
        # this independent task can inspect and cancel the pending operation.
        try:
            await asyncio.wait_for(started.wait(), timeout=1)
            assert not task.done()
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        finally:
            release.set()
            await asyncio.gather(task, return_exceptions=True)

    asyncio.run(run())


def test_embedding_failure_is_not_swallowed(store, monkeypatch):
    async def embed(self, texts, **kwargs):
        raise RuntimeError("embedding unavailable")

    monkeypatch.setattr(AsyncEmbedding, "async_get_embeddings", embed)
    with pytest.raises(RuntimeError, match="embedding unavailable"):
        asyncio.run(store.async_query(Query(query_str="hello")))


@pytest.mark.parametrize("vector", [[1.0], []])
def test_async_generated_dimensions_are_validated(store, monkeypatch, vector):
    async def embed(self, texts, **kwargs):
        return [vector]

    monkeypatch.setattr(AsyncEmbedding, "async_get_embeddings", embed)
    with pytest.raises(ValueError, match="dimension|non-empty"):
        asyncio.run(store.async_upsert_document([Document(text="hello")]))
