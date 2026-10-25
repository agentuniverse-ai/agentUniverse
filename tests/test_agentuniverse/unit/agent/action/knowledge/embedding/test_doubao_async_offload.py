"""Doubao's synchronous SDK must not run on the async caller's loop thread."""
import asyncio
import threading
from types import SimpleNamespace
from unittest.mock import patch
import pytest
from agentuniverse.agent.action.knowledge.embedding.doubao_embedding import DoubaoEmbedding


def test_sdk_request_runs_off_loop_and_preserves_order():
    loop_thread = threading.get_ident()
    calls = []
    def create(**kwargs):
        calls.append((threading.get_ident(), kwargs))
        return SimpleNamespace(data=[SimpleNamespace(embedding=[float(i)]) for i in range(len(kwargs['input']))])
    embedding = DoubaoEmbedding(endpoint_id='endpoint', client=SimpleNamespace(embeddings=SimpleNamespace(create=create)))
    assert asyncio.run(embedding.async_get_embeddings(['first', 'second'])) == [[0.], [1.]]
    assert calls[0][0] != loop_thread
    assert calls[0][1] == {'model': 'endpoint', 'input': ['first', 'second']}


def test_loop_progresses_while_sdk_waits():
    entered, progressed = threading.Event(), threading.Event()
    def create(**kwargs):
        entered.set()
        # Bounded wait also makes the pre-fix failure terminate deterministically.
        if not progressed.wait(1):
            raise RuntimeError('event loop blocked')
        return SimpleNamespace(data=[SimpleNamespace(embedding=[1.])])
    embedding = DoubaoEmbedding(endpoint_id='endpoint', client=SimpleNamespace(embeddings=SimpleNamespace(create=create)))
    async def run():
        task = asyncio.create_task(embedding.async_get_embeddings(['hello']))
        while not entered.is_set():
            await asyncio.sleep(0)
        progressed.set()
        return await task
    assert asyncio.run(run()) == [[1.]]


def test_async_forwards_options_and_propagates_errors():
    def fail(self, texts, **kwargs):
        assert texts == ['hello'] and kwargs == {'text_type': 'query'}
        raise ValueError('sdk failed')
    embedding = DoubaoEmbedding(endpoint_id='endpoint')
    with patch.object(DoubaoEmbedding, 'get_embeddings', fail):
        with pytest.raises(ValueError, match='sdk failed'):
            asyncio.run(embedding.async_get_embeddings(['hello'], text_type='query'))


def test_normalization_preserved():
    create = lambda **kwargs: SimpleNamespace(data=[SimpleNamespace(embedding=[3., 4.] + [0.] * 510)])
    embedding = DoubaoEmbedding(endpoint_id='endpoint', embedding_dims=512,
        client=SimpleNamespace(embeddings=SimpleNamespace(create=create)))
    result = asyncio.run(embedding.async_get_embeddings(['hello']))
    assert result[0][:2] == [.6, .8]
    assert len(result[0]) == 512


def test_worker_preserves_context_variables():
    from contextvars import ContextVar
    marker = ContextVar('doubao_test_marker', default='missing')
    def create(**kwargs):
        assert marker.get() == 'request-context'
        return SimpleNamespace(data=[SimpleNamespace(embedding=[1.])])
    embedding = DoubaoEmbedding(endpoint_id='endpoint', client=SimpleNamespace(embeddings=SimpleNamespace(create=create)))
    async def run():
        marker.set('request-context')
        return await embedding.async_get_embeddings(['hello'])
    assert asyncio.run(run()) == [[1.]]


def test_cancellation_propagates_without_waiting_for_worker():
    entered, release = threading.Event(), threading.Event()
    def create(**kwargs):
        entered.set()
        release.wait(1)
        return SimpleNamespace(data=[SimpleNamespace(embedding=[1.])])
    embedding = DoubaoEmbedding(endpoint_id='endpoint', client=SimpleNamespace(embeddings=SimpleNamespace(create=create)))
    async def run():
        task = asyncio.create_task(embedding.async_get_embeddings(['hello']))
        try:
            while not entered.is_set():
                await asyncio.sleep(0)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert not release.is_set()
        finally:
            release.set()
    asyncio.run(run())
