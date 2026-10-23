"""Scoped memory deletion uses valid Chroma predicates and preserves other scopes."""
import socket
import uuid
from unittest.mock import Mock

import pytest

chromadb = pytest.importorskip("chromadb")
from chromadb.api.client import SharedSystemClient  # noqa: E402
from chromadb.config import Settings  # noqa: E402

from agentuniverse.agent.memory.memory_storage import chroma_memory_storage as module  # noqa: E402
from agentuniverse.agent.memory.message import Message  # noqa: E402


@pytest.fixture
def storage(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("offline")

    monkeypatch.setattr(socket.socket, "connect", no_network)
    monkeypatch.setattr(socket, "getaddrinfo", no_network)
    # chromadb caches one process-global system per identifier and refuses a
    # second one whose Settings differ. Every non-persistent client shares the
    # identifier "ephemeral", so another module's client makes this creation
    # raise ValueError. Reset the cache so each test owns a clean system.
    SharedSystemClient.clear_system_cache()
    client = chromadb.EphemeralClient(Settings(anonymized_telemetry=False))
    collection = client.create_collection("scoped_delete_" + uuid.uuid4().hex, embedding_function=None)
    manager = Mock()
    manager.get_instance_obj.return_value.get_embeddings.return_value = [[1.0, 0.0]]
    monkeypatch.setattr(module, "EmbeddingManager", lambda: manager)
    instance = module.ChromaMemoryStorage(embedding_model="offline")
    instance._collection = collection
    for identity, session, agent in [
        ("match", "session", "agent"),
        ("other_agent", "session", "other"),
        ("other_session", "other", "agent"),
        ("neither", "other", "other"),
    ]:
        instance.add([Message(id=identity, content=identity)], session_id=session, agent_id=agent)
    yield instance, collection
    client.delete_collection(collection.name)


@pytest.mark.parametrize("kwargs,remaining", [
    ({"session_id": "session", "agent_id": "agent"}, {"other_agent", "other_session", "neither"}),
    ({"session_id": "session"}, {"other_session", "neither"}),
    ({"agent_id": "agent"}, {"other_agent", "neither"}),
    ({}, {"match", "other_agent", "other_session", "neither"}),
    ({"session_id": "missing", "agent_id": "agent"}, {"match", "other_agent", "other_session", "neither"}),
    ({"session_id": "", "agent_id": "agent"}, {"match", "other_agent", "other_session", "neither"}),
])
def test_delete_only_matching_scope(storage, kwargs, remaining):
    instance, collection = storage
    instance.delete(**kwargs)
    assert set(collection.get()["ids"]) == remaining
