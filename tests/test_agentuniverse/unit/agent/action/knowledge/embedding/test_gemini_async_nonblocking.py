"""Offline Gemini async scheduling and synchronous-contract regressions."""

import asyncio
import sys
from contextvars import ContextVar
from threading import Event, get_ident
from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.embedding.gemini_embedding import GeminiEmbedding


def embedding_with(call):
    return GeminiEmbedding(client=SimpleNamespace(models=SimpleNamespace(embed_content=call)))


def response(vectors):
    return SimpleNamespace(embeddings=[SimpleNamespace(values=v) for v in vectors])


def test_sdk_call_does_not_block_event_loop():
    released = Event()
    worker_threads = []

    def embed(**kwargs):
        worker_threads.append(get_ident())
        assert released.wait(5), "event loop could not release the SDK call"
        return response([[1.0, 2.0]])

    async def run():
        task = asyncio.create_task(embedding_with(embed).async_get_embeddings(["hello"]))
        asyncio.get_running_loop().call_soon(released.set)
        return await task

    assert asyncio.run(run()) == [[1.0, 2.0]]
    assert worker_threads[0] != get_ident()


@pytest.mark.parametrize("vectors", [[], [[1.0]], [[1.0, 2.0], [3.0, 4.0]]])
def test_result_order_and_model_match_sync_contract(vectors):
    calls = []

    def embed(**kwargs):
        calls.append(kwargs)
        return response(vectors)

    embedding = embedding_with(embed)
    embedding.embedding_model_name = "configured-model"
    texts = ["first", "second"]
    assert asyncio.run(embedding.async_get_embeddings(texts)) == vectors
    assert calls == [{"model": "configured-model", "contents": texts}]


def test_sdk_error_keeps_existing_value_error_contract():
    failure = RuntimeError("offline failure")

    def embed(**kwargs):
        raise failure

    with pytest.raises(ValueError) as raised:
        asyncio.run(embedding_with(embed).async_get_embeddings(["example"]))
    assert raised.value.args == (failure,)


def test_missing_key_keeps_existing_validation(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GOOGLE_API_KEY is required but not set"):
        asyncio.run(GeminiEmbedding().async_get_embeddings(["example"]))


def test_delegation_preserves_kwargs_and_context(monkeypatch):
    marker = ContextVar("gemini_test_marker", default="unset")
    calls = []

    def get_embeddings(self, texts, **kwargs):
        calls.append((texts, kwargs, marker.get(), get_ident()))
        return [[5.0]]

    monkeypatch.setattr(GeminiEmbedding, "get_embeddings", get_embeddings)
    token = marker.set("request-context")
    try:
        result = asyncio.run(GeminiEmbedding().async_get_embeddings(["text"], option="value"))
    finally:
        marker.reset(token)
    assert result == [[5.0]]
    assert calls[0][:3] == (["text"], {"option": "value"}, "request-context")
    assert calls[0][3] != get_ident()


def test_cancellation_releases_waiter_but_does_not_stop_sdk_thread():
    entered, release, finished = Event(), Event(), Event()

    def embed(**kwargs):
        entered.set()
        try:
            release.wait(5)
            return response([[1.0]])
        finally:
            finished.set()

    async def run():
        task = asyncio.create_task(embedding_with(embed).async_get_embeddings(["text"]))
        try:
            while not entered.is_set():
                await asyncio.sleep(0)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert not finished.is_set()
        finally:
            release.set()

    asyncio.run(run())
    assert finished.is_set()


def test_lazy_client_initialization_and_default_model_stay_off_loop(monkeypatch):
    calls = []

    def embed(**kwargs):
        calls.append(kwargs)
        return response([[7.0]])

    def client_factory(**kwargs):
        calls.append((kwargs, get_ident()))
        return SimpleNamespace(models=SimpleNamespace(embed_content=embed))

    monkeypatch.setitem(sys.modules, "google", SimpleNamespace(genai=SimpleNamespace(Client=client_factory)))
    embedding = GeminiEmbedding(gemini_api_key="offline-test-key")
    assert asyncio.run(embedding.async_get_embeddings(["text"])) == [[7.0]]
    assert calls[0][0] == {"api_key": "offline-test-key"}
    assert calls[0][1] != get_ident()
    assert calls[1] == {"model": "text-embedding-004", "contents": ["text"]}
    assert embedding.client is not None
