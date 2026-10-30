"""Framework text roles must not leak into OpenAI SDK request parameters."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch
import pytest
from agentuniverse.agent.action.knowledge.embedding.openai_embedding import OpenAIEmbedding
from agentuniverse.agent.action.knowledge.store.pgvector_store import PGVectorStore
from agentuniverse.agent.action.knowledge.store.query import Query

MODULE = 'agentuniverse.agent.action.knowledge.embedding.openai_embedding'


@pytest.mark.parametrize('role', ['query', 'document'])
@pytest.mark.parametrize('asynchronous', [False, True])
def test_role_is_accepted_without_forwarding(role, asynchronous):
    processor = OpenAIEmbedding(embedding_model_name='model', openai_api_key='test', dimensions=2)
    sdk = Mock()
    response = SimpleNamespace(data=[SimpleNamespace(embedding=[1., 2.])])
    sdk.embeddings.create = AsyncMock(return_value=response) if asynchronous else Mock(return_value=response)
    with patch(MODULE + ('.AsyncOpenAI' if asynchronous else '.OpenAI'), return_value=sdk):
        if asynchronous:
            result = asyncio.run(processor.async_get_embeddings(['hello'], text_type=role))
        else:
            result = processor.get_embeddings(['hello'], text_type=role)
    assert result == [[1., 2.]]
    sdk.embeddings.create.assert_called_once_with(input=['hello'], model='model', dimensions=2)


def test_pgvector_managed_query_calls_real_embedding():
    processor = OpenAIEmbedding(embedding_model_name='model', openai_api_key='test')
    sdk = Mock()
    sdk.embeddings.create.return_value = SimpleNamespace(data=[SimpleNamespace(embedding=[1., 2.])])
    store = PGVectorStore(embedding_model='test', dimensions=2)
    with patch(MODULE + '.OpenAI', return_value=sdk), \
         patch('agentuniverse.agent.action.knowledge.store.pgvector_store.EmbeddingManager') as manager:
        manager.return_value.get_instance_obj.return_value = processor
        assert store._embedding_for_query(Query(query_str='hello')) == [1., 2.]
