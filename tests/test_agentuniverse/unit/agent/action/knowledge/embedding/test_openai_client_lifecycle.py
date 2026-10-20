"""Client ownership and loop scope for repeated embedding calls."""
import asyncio
from types import SimpleNamespace
from unittest.mock import Mock, AsyncMock, patch
import pytest
from agentuniverse.agent.action.knowledge.embedding.openai_embedding import OpenAIEmbedding

MODULE = 'agentuniverse.agent.action.knowledge.embedding.openai_embedding'


def sdk(async_client=False):
    client = Mock()
    response = SimpleNamespace(data=[SimpleNamespace(embedding=[1., 2.])])
    client.embeddings.create = AsyncMock(return_value=response) if async_client else Mock(return_value=response)
    if async_client:
        client.close = AsyncMock()
    return client


def test_sync_reuses_owned_client_and_reopens_after_close():
    client = sdk()
    embedding = OpenAIEmbedding(embedding_model_name='model', openai_api_key='test')
    with patch(MODULE + '.OpenAI', return_value=client) as factory:
        for _ in range(3):
            assert embedding.get_embeddings(['hello']) == [[1., 2.]]
        factory.assert_called_once()
        embedding.close()
        embedding.close()
        client.close.assert_called_once()
        embedding.get_embeddings(['again'])
        assert factory.call_count == 2
        embedding.close()


def test_injected_clients_are_preserved_and_not_closed():
    sync, async_client = sdk(), sdk(True)
    embedding = OpenAIEmbedding(embedding_model_name='model', client=sync, async_client=async_client)
    async def run():
        assert await embedding.async_get_embeddings(['hello']) == [[1., 2.]]
        await embedding.aclose()
    with patch(MODULE + '.OpenAI') as sync_factory, patch(MODULE + '.AsyncOpenAI') as async_factory:
        assert embedding.get_embeddings(['hello']) == [[1., 2.]]
        embedding.close()
        asyncio.run(run())
    sync_factory.assert_not_called()
    async_factory.assert_not_called()
    sync.close.assert_not_called()
    async_client.close.assert_not_called()
    assert embedding.client is sync and embedding.async_client is async_client


def test_async_reuse_and_close_on_operating_loop():
    client = sdk(True)
    embedding = OpenAIEmbedding(embedding_model_name='model', openai_api_key='test')
    async def run():
        with patch(MODULE + '.AsyncOpenAI', return_value=client) as factory:
            for _ in range(3):
                await embedding.async_get_embeddings(['hello'])
            factory.assert_called_once()
            await embedding.aclose()
            await embedding.aclose()
            client.close.assert_awaited_once()
    asyncio.run(run())


def test_owned_async_client_rejects_cross_loop_use_until_closed():
    client = sdk(True)
    embedding = OpenAIEmbedding(embedding_model_name='model', openai_api_key='test')
    first, second = asyncio.new_event_loop(), asyncio.new_event_loop()
    try:
        with patch(MODULE + '.AsyncOpenAI', return_value=client):
            first.run_until_complete(embedding.async_get_embeddings(['one']))
            with pytest.raises(RuntimeError, match='event loop'):
                second.run_until_complete(embedding.async_get_embeddings(['two']))
            first.run_until_complete(embedding.aclose())
            second.run_until_complete(embedding.async_get_embeddings(['three']))
            second.run_until_complete(embedding.aclose())
    finally:
        first.close()
        second.close()


def test_missing_model_does_not_allocate_client():
    embedding = OpenAIEmbedding(openai_api_key='test')
    with patch(MODULE + '.OpenAI') as sync_factory, patch(MODULE + '.AsyncOpenAI') as async_factory:
        with pytest.raises(ValueError):
            embedding.get_embeddings(['hello'])
        with pytest.raises(ValueError):
            asyncio.run(embedding.async_get_embeddings(['hello']))
    sync_factory.assert_not_called()
    async_factory.assert_not_called()


def test_failed_initialization_can_be_retried():
    client = sdk()
    embedding = OpenAIEmbedding(embedding_model_name='model', openai_api_key='test')
    with patch(MODULE + '.OpenAI', side_effect=[RuntimeError('init failed'), client]):
        with pytest.raises(RuntimeError, match='init failed'):
            embedding.get_embeddings(['hello'])
        assert embedding.client is None
        assert embedding.get_embeddings(['hello']) == [[1., 2.]]
        embedding.close()


def test_async_close_failure_retains_handle_for_retry():
    client = sdk(True)
    client.close.side_effect = [RuntimeError('close failed'), None]
    embedding = OpenAIEmbedding(embedding_model_name='model', openai_api_key='test')
    async def run():
        with patch(MODULE + '.AsyncOpenAI', return_value=client):
            await embedding.async_get_embeddings(['hello'])
            with pytest.raises(RuntimeError, match='close failed'):
                await embedding.aclose()
            assert embedding.async_client is client
            await embedding.aclose()
            assert embedding.async_client is None
    asyncio.run(run())
