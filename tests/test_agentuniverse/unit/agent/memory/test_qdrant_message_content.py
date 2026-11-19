"""Content round trips through a real, isolated Qdrant local database."""

from copy import deepcopy
from types import SimpleNamespace
from uuid import UUID

import pytest

pytest.importorskip("qdrant_client")
from qdrant_client import QdrantClient  # noqa: E402

from agentuniverse.agent.memory.message import Message  # noqa: E402
from agentuniverse.agent.memory.memory_storage import qdrant_memory_storage as module  # noqa: E402


@pytest.fixture
def storage(monkeypatch):
    embedding_inputs = []

    def embed(texts):
        embedding_inputs.extend(texts)
        return [[1.0, 0.0] for _ in texts]

    model = SimpleNamespace(get_embeddings=embed)
    manager = SimpleNamespace(get_instance_obj=lambda name: model)
    monkeypatch.setattr(module, "EmbeddingManager", lambda: manager)
    client = QdrantClient(":memory:")
    store = module.QdrantMemoryStorage(client=client, embedding_model="test-embedding")
    yield store, embedding_inputs
    store.client.close()


@pytest.mark.parametrize("content", [
    "original message 中文", "", None,
    [{"type": "text", "text": "original structured text"}],
])
@pytest.mark.parametrize("metadata_content", ["metadata preview", {"preview": "not a message"}])
def test_metadata_cannot_replace_message_content(storage, content, metadata_content):
    store, embedded = storage
    message = Message(
        id=str(UUID(int=1)), content=content, type="human", source="chat",
        metadata={"content": metadata_content, "topic": "example"},
    )
    original = deepcopy(message.model_dump())
    store.add([message], session_id="session", agent_id="agent")
    restored = store.get(session_id="session", agent_id="agent")
    assert len(restored) == 1
    assert restored[0].content == content
    assert restored[0].metadata["topic"] == "example"
    assert restored[0].source == "chat"
    assert restored[0].type == "human"
    assert embedded == [str(content)]
    assert message.model_dump() == original
    point = store.client.retrieve(store.collection_name, ids=[message.id])[0]
    assert point.payload["content"] == content


@pytest.mark.parametrize("metadata", [None, {}, {"topic": "example"}])
def test_messages_without_content_collision_are_unchanged(storage, metadata):
    store, _ = storage
    message = Message(id=str(UUID(int=2)), content="original", metadata=metadata)
    store.add([message])
    restored = store.get()
    assert len(restored) == 1
    assert restored[0].content == "original"
    for key, value in (metadata or {}).items():
        assert restored[0].metadata[key] == value


def test_same_id_update_replaces_actual_content(storage):
    store, _ = storage
    message_id = str(UUID(int=3))
    store.add([Message(id=message_id, content="before", metadata={"content": "old preview"})])
    store.add([Message(id=message_id, content="after", metadata={"content": "new preview"})])
    restored = store.get()
    assert [(message.id, message.content) for message in restored] == [(message_id, "after")]
    assert store.client.count(store.collection_name).count == 1


def test_mixed_batch_does_not_lose_messages_on_metadata_collision(storage):
    store, _ = storage
    messages = [
        Message(id=str(UUID(int=number)), content=f"message-{number}", metadata=metadata)
        for number, metadata in enumerate([
            {}, {"content": {"preview": "dictionary"}}, {"content": "preview"},
        ], start=10)
    ]
    store.add(messages, session_id="session")
    restored = store.get(session_id="session")
    assert {message.id: message.content for message in restored} == {
        message.id: message.content for message in messages
    }


def test_session_and_agent_filters_still_apply(storage):
    store, _ = storage
    for number, (session, agent) in enumerate([
        ("selected", "selected"), ("other", "selected"), ("selected", "other"),
    ], start=20):
        store.add([Message(
            id=str(UUID(int=number)), content=f"message-{number}",
            metadata={"content": "preview"},
        )], session_id=session, agent_id=agent)
    restored = store.get(session_id="selected", agent_id="selected")
    assert [message.content for message in restored] == ["message-20"]


def test_content_survives_local_database_reopen(storage, tmp_path):
    store, _ = storage
    store.client.close()
    store.client = QdrantClient(path=str(tmp_path / "qdrant"))
    store.add([Message(
        id=str(UUID(int=30)), content="persisted message",
        metadata={"content": "preview", "topic": "persistent"},
    )])
    store.client.close()
    store.client = QdrantClient(path=str(tmp_path / "qdrant"))
    restored = store.get()
    assert [message.content for message in restored] == ["persisted message"]
    assert restored[0].metadata["topic"] == "persistent"


def test_empty_batch_does_not_create_a_collection(storage):
    store, _ = storage
    store.add([])
    assert not store.client.collection_exists(store.collection_name)
