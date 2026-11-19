#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/15
# @Author  : dxz0069
# @FileName: test_weaviate_store.py

import os
import sys
import types
import unittest
from unittest.mock import MagicMock

try:
    import weaviate  # noqa: F401

    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    # Inject a minimal fake of the client library so the component's lazy
    # imports resolve and the behavioral tests below still run everywhere;
    # the fake only provides module level symbols, all client behavior is
    # mocked by the tests themselves.
    _fake_weaviate = types.ModuleType("weaviate")
    _fake_weaviate.connect_to_custom = MagicMock()

    class _VectorDistances:
        COSINE = "cosine"
        DOT = "dot"
        L2_SQUARED = "l2-squared"
        MANHATTAN = "manhattan"
        HAMMING = "hamming"

    class _NamedVectorsFactory:
        @staticmethod
        def none(name, vector_index_config=None):
            return {"name": name, "vector_index_config": vector_index_config}

    class _VectorIndexFactory:
        @staticmethod
        def hnsw(**kwargs):
            return {"hnsw": kwargs}

    class _Configure:
        NamedVectors = _NamedVectorsFactory
        VectorIndex = _VectorIndexFactory

    class _AuthApiKey:
        def __init__(self, api_key):
            self.api_key = api_key

    _fake_config = types.ModuleType("weaviate.classes.config")
    _fake_config.VectorDistances = _VectorDistances
    _fake_config.Configure = _Configure
    _fake_classes = types.ModuleType("weaviate.classes")
    _fake_classes.config = _fake_config
    _fake_auth = types.ModuleType("weaviate.auth")
    _fake_auth.AuthApiKey = _AuthApiKey
    _fake_weaviate.classes = _fake_classes
    _fake_weaviate.auth = _fake_auth
    sys.modules.setdefault("weaviate", _fake_weaviate)
    sys.modules.setdefault("weaviate.classes", _fake_classes)
    sys.modules.setdefault("weaviate.classes.config", _fake_config)
    sys.modules.setdefault("weaviate.auth", _fake_auth)

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


class TestWeaviateStore(unittest.TestCase):
    """Test cases for the Weaviate store, run against mocked clients."""

    def setUp(self):
        from agentuniverse.agent.action.knowledge.store.weaviate_store import WeaviateStore
        self.WeaviateStore = WeaviateStore
        self.store = WeaviateStore(collection_name="test_collection")

    def _mock_client(self):
        client = MagicMock()
        client.collections.exists.return_value = False
        self.store.client = client
        return client

    def test_distance_metric_mapping(self):
        from weaviate.classes.config import VectorDistances
        self.assertIs(self.store._distance_metric(), VectorDistances.COSINE)
        euclid = self.WeaviateStore(distance="EUCLID")
        self.assertIs(euclid._distance_metric(), VectorDistances.L2_SQUARED)
        unknown = self.WeaviateStore(distance="unknown")
        self.assertIs(unknown._distance_metric(), VectorDistances.COSINE)

    def test_document_uuid(self):
        document = Document(id="not-a-uuid", text="hello")
        first = self.store._document_uuid(document)
        second = self.store._document_uuid(document)
        self.assertEqual(first, second)
        valid = Document(id="3fa85f64-5717-4562-b3fc-2c963f66afa6", text="hello")
        self.assertEqual(
            self.store._document_uuid(valid),
            "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        )

    def test_insert_document_creates_collection(self):
        client = self._mock_client()
        documents = [Document(id="doc1", text="hello", embedding=[0.1, 0.2])]
        self.store.insert_document(documents)
        client.collections.exists.assert_called_with("test_collection")
        client.collections.create.assert_called_once()
        client.collections.get.assert_called_with("test_collection")
        collection = client.collections.get.return_value
        collection.data.insert.assert_called_once()
        kwargs = collection.data.insert.call_args.kwargs
        self.assertEqual(kwargs["uuid"], self.store._document_uuid(documents[0]))
        self.assertEqual(kwargs["vector"], [0.1, 0.2])
        self.assertEqual(kwargs["properties"]["text"], "hello")

    def test_insert_document_skips_empty_embeddings(self):
        client = self._mock_client()
        documents = [Document(id="doc1", text="no embedding")]
        self.store.insert_document(documents)
        collection = client.collections.get.return_value
        collection.data.insert.assert_not_called()

    def test_upsert_document_uses_replace(self):
        client = self._mock_client()
        documents = [Document(id="doc1", text="hello", embedding=[0.1, 0.2])]
        self.store.upsert_document(documents)
        collection = client.collections.get.return_value
        collection.data.replace.assert_called_once()
        self.assertEqual(
            collection.data.replace.call_args.kwargs["uuid"],
            self.store._document_uuid(documents[0]),
        )

    def test_query(self):
        client = self._mock_client()
        result = MagicMock()
        result.uuid = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        result.properties = {"text": "hello", "metadata": {"k": "v"}}
        result.vector = {"embedding": [0.1, 0.2]}
        client.collections.get.return_value.query.near_vector.return_value = [result]

        query = Query(query_str="hi", embeddings=[[0.1, 0.2]], similarity_top_k=5)
        documents = self.store.query(query)

        near_vector_kwargs = client.collections.get.return_value.query.near_vector.call_args.kwargs
        self.assertEqual(near_vector_kwargs["near_vector"], [0.1, 0.2])
        self.assertEqual(near_vector_kwargs["limit"], 5)
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].text, "hello")
        self.assertEqual(documents[0].metadata, {"k": "v"})
        self.assertEqual(documents[0].embedding, [0.1, 0.2])

    def test_query_without_embeddings(self):
        self._mock_client()
        query = Query(query_str="hi")
        self.assertEqual(self.store.query(query), [])
        self.store.client.collections.get.return_value.query.near_vector.assert_not_called()

    def test_query_without_client(self):
        store = self.WeaviateStore()
        self.assertEqual(store.query(Query(query_str="hi")), [])

    def test_delete_document(self):
        client = self._mock_client()
        self.store.delete_document("3fa85f64-5717-4562-b3fc-2c963f66afa6")
        collection = client.collections.get.return_value
        collection.data.delete_by_id.assert_called_once_with(
            "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        )

    def test_new_client_connection_args(self):
        import weaviate
        store = self.WeaviateStore(
            connection_args={"http_host": "weaviate.example.com", "http_port": 443, "http_secure": True},
            api_key="secret",
        )
        with unittest.mock.patch.object(weaviate, "connect_to_custom") as connect:
            client = store._new_client()
        self.assertIs(client, connect.return_value)
        kwargs = connect.call_args.kwargs
        self.assertEqual(kwargs["http_host"], "weaviate.example.com")
        self.assertEqual(kwargs["http_port"], 443)
        self.assertTrue(kwargs["http_secure"])
        self.assertEqual(kwargs["grpc_host"], "localhost")
        self.assertIsNotNone(kwargs["auth_credentials"])


@unittest.skipUnless(
    WEAVIATE_AVAILABLE and os.environ.get("WEAVIATE_HTTP_HOST"),
    "real integration test: install weaviate-client, start Weaviate "
    "(docker run -p 8080:8080 -p 50051:50051 cr.weaviate.io/semitechnologies/weaviate:latest) "
    "and set WEAVIATE_HTTP_HOST to run",
)
class TestWeaviateStoreIntegration(unittest.TestCase):
    """Integration tests against a real Weaviate server.

    Start a server and set the endpoint to run:
        docker run -d --name weaviate -p 8080:8080 -p 50051:50051 \\
            cr.weaviate.io/semitechnologies/weaviate:latest
        WEAVIATE_HTTP_HOST=localhost python -m pytest \\
            tests/test_agentuniverse/unit/agent/action/knowledge/store/test_weaviate_store.py
    """

    def test_roundtrip(self):
        from agentuniverse.agent.action.knowledge.store.weaviate_store import WeaviateStore
        import uuid as uuid_module

        collection = "test_" + uuid_module.uuid4().hex[:8]
        store = WeaviateStore(
            collection_name=collection,
            connection_args={
                "http_host": os.environ["WEAVIATE_HTTP_HOST"],
                "http_port": int(os.environ.get("WEAVIATE_HTTP_PORT", "8080")),
                "http_secure": os.environ.get("WEAVIATE_HTTP_SECURE", "false") == "true",
                "grpc_host": os.environ.get("WEAVIATE_GRPC_HOST", os.environ["WEAVIATE_HTTP_HOST"]),
                "grpc_port": int(os.environ.get("WEAVIATE_GRPC_PORT", "50051")),
                "grpc_secure": os.environ.get("WEAVIATE_HTTP_SECURE", "false") == "true",
            },
        )
        store.client = store._new_client()
        try:
            documents = [
                Document(id="doc1", text="hello world", embedding=[1.0, 0.0], metadata={"k": "v"}),
                Document(id="doc2", text="goodbye world", embedding=[0.0, 1.0]),
            ]
            store.insert_document(documents)
            results = store.query(Query(query_str="hi", embeddings=[[1.0, 0.0]], similarity_top_k=1))
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].text, "hello world")
            store.upsert_document([Document(id="doc1", text="updated", embedding=[1.0, 0.1])])
            results = store.query(Query(query_str="hi", embeddings=[[1.0, 0.0]], similarity_top_k=10))
            texts = {document.text for document in results}
            self.assertIn("updated", texts)
            self.assertNotIn("hello world", texts)
            store.delete_document("doc1")
            results = store.query(Query(query_str="hi", embeddings=[[1.0, 0.0]], similarity_top_k=10))
            self.assertEqual([document.text for document in results], ["goodbye world"])
        finally:
            store.client.collections.delete(collection)
            store.client.close()


if __name__ == "__main__":
    unittest.main()
