"""Retain each query row from native Chroma batched vector searches."""
import chromadb
from chromadb.api.client import SharedSystemClient
from chromadb.config import Settings
import pytest

from agentuniverse.agent.action.knowledge.store.chroma_store import ChromaStore
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


@pytest.fixture
def store(tmp_path):
    client = chromadb.PersistentClient(path=str(tmp_path), settings=Settings(anonymized_telemetry=False))
    collection = client.create_collection('batch_query_test', embedding_function=None)
    instance = ChromaStore(collection=collection)
    instance.insert_document([
        Document(id=name, text=name, embedding=vector, metadata={'label': name})
        for name, vector in [('positive', [1., 0.]), ('middle', [0., 1.]), ('negative', [-1., 0.])]
    ])
    try:
        yield instance
    finally:
        client.delete_collection(collection.name)
        client._system.stop()
        systems = getattr(SharedSystemClient, '_identifier_to_system', None)
        if systems is None:  # Chroma 0.4.x uses this spelling.
            systems = SharedSystemClient._identifer_to_system
        systems.pop(client._identifier, None)


@pytest.mark.parametrize('query_count', [1, 2])
@pytest.mark.parametrize('top_k', [1, 2])
def test_public_query_keeps_all_query_rows(store, query_count, top_k):
    vectors = [[1., 0.], [-1., 0.]][:query_count]
    native = store.collection.query(query_embeddings=vectors, n_results=top_k)
    expected = [identifier for row in native['ids'] for identifier in row]
    result = store.query(Query(embeddings=vectors, similarity_top_k=top_k))
    assert [doc.id for doc in result] == expected
    assert [doc.text for doc in result] == expected
    assert [doc.metadata['label'] for doc in result] == expected


@pytest.mark.parametrize('include_embeddings', [True, False])
def test_conversion_keeps_aligned_native_vectors_and_metadata(store, include_embeddings):
    include = ['documents', 'metadatas']
    if include_embeddings:
        include.append('embeddings')
    native = store.collection.query(query_embeddings=[[1., 0.], [-1., 0.]], n_results=1, include=include)
    result = store.to_documents(native)
    assert [doc.id for doc in result] == ['positive', 'negative']
    assert [doc.metadata['label'] for doc in result] == ['positive', 'negative']
    expected = [[1., 0.], [-1., 0.]] if include_embeddings else [[], []]
    assert [doc.embedding for doc in result] == expected
