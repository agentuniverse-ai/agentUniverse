"""Ordinary optional conversation attributes can be persisted by Chroma."""
import socket
import uuid
from copy import deepcopy
from unittest.mock import Mock

import pytest

chromadb = pytest.importorskip("chromadb")
from chromadb.config import Settings  # noqa: E402

from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage  # noqa: E402
from agentuniverse.agent.memory.conversation_memory.memory_storage import chroma_conversation_memory_storage as module  # noqa: E402
from agentuniverse.agent.memory.message import Message  # noqa: E402


@pytest.fixture
def storage(monkeypatch, tmp_path):
    def no_network(*args, **kwargs):
        raise AssertionError("offline")

    monkeypatch.setattr(socket.socket, "connect", no_network)
    monkeypatch.setattr(socket, "getaddrinfo", no_network)
    # Ephemeral clients share process-wide settings, even after collection deletion.
    # A per-test path keeps these telemetry settings isolated from other stores.
    client = chromadb.PersistentClient(path=str(tmp_path), settings=Settings(anonymized_telemetry=False))
    collection = client.create_collection("nullable_" + uuid.uuid4().hex, embedding_function=None)
    manager = Mock()
    manager.get_instance_obj.return_value.get_embeddings.return_value = [[1.0, 0.0]]
    monkeypatch.setattr(module, "EmbeddingManager", lambda: manager)
    instance = module.ChromaConversationMemoryStorage(embedding_model="offline")
    instance._collection = collection
    yield instance, collection
    client.delete_collection(collection.name)


@pytest.mark.parametrize("metadata", [None, {}, {"params": None, "prefix": None, "pair_id": None}])
def test_nullable_conversation_metadata_roundtrips(storage, metadata):
    instance, collection = storage
    message = ConversationMessage(content="hello", metadata=metadata, additional_args={"step": 2})
    original = deepcopy(message.model_dump())
    instance.add([message], session_id="session")
    restored = instance.get(session_id="session")
    assert len(restored) == 1
    assert restored[0].id == message.id
    assert restored[0].content == "hello"
    assert restored[0].additional_args == {"step": 2}
    assert restored[0].source is None and restored[0].target is None
    assert all(value is not None for value in collection.get()["metadatas"][0].values())
    assert message.model_dump() == original


def test_ordinary_message_can_be_converted_and_persisted(storage):
    instance, _ = storage
    instance.add([Message(content="summary", type="human")], session_id="session")
    restored = instance.get(session_id="session")
    assert len(restored) == 1
    assert restored[0].content == "summary"
    assert restored[0].type == "human"


def test_non_null_metadata_including_falsey_values_is_preserved(storage):
    instance, collection = storage
    message = ConversationMessage(
        content="hello", trace_id="trace", source="source", target="target",
        source_type="user", target_type="agent", type="input",
        metadata={"params": 0, "prefix": "", "pair_id": False},
    )
    instance.add([message], session_id="session")
    stored = collection.get()["metadatas"][0]
    assert stored["params"] == 0 and stored["prefix"] == "" and stored["pair_id"] is False
    restored = instance.get(session_id="session")[0]
    assert (restored.source, restored.target, restored.trace_id) == ("source", "target", "trace")
    assert (restored.source_type, restored.target_type, restored.type) == ("user", "agent", "input")
