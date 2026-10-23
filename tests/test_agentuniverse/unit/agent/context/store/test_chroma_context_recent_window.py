"""Select the newest context globally before applying the result limit."""
from datetime import datetime, timedelta

import chromadb
from chromadb.config import Settings
from chromadb.api.client import SharedSystemClient
import pytest

from agentuniverse.agent.context.context_model import ContextMetadata, ContextPriority, ContextSegment, ContextType
from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


class ConstantEmbedding:
    def __call__(self, input):
        return [[1., 0.] for _ in input]


@pytest.fixture
def store(tmp_path):
    client = chromadb.PersistentClient(path=str(tmp_path), settings=Settings(anonymized_telemetry=False))
    collection = client.create_collection('recent_context', embedding_function=ConstantEmbedding())
    instance = ChromaContextStore()
    instance._collection = collection
    start = datetime(2026, 1, 1)
    # Insert out of timestamp order so neither insertion nor ID order is sufficient.
    for name, age in [('a_old', 0), ('b_newest', 3), ('c_middle', 1), ('d_newer', 2)]:
        instance.add([ContextSegment(
            id=name, content=name, tokens=1, type=ContextType.CONVERSATION,
            priority=ContextPriority.HIGH,
            metadata=ContextMetadata(created_at=start + timedelta(days=age)))], session_id='wanted')
    instance.add([ContextSegment(id='other', content='other session', tokens=1,
                                type=ContextType.CONVERSATION,
                                metadata=ContextMetadata(created_at=start + timedelta(days=10)))], session_id='other')
    try:
        yield instance
    finally:
        client.delete_collection(collection.name)
        client._system.stop()
        systems = getattr(SharedSystemClient, '_identifier_to_system', None)
        if systems is None:  # Chroma 0.4.x spells this cache name differently.
            systems = SharedSystemClient._identifer_to_system
        systems.pop(client._identifier, None)


@pytest.mark.parametrize('limit', [1, 2, 3, 10])
@pytest.mark.parametrize('filters', [{}, {'context_type': ContextType.CONVERSATION,
                                        'priority': ContextPriority.HIGH}])
def test_get_returns_newest_matching_context(store, limit, filters):
    result = store.get('wanted', limit=limit, **filters)
    assert [segment.id for segment in result] == ['b_newest', 'd_newer', 'c_middle', 'a_old'][:limit]
    assert all(segment.session_id == 'wanted' for segment in result)


def test_missing_session_stays_empty(store):
    assert store.get('missing', limit=1) == []


@pytest.mark.parametrize('limit', [0, -1, -10])
def test_nonpositive_limit_stays_empty(store, limit):
    assert store.get('wanted', limit=limit) == []
