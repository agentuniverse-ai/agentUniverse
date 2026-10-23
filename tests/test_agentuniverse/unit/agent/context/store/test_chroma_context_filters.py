"""Exercise compound context filters against the pinned Chroma API."""
import uuid

import pytest

chromadb = pytest.importorskip('chromadb')
from chromadb.api.client import SharedSystemClient
from chromadb.config import Settings

from agentuniverse.agent.context.context_model import ContextPriority, ContextSegment, ContextType
from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


class ConstantEmbedding:
    def __call__(self, input):
        return [[1., 0.] for _ in input]


@pytest.fixture
def store():
    # chromadb caches one process-global system per identifier and refuses a
    # second one whose Settings differ. Every non-persistent client shares the
    # identifier "ephemeral", so another module's client makes this creation
    # raise ValueError. Reset the cache so each test owns a clean system.
    SharedSystemClient.clear_system_cache()
    client = chromadb.EphemeralClient(Settings(anonymized_telemetry=False))
    collection = client.create_collection('filters_' + uuid.uuid4().hex, embedding_function=ConstantEmbedding())
    instance = ChromaContextStore()
    instance._collection = collection
    for session, identifier, kind, priority in [
        ('one', 'match', ContextType.CONVERSATION, ContextPriority.HIGH),
        ('one', 'wrong_type', ContextType.BACKGROUND, ContextPriority.HIGH),
        ('one', 'wrong_priority', ContextType.CONVERSATION, ContextPriority.LOW),
        ('two', 'other_session', ContextType.CONVERSATION, ContextPriority.HIGH),
    ]:
        instance.add([ContextSegment(id=identifier, type=kind, priority=priority,
                                     content=identifier, tokens=1)], session_id=session)
    yield instance
    client.delete_collection(collection.name)


@pytest.mark.parametrize('filters,expected', [
    ({}, {'match', 'wrong_type', 'wrong_priority'}),
    ({'context_type': ContextType.CONVERSATION}, {'match', 'wrong_priority'}),
    ({'priority': ContextPriority.HIGH}, {'match', 'wrong_type'}),
    ({'context_type': ContextType.CONVERSATION, 'priority': ContextPriority.HIGH}, {'match'}),
])
@pytest.mark.parametrize('operation', ['get', 'search'])
def test_compound_filters_retrieve_only_matching_session(store, filters, expected, operation):
    if operation == 'get':
        result = store.get('one', **filters)
    else:
        result = store.search('query', 'one', top_k=4, **filters)
    assert {segment.id for segment in result} == expected


def test_compound_filters_with_no_matches(store):
    filters = {'context_type': ContextType.TOOL_RESULT, 'priority': ContextPriority.HIGH}
    assert store.get('one', **filters) == []
    assert store.search('query', 'one', **filters) == []
