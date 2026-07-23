#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for WeaviateStore.

All tests mock the weaviate client so no server is required. Covers config
validation, dimension checking, insert/query round-trip, delete, count, and
error paths.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.weaviate_store import WeaviateStore


def _mock_weaviate():
    """Build a mock weaviate module + client for patching sys.modules."""
    mock_mod = MagicMock()
    mock_mod.__version__ = "4.22.0"

    # classes sub-module
    classes = MagicMock()
    classes.config.Configure.VectorIndex.hnsw.return_value = MagicMock()
    classes.config.DataType.TEXT = "TEXT"
    classes.config.Property = MagicMock()
    classes.query.MetadataQuery = MagicMock()
    classes.query.Filter = MagicMock()
    mock_mod.classes = classes

    # AuthApiKey
    mock_mod.auth.AuthApiKey = MagicMock(return_value=MagicMock())

    # connect_to_local returns a mock client
    client = MagicMock()
    collection = MagicMock()
    client.collections.exists.return_value = False
    client.collections.create.return_value = collection
    client.collections.get.return_value = collection
    mock_mod.connect_to_local = MagicMock(return_value=client)
    mock_mod.connect_to_custom = MagicMock(return_value=client)

    return mock_mod, client, collection


class TestWeaviateStoreConfig(unittest.TestCase):

    def test_valid_config_is_accepted(self):
        store = WeaviateStore(
            url="http://localhost:8080",
            collection_name="TestCollection",
            dimensions=128,
            distance="cosine",
        )
        store._validate_config()  # must not raise

    def test_empty_url_rejected(self):
        store = WeaviateStore(url="", collection_name="C")
        with self.assertRaises(ValueError):
            store._validate_config()

    def test_empty_collection_name_rejected(self):
        store = WeaviateStore(url="http://x", collection_name="")
        with self.assertRaises(ValueError):
            store._validate_config()

    def test_invalid_distance_rejected(self):
        store = WeaviateStore(url="http://x", collection_name="C",
                              distance="manhattan_proj")
        with self.assertRaises(ValueError):
            store._validate_config()

    def test_zero_top_k_rejected(self):
        store = WeaviateStore(url="http://x", collection_name="C",
                              similarity_top_k=0)
        with self.assertRaises(ValueError):
            store._validate_config()

    def test_negative_dimensions_rejected(self):
        store = WeaviateStore(url="http://x", collection_name="C",
                              dimensions=-1)
        with self.assertRaises(ValueError):
            store._validate_config()

    def test_l2_and_dot_distances_accepted(self):
        for d in ("l2", "dot", "euclidean"):
            store = WeaviateStore(url="http://x", collection_name="C", distance=d)
            store._validate_config()


class TestWeaviateStoreInsert(unittest.TestCase):

    def setUp(self):
        self.mock_mod, self.mock_client, self.mock_collection = _mock_weaviate()
        self._patcher = patch.dict("sys.modules", {
            "weaviate": self.mock_mod,
            "weaviate.classes": self.mock_mod.classes,
        })
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def _store(self):
        store = WeaviateStore(
            url="http://localhost:8080",
            collection_name="TestCol",
            dimensions=3,
            embedding_model=None,
        )
        store._new_client()
        return store

    def test_insert_single_document(self):
        store = self._store()
        doc = Document(id="d1", text="hello", embedding=[0.1, 0.2, 0.3])
        store.insert_document([doc])
        self.mock_collection.data.insert.assert_called_once()
        call = self.mock_collection.data.insert.call_args
        self.assertEqual(call.kwargs["uuid"], "d1")
        self.assertEqual(call.kwargs["properties"]["text"], "hello")
        self.assertEqual(call.kwargs["vector"], [0.1, 0.2, 0.3])

    def test_insert_dimension_mismatch_raises(self):
        store = self._store()
        docs = [
            Document(id="d1", text="a", embedding=[0.1, 0.2, 0.3]),
            Document(id="d2", text="b", embedding=[0.1, 0.2]),  # dim 2 vs 3
        ]
        with self.assertRaises(ValueError) as ctx:
            store.insert_document(docs)
        self.assertIn("dim", str(ctx.exception).lower())
        self.assertIn("d2", str(ctx.exception))

    def test_insert_empty_list_is_noop(self):
        store = self._store()
        store.insert_document([])
        self.mock_collection.data.insert.assert_not_called()

    def test_insert_skips_doc_without_embedding_when_no_model(self):
        store = self._store()
        store.insert_document([
            Document(id="d1", text="has emb", embedding=[0.1, 0.2, 0.3]),
            Document(id="d2", text="no emb", embedding=[]),
        ])
        # Only the first doc was inserted.
        self.assertEqual(self.mock_collection.data.insert.call_count, 1)


class TestWeaviateStoreQuery(unittest.TestCase):

    def setUp(self):
        self.mock_mod, self.mock_client, self.mock_collection = _mock_weaviate()
        self._patcher = patch.dict("sys.modules", {
            "weaviate": self.mock_mod,
            "weaviate.classes": self.mock_mod.classes,
        })
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def _store(self):
        store = WeaviateStore(
            url="http://localhost:8080",
            collection_name="TestCol",
            dimensions=3,
        )
        store._new_client()
        return store

    def test_query_returns_documents_with_score(self):
        store = self._store()
        # Mock near_vector return.
        obj1 = MagicMock()
        obj1.properties = {
            "text": "result text",
            "metadata_json": json.dumps({"category": "news"}),
        }
        obj1.metadata.distance = 0.15
        obj2 = MagicMock()
        obj2.properties = {"text": "second", "metadata_json": "{}"}
        obj2.metadata.distance = 0.30
        self.mock_collection.query.near_vector.return_value = MagicMock(
            objects=[obj1, obj2])

        results = store.query(Query(embeddings=[[0.1, 0.2, 0.3]],
                                    similarity_top_k=5))
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].text, "result text")
        self.assertEqual(results[0].metadata["category"], "news")
        self.assertEqual(results[0].metadata["score"], 0.15)
        self.assertEqual(results[1].metadata["score"], 0.30)

    def test_query_no_embedding_returns_empty(self):
        store = self._store()
        results = store.query(Query(query_str="", embeddings=[]))
        self.assertEqual(results, [])

    def test_query_corrupt_metadata_json_does_not_crash(self):
        store = self._store()
        obj = MagicMock()
        obj.properties = {"text": "ok", "metadata_json": "not-valid-json{"}
        obj.metadata.distance = 0.1
        self.mock_collection.query.near_vector.return_value = MagicMock(
            objects=[obj])
        results = store.query(Query(embeddings=[[0.1, 0.2, 0.3]]))
        self.assertEqual(len(results), 1)
        # metadata should be empty dict, not crash.
        self.assertEqual(results[0].metadata["score"], 0.1)


class TestWeaviateStoreDeleteAndCount(unittest.TestCase):

    def setUp(self):
        self.mock_mod, self.mock_client, self.mock_collection = _mock_weaviate()
        self._patcher = patch.dict("sys.modules", {
            "weaviate": self.mock_mod,
            "weaviate.classes": self.mock_mod.classes,
        })
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def _store(self):
        store = WeaviateStore(url="http://localhost:8080",
                              collection_name="TestCol", dimensions=3)
        store._new_client()
        return store

    def test_delete_calls_delete_by_id(self):
        store = self._store()
        store.delete_document("doc-123")
        self.mock_collection.data.delete_by_id.assert_called_once_with(
            uuid="doc-123")

    def test_count_returns_total(self):
        store = self._store()
        self.mock_collection.aggregate.over_all.return_value = MagicMock(
            total_count=42)
        self.assertEqual(store.get_document_count(), 42)

    def test_count_on_error_returns_zero(self):
        store = self._store()
        self.mock_collection.aggregate.over_all.side_effect = RuntimeError(
            "connection lost")
        self.assertEqual(store.get_document_count(), 0)

    def test_get_document_by_id(self):
        store = self._store()
        obj = MagicMock()
        obj.properties = {"text": "found", "metadata_json": '{"k":"v"}'}
        self.mock_collection.query.fetch_object_by_id.return_value = obj
        doc = store.get_document_by_id("d1")
        self.assertEqual(doc.text, "found")
        self.assertEqual(doc.metadata, {"k": "v"})

    def test_get_document_by_id_not_found(self):
        store = self._store()
        self.mock_collection.query.fetch_object_by_id.return_value = None
        doc = store.get_document_by_id("missing")
        self.assertIsNone(doc)


class TestWeaviateStoreUrlParsing(unittest.TestCase):

    def test_parse_host(self):
        self.assertEqual(WeaviateStore._parse_host("http://weave.example.com:8080"),
                         "weave.example.com")
        self.assertEqual(WeaviateStore._parse_host("http://localhost:8080"),
                         "localhost")

    def test_parse_port(self):
        self.assertEqual(WeaviateStore._parse_port("http://x:9090"), 9090)
        self.assertEqual(WeaviateStore._parse_port("http://x"), 8080)

    def test_parse_secure(self):
        self.assertTrue(WeaviateStore._parse_secure("https://secure.example.com"))
        self.assertFalse(WeaviateStore._parse_secure("http://insecure.example.com"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
