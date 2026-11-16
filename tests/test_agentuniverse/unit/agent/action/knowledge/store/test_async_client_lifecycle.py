"""Coroutine client factories belong to their operating event loop."""

# Test doubles use concise built-in errors to exercise failure paths.
# ruff: noqa: TRY003

import asyncio
import gc
import warnings
from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.store.pgvector_store import PGVectorStore
from agentuniverse.agent.action.knowledge.store.redis_vector_store import RedisVectorStore
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent_serve.web.gunicorn_server import post_fork


@pytest.mark.parametrize("cls", [PGVectorStore, RedisVectorStore])
def test_startup_defers_coroutine_factory_until_awaited(cls, monkeypatch):
    created_on = []
    async_client = object()

    def sync_factory(self):
        self.client = "sync client"
        return self.client

    async def async_factory(self):
        created_on.append(asyncio.get_running_loop())
        self.async_client = async_client
        return async_client

    monkeypatch.setattr(cls, "_new_client", sync_factory)
    monkeypatch.setattr(cls, "_new_async_client", async_factory)
    queue = []
    monkeypatch.setattr("agentuniverse.agent_serve.web.post_fork_queue.POST_FORK_QUEUE", queue)
    monkeypatch.setattr("agentuniverse.agent_serve.web.gunicorn_server.POST_FORK_QUEUE", queue)
    store = cls()
    store._initialize_by_component_configer(SimpleNamespace(name="store", description="test"))

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", RuntimeWarning)
        post_fork(None, None)
        gc.collect()
    assert not [warning for warning in caught if issubclass(warning.category, RuntimeWarning)]
    assert store.client == "sync client"
    assert store.async_client is None
    assert created_on == []

    async def use():
        assert await store._ensure_async_client() is async_client
        assert await store._ensure_async_client() is async_client
        assert created_on == [asyncio.get_running_loop()]

    asyncio.run(use())


def test_synchronous_async_client_factory_still_runs_after_fork(monkeypatch):
    class SDKStore(Store):
        def _new_client(self):
            self.client = "sync"

        def _new_async_client(self):
            self.async_client = "async SDK client created synchronously"

    queue = []
    monkeypatch.setattr("agentuniverse.agent_serve.web.post_fork_queue.POST_FORK_QUEUE", queue)
    monkeypatch.setattr("agentuniverse.agent_serve.web.gunicorn_server.POST_FORK_QUEUE", queue)
    store = SDKStore()
    store._initialize_by_component_configer(SimpleNamespace(name="sdk", description="test"))
    post_fork(None, None)
    assert store.client == "sync"
    assert store.async_client == "async SDK client created synchronously"


@pytest.mark.parametrize("cls", [PGVectorStore, RedisVectorStore])
def test_deferred_initialization_failure_propagates(cls, monkeypatch):
    async def fail(self):
        raise RuntimeError("connection unavailable")

    monkeypatch.setattr(cls, "_new_async_client", fail)
    with pytest.raises(RuntimeError, match="connection unavailable"):
        asyncio.run(cls()._ensure_async_client())
