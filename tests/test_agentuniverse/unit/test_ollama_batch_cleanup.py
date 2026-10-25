"""Keep a live event loop after a batch fails to expose orphan requests."""
import asyncio
import json

import httpx
import pytest

from agentuniverse.agent.action.knowledge.embedding.ollama_embedding import OllamaEmbedding


@pytest.mark.asyncio
@pytest.mark.parametrize('failure', ['http', 'json', 'missing', 'cancelled'])
async def test_batch_failure_waits_for_sibling_cleanup(failure):
    started = asyncio.Event()
    cleaned = asyncio.Event()
    requests = []

    async def handle(request):
        prompt = json.loads(request.content)['prompt']
        requests.append(asyncio.current_task())
        if prompt == 'blocked':
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                await asyncio.sleep(0)
                cleaned.set()
        await started.wait()
        if failure == 'http':
            return httpx.Response(500)
        if failure == 'json':
            return httpx.Response(200, content=b'not json')
        if failure == 'missing':
            return httpx.Response(200, json={})
        raise asyncio.CancelledError()

    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        model = OllamaEmbedding(embedding_model_name='test', client=object(), async_client=client)
        try:
            expected = asyncio.CancelledError if failure == 'cancelled' else Exception
            with pytest.raises(expected):
                await asyncio.wait_for(model.async_get_embeddings(['blocked', 'failure']), timeout=3)
            assert cleaned.is_set()
            assert all(task.done() for task in requests)
            assert not client.is_closed
        finally:
            # The baseline deliberately leaves a request running; clean it up
            # after the assertion so this test does not contaminate later cases.
            for task in requests:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*requests, return_exceptions=True)


@pytest.mark.asyncio
async def test_caller_cancellation_drains_all_children():
    all_started = asyncio.Event()
    started = []
    cleaned = []

    async def handle(request):
        prompt = json.loads(request.content)['prompt']
        started.append(prompt)
        if len(started) == 3:
            all_started.set()
        try:
            await asyncio.Event().wait()
        finally:
            await asyncio.sleep(0)
            cleaned.append(prompt)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        model = OllamaEmbedding(embedding_model_name='test', client=object(), async_client=client)
        batch = asyncio.create_task(model.async_get_embeddings(['a', 'b', 'c']))
        await asyncio.wait_for(all_started.wait(), 3)
        batch.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(batch, 3)
        assert sorted(cleaned) == ['a', 'b', 'c']
        assert not client.is_closed


@pytest.mark.asyncio
@pytest.mark.parametrize('texts', [[], ['one'], ['one', 'two', 'one']])
async def test_success_preserves_input_order_and_duplicate_positions(texts):
    async def handle(request):
        prompt = json.loads(request.content)['prompt']
        if prompt == 'one':
            await asyncio.sleep(0)
        return httpx.Response(200, json={'embedding': [1.0 if prompt == 'one' else 2.0]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        model = OllamaEmbedding(embedding_model_name='test', client=object(), async_client=client)
        result = await model.async_get_embeddings(texts)
        assert result == [[1.0 if text == 'one' else 2.0] for text in texts]
        assert not client.is_closed


@pytest.mark.asyncio
async def test_failed_batch_does_not_cancel_unrelated_task():
    unrelated = asyncio.create_task(asyncio.Event().wait())

    async def handle(request):
        return httpx.Response(500)

    try:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            model = OllamaEmbedding(embedding_model_name='test', client=object(), async_client=client)
            with pytest.raises(Exception, match='Failed to get embeddings'):
                await model.async_get_embeddings(['a', 'b'])
            assert not unrelated.done()
    finally:
        unrelated.cancel()
        await asyncio.gather(unrelated, return_exceptions=True)


@pytest.mark.asyncio
async def test_client_remains_reusable_after_failure():
    calls = 0

    async def handle(request):
        nonlocal calls
        calls += 1
        return httpx.Response(500) if calls == 1 else httpx.Response(200, json={'embedding': [0.5]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        model = OllamaEmbedding(embedding_model_name='test', client=object(), async_client=client)
        with pytest.raises(Exception, match='Failed to get embeddings'):
            await model.async_get_embeddings(['first'])
        assert await model.async_get_embeddings(['second']) == [[0.5]]
