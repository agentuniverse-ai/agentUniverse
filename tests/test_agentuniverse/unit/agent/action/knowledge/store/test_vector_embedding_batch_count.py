"""Reject wrong embedding counts before assigning vectors to source documents."""
from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.pgvector_store import PGVectorStore
from agentuniverse.agent.action.knowledge.store.redis_vector_store import RedisVectorStore


@pytest.mark.parametrize('store_class', [PGVectorStore, RedisVectorStore])
@pytest.mark.parametrize('returned_count', [0, 1, 3])
@pytest.mark.parametrize('asynchronous', [False, True])
@pytest.mark.asyncio
async def test_wrong_count_preserves_documents_before_backend_io(monkeypatch, store_class, returned_count, asynchronous):
    store = store_class(embedding_model='batch_model')
    docs = [Document(id='first', text='First'),
            Document(id='existing', text='Existing', embedding=[9.0, 9.0]),
            Document(id='second', text='Second')]
    original = [doc.model_dump() for doc in docs]
    batches = []

    def embed(texts):
        batches.append(texts)
        return [[float(i), 1.0] for i in range(returned_count)]

    monkeypatch.setattr(EmbeddingManager(), 'get_instance_obj',
                        lambda *args, **kwargs: SimpleNamespace(get_embeddings=embed))
    with pytest.raises(ValueError):
        if asynchronous:
            await store.async_upsert_document(docs)
        else:
            store.upsert_document(docs)
    assert [doc.model_dump() for doc in docs] == original
    assert batches == [['First', 'Second']]
    assert store.client is None
    assert store.async_client is None


@pytest.mark.parametrize('store_class', [PGVectorStore, RedisVectorStore])
def test_matching_batch_assigns_only_missing_embeddings(monkeypatch, store_class):
    store = store_class(embedding_model='batch_model')
    docs = [Document(id='first', text='First'),
            Document(id='existing', text='Existing', embedding=[9.0, 9.0]),
            Document(id='second', text='Second')]
    monkeypatch.setattr(EmbeddingManager(), 'get_instance_obj',
                        lambda *args, **kwargs: SimpleNamespace(
                            get_embeddings=lambda texts: [[1.0, 0.0], [0.0, 1.0]]))
    vectors = store._vectors_for_documents(docs)
    assert vectors == [[1.0, 0.0], [9.0, 9.0], [0.0, 1.0]]
    assert [doc.embedding for doc in docs] == vectors
