#!/usr/bin/env python3

"""Chroma 1.x integration tests for agentUniverse storage components."""

import shutil
import tempfile
import unittest
import uuid
from unittest.mock import patch

from chromadb.api.client import SharedSystemClient

from agentuniverse.agent.action.knowledge.store.chroma_store import ChromaStore
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.context.context_model import ContextPriority, ContextSegment, ContextType
from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore
from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.conversation_memory.memory_storage.chroma_conversation_memory_storage import (
    ChromaConversationMemoryStorage,
)
from agentuniverse.agent.memory.memory_storage.chroma_memory_storage import ChromaMemoryStorage
from agentuniverse.agent.memory.message import Message


class _FakeEmbeddingModel:
    """Return deterministic two-dimensional embeddings."""

    @staticmethod
    def get_embeddings(value, **_kwargs):
        if isinstance(value, list):
            return [[1.0, 0.0] for _item in value]
        return [1.0, 0.0]


class _FakeEmbeddingManager:
    """Return the deterministic embedding model for any component name."""

    @staticmethod
    def get_instance_obj(_name):
        return _FakeEmbeddingModel()


class ChromaCompatibilityTest(unittest.TestCase):
    """Exercise Chroma-backed knowledge, memory, and context operations."""

    def setUp(self) -> None:
        self.temp_paths = []

    def tearDown(self) -> None:
        SharedSystemClient.clear_system_cache()
        for path in self.temp_paths:
            shutil.rmtree(path, ignore_errors=True)

    def _temp_path(self) -> str:
        path = tempfile.mkdtemp(prefix="agentuniverse-chroma-")
        self.temp_paths.append(path)
        return path

    @staticmethod
    def _collection_name(prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex}"

    def test_knowledge_store_in_memory_crud(self) -> None:
        store = ChromaStore(collection_name=self._collection_name("knowledge"))
        client = store._new_client()
        store.insert_document(
            [
                Document(
                    id="doc-1",
                    text="Python 3.12 compatible storage",
                    embedding=[1.0, 0.0],
                    metadata={"source": "test"},
                )
            ]
        )

        result = store.query(Query(query_str="compatibility", embeddings=[[1.0, 0.0]], similarity_top_k=1))

        self.assertEqual([document.id for document in result], ["doc-1"])
        client.delete_collection(store.collection_name)

    def test_knowledge_store_persists_across_clients(self) -> None:
        persist_path = self._temp_path()
        collection_name = self._collection_name("persistent")
        first_store = ChromaStore(collection_name=collection_name, persist_path=persist_path)
        first_store._new_client()
        first_store.insert_document(
            [
                Document(
                    id="doc-1",
                    text="persistent document",
                    embedding=[1.0, 0.0],
                    metadata={"source": "test"},
                )
            ]
        )

        second_store = ChromaStore(collection_name=collection_name, persist_path=persist_path)
        client = second_store._new_client()
        result = second_store.query(Query(query_str="persistent", embeddings=[[1.0, 0.0]], similarity_top_k=1))

        self.assertEqual([document.id for document in result], ["doc-1"])
        client.delete_collection(collection_name)

    @patch(
        "agentuniverse.agent.memory.memory_storage.chroma_memory_storage.EmbeddingManager",
        return_value=_FakeEmbeddingManager(),
    )
    def test_memory_storage_adds_and_retrieves_messages(self, _embedding_model) -> None:
        storage = ChromaMemoryStorage(
            collection_name=self._collection_name("memory"),
            persist_path=None,
            embedding_model="fake_embedding",
        )
        client = storage._init_collection()
        storage.add(
            [Message(id="message-1", content="remember this", source="user", type="human")],
            session_id="session-1",
            agent_id="agent-1",
        )

        result = storage.get(session_id="session-1", input="remember", top_k=1)

        self.assertEqual([message.id for message in result], ["message-1"])
        client.delete_collection(storage.collection_name)

    @patch(
        "agentuniverse.agent.memory.conversation_memory.memory_storage."
        "chroma_conversation_memory_storage.EmbeddingManager",
        return_value=_FakeEmbeddingManager(),
    )
    def test_conversation_memory_round_trip(self, _embedding_model) -> None:
        storage = ChromaConversationMemoryStorage(
            collection_name=self._collection_name("conversation"),
            persist_path=None,
            embedding_model="fake_embedding",
        )
        client = storage._init_collection()
        message = ConversationMessage(
            id="conversation-1",
            trace_id="trace-1",
            conversation_id="session-1",
            source="user",
            source_type="user",
            target="agent-1",
            target_type="agent",
            type="input",
            content="hello agent",
            metadata={"params": "{}", "prefix": "", "pair_id": "pair-1"},
        )
        storage.add([message], session_id="session-1")

        result = storage.get(session_id="session-1", top_k=1)

        self.assertEqual([item.id for item in result], ["conversation-1"])
        client.delete_collection(storage.collection_name)

    @patch(
        "agentuniverse.llm.llm_manager.LLMManager.get_instance_obj",
        return_value=_FakeEmbeddingModel(),
    )
    def test_context_store_custom_embedding_round_trip(self, _embedding_model) -> None:
        store = ChromaContextStore(
            collection_name=self._collection_name("context"),
            persist_directory=self._temp_path(),
            embedding_model_name="fake_embedding",
            similarity_threshold=0.0,
        )
        store.initialize_by_component_configer(object())
        segment = ContextSegment(
            id="segment-1",
            type=ContextType.REFERENCE,
            priority=ContextPriority.HIGH,
            content="Python 3.12 context",
            tokens=4,
        )
        store.add([segment], session_id="session-1")

        reopened_store = ChromaContextStore(
            collection_name=store.collection_name,
            persist_directory=store.persist_directory,
            embedding_model_name="fake_embedding",
            similarity_threshold=0.0,
        )
        reopened_store.initialize_by_component_configer(object())
        retrieved = reopened_store.get("session-1")
        searched = reopened_store.search("Python context", "session-1", top_k=1)

        self.assertEqual([item.id for item in retrieved], ["segment-1"])
        self.assertEqual([item.id for item in searched], ["segment-1"])
        reopened_store.clear_all()


if __name__ == "__main__":
    unittest.main()
