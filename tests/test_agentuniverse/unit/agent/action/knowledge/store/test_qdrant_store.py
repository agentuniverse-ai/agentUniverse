# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_qdrant_store.py

"""Unit tests for QdrantStore pure behaviors (no live Qdrant server)."""

from types import SimpleNamespace
from unittest import mock

import pytest
from qdrant_client.models import Distance

import agentuniverse.agent.action.knowledge.store.store as store_module
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.qdrant_store import (
    DEFAULT_CONNECTION_ARGS,
    QdrantStore,
)
from agentuniverse.agent.action.knowledge.store.query import Query


@pytest.fixture
def store():
    return QdrantStore()


class TestQdrantStore:
    """Test QdrantStore defaults, metric mapping and no-client behavior."""

    def test_default_attributes(self, store):
        assert store.connection_args is None
        assert store.collection_name == "qdrant_db"
        assert store.distance == "COSINE"
        assert store.embedding_model is None
        assert store.similarity_top_k == 10
        assert store.with_vectors is False
        assert store.client is None
        assert store.VECTOR_NAME == "embedding"

    def test_metric_from_str_mappings(self, store):
        assert store._metric_from_str() == Distance.COSINE
        assert QdrantStore(distance="euclid")._metric_from_str() == \
            Distance.EUCLID
        assert QdrantStore(distance="DOT")._metric_from_str() == Distance.DOT
        assert QdrantStore(distance="MANHATTAN")._metric_from_str() == \
            Distance.MANHATTAN
        assert QdrantStore(distance="unknown")._metric_from_str() == \
            Distance.COSINE

    def test_missing_client_ops_are_noops(self, store):
        assert store.query(Query(query_str="hello")) == []
        store.insert_document([Document(text="hello")])
        store.upsert_document([Document(text="hello")])
        store.update_document([Document(text="hello")])
        store.delete_document("some-id")

    def test_to_documents_none_or_empty(self):
        assert QdrantStore.to_documents(None) == []
        assert QdrantStore.to_documents([]) == []

    def test_to_documents_named_vector_conversion(self):
        point = SimpleNamespace(
            id="point-1",
            payload={"text": "hello qdrant", "metadata": {"src": "test"}},
            vector={"embedding": [0.1, 0.2, 0.3]},
        )
        doc = QdrantStore.to_documents([point])[0]
        assert doc.id == "point-1"
        assert doc.text == "hello qdrant"
        assert doc.metadata == {"src": "test"}
        assert doc.embedding == [0.1, 0.2, 0.3]

    def test_to_documents_missing_payload_or_vector(self):
        empty = QdrantStore.to_documents(
            [SimpleNamespace(id="point-2", payload=None, vector=None)])[0]
        assert empty.text is None
        assert empty.embedding == []
        other = QdrantStore.to_documents(
            [SimpleNamespace(id="point-3", payload={},
                             vector={"other": [9.9]})])[0]
        assert other.embedding == []

    def test_initialize_sets_fields(self, store):
        configer = SimpleNamespace(
            name="qd", description="qd docs",
            connection_args={"host": "h", "port": 1},
            collection_name="coll", distance="DOT",
            embedding_model="emb", similarity_top_k=5, with_vectors=True)
        with mock.patch.object(store_module, "add_post_fork"):
            store.initialize_by_component_configer(configer)
        assert store.name == "qd"
        assert store.connection_args == {"host": "h", "port": 1}
        assert store.collection_name == "coll"
        assert store.distance == "DOT"
        assert store.embedding_model == "emb"
        assert store.similarity_top_k == 5
        assert store.with_vectors is True

    def test_initialize_defaults_connection_args(self, store):
        with mock.patch.object(store_module, "add_post_fork"):
            store.initialize_by_component_configer(
                SimpleNamespace(name="qd", description=None))
        assert store.connection_args == DEFAULT_CONNECTION_ARGS
