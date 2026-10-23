"""A memory store must support reading before its first stored turn."""
from contextlib import closing
from unittest.mock import Mock

import pytest

pytest.importorskip("qdrant_client")
from qdrant_client import QdrantClient

from agentuniverse.agent.memory.memory_storage.qdrant_memory_storage import QdrantMemoryStorage


@pytest.mark.parametrize("query", ["", "first question"])
def test_first_read_returns_empty_without_creating_collection(query, monkeypatch):
    with closing(QdrantClient(":memory:")) as client:
        storage = QdrantMemoryStorage(client=client, embedding_model="fake")
        from agentuniverse.agent.memory.memory_storage.qdrant_memory_storage import EmbeddingManager
        monkeypatch.setattr(EmbeddingManager(), "get_instance_obj", lambda name: Mock(get_embeddings=Mock(return_value=[[1.0, 0.0]])))
        assert storage.get(session_id="first-session", input=query) == []
        assert not client.collection_exists("memory")


def test_collection_lookup_errors_are_not_suppressed(monkeypatch):
    with closing(QdrantClient(":memory:")) as client:
        storage = QdrantMemoryStorage(client=client)
        failure = RuntimeError("connection unavailable")
        monkeypatch.setattr(client, "collection_exists", Mock(side_effect=failure))
        with pytest.raises(RuntimeError) as caught:
            storage.get(session_id="first-session")
        assert caught.value is failure


def test_first_read_does_not_prevent_later_add(monkeypatch):
    from agentuniverse.agent.memory.memory_storage.qdrant_memory_storage import EmbeddingManager
    from agentuniverse.agent.memory.message import Message

    with closing(QdrantClient(":memory:")) as client:
        storage = QdrantMemoryStorage(client=client, embedding_model="fake")
        monkeypatch.setattr(EmbeddingManager(), "get_instance_obj", lambda name: Mock(get_embeddings=Mock(return_value=[[1.0, 0.0]])))
        assert storage.get(session_id="new") == []
        storage.add([Message(content="first turn")], session_id="new")
        assert [m.content for m in storage.get(session_id="new")] == ["first turn"]
