#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for MongoDBAtlasStore.

All tests mock the pymongo client so no server or network access is
required. Covers config validation, dimension checking, insert / upsert /
query round-trip, delete, count, fetch-by-id, list-ids, and error paths.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.mongodb_atlas_store import \
    MongoDBAtlasStore
from agentuniverse.agent.action.knowledge.store.query import Query


def _mock_pymongo():
    """Build a mock pymongo module + client for patching sys.modules."""
    mock_mod = MagicMock()
    mock_mod.__version__ = "4.6.0"

    client = MagicMock()
    client.admin.command.return_value = {"ok": 1}

    database = MagicMock()
    database.list_collection_names.return_value = ["documents"]
    collection = MagicMock()
    database.__getitem__.return_value = collection
    database.create_collection.return_value = collection
    client.__getitem__.return_value = database

    mock_mod.MongoClient = MagicMock(return_value=client)

    return mock_mod, client, collection


class TestMongoDBAtlasStoreConfig(unittest.TestCase):

    def test_valid_config_is_accepted(self):
        store = MongoDBAtlasStore(
            database_name="db", collection_name="docs",
            dimensions=128, similarity="cosine",
        )
        store._validate_config()

    def test_invalid_similarity_rejected(self):
        store = MongoDBAtlasStore(database_name="db", collection_name="docs",
                                  similarity="manhattan")
        with self.assertRaises(ValueError):
            store._validate_config()

    def test_zero_top_k_rejected(self):
        store = MongoDBAtlasStore(database_name="db", collection_name="docs",
                                  similarity_top_k=0)
        with self.assertRaises(ValueError):
            store._validate_config()

    def test_negative_dimensions_rejected(self):
        store = MongoDBAtlasStore(database_name="db", collection_name="docs",
                                  dimensions=-1)
        with self.assertRaises(ValueError):
            store._validate_config()

    def test_empty_database_name_rejected(self):
        store = MongoDBAtlasStore(database_name="", collection_name="docs")
        with self.assertRaises(ValueError):
            store._validate_config()

    def test_empty_collection_name_rejected(self):
        store = MongoDBAtlasStore(database_name="db", collection_name="")
        with self.assertRaises(ValueError):
            store._validate_config()

    def test_all_supported_similarities_accepted(self):
        for s in ("cosine", "euclidean", "dotProduct", "dotproduct", "dot"):
            store = MongoDBAtlasStore(database_name="db",
                                      collection_name="docs", similarity=s)
            store._validate_config()

    def test_empty_vector_field_rejected(self):
        store = MongoDBAtlasStore(database_name="db", collection_name="docs",
                                  vector_field="")
        with self.assertRaises(ValueError):
            store._validate_config()


class _MongoPatchMixin:

    def setUp(self):
        self.mock_mod, self.mock_client, self.mock_collection = _mock_pymongo()
        self._patcher = patch.dict("sys.modules", {"pymongo": self.mock_mod})
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def _store(self, **overrides):
        params = dict(
            connection_url="mongodb://localhost:27017",
            database_name="test_db",
            collection_name="test_docs",
            dimensions=3,
            embedding_model=None,
        )
        params.update(overrides)
        store = MongoDBAtlasStore(**params)
        store._new_client()
        return store


class TestMongoDBAtlasStoreInsert(_MongoPatchMixin, unittest.TestCase):

    def test_insert_single_document_upserts(self):
        store = self._store()
        doc = Document(id="d1", text="hello", embedding=[0.1, 0.2, 0.3])
        store.insert_document([doc])
        self.mock_collection.replace_one.assert_called_once()
        args = self.mock_collection.replace_one.call_args
        # replace_one is called positionally: replace_one(filter, replacement, upsert=True)
        self.assertEqual(args[0][0], {"_id": "d1"})
        replacement = args[0][1]
        self.assertEqual(replacement["_id"], "d1")
        self.assertEqual(replacement["text"], "hello")
        self.assertEqual(replacement["embedding"], [0.1, 0.2, 0.3])
        self.assertTrue(args.kwargs.get("upsert"))

    def test_upsert_dimension_mismatch_raises(self):
        store = self._store()
        docs = [
            Document(id="d1", text="a", embedding=[0.1, 0.2, 0.3]),
            Document(id="d2", text="b", embedding=[0.1, 0.2]),
        ]
        with self.assertRaises(ValueError) as ctx:
            store.upsert_document(docs)
        self.assertIn("dimension", str(ctx.exception).lower())

    def test_insert_empty_list_is_noop(self):
        store = self._store()
        store.insert_document([])
        self.mock_collection.replace_one.assert_not_called()

    def test_update_document_delegates_to_upsert(self):
        store = self._store()
        doc = Document(id="d1", text="updated", embedding=[0.1, 0.2, 0.3])
        store.update_document([doc])
        self.mock_collection.replace_one.assert_called_once()


class TestMongoDBAtlasStoreQuery(_MongoPatchMixin, unittest.TestCase):

    def test_query_returns_documents_with_score(self):
        store = self._store()
        self.mock_collection.aggregate.return_value = iter([
            {"_id": "m1", "text": "result",
             "metadata_json": json.dumps({"k": "v"}), "score": 0.95},
            {"_id": "m2", "text": "second",
             "metadata_json": "{}", "score": 0.80},
        ])
        results = store.query(
            Query(embeddings=[[0.1, 0.2, 0.3]], similarity_top_k=5))
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].text, "result")
        self.assertEqual(results[0].metadata["k"], "v")
        self.assertEqual(results[0].metadata["score"], 0.95)

    def test_query_builds_vector_search_pipeline(self):
        store = self._store()
        self.mock_collection.aggregate.return_value = iter([])
        store.query(Query(embeddings=[[0.1, 0.2, 0.3]], similarity_top_k=4))
        pipeline = self.mock_collection.aggregate.call_args[0][0]
        self.assertIn("$vectorSearch", pipeline[0])
        vs = pipeline[0]["$vectorSearch"]
        self.assertEqual(vs["limit"], 4)
        self.assertEqual(vs["path"], "embedding")
        self.assertGreaterEqual(vs["numCandidates"], 4)

    def test_query_with_metadata_filter_adds_filter(self):
        store = self._store()
        self.mock_collection.aggregate.return_value = iter([])
        store.query(Query(embeddings=[[0.1, 0.2, 0.3]]),
                    metadata_filter={"tenant": "acme"})
        pipeline = self.mock_collection.aggregate.call_args[0][0]
        vs = pipeline[0]["$vectorSearch"]
        self.assertIn("filter", vs)

    def test_query_invalid_filter_type_raises(self):
        store = self._store()
        with self.assertRaises(TypeError):
            store.query(Query(embeddings=[[0.1, 0.2, 0.3]]),
                        metadata_filter="not-a-dict")

    def test_query_no_embedding_and_no_model_raises(self):
        store = self._store()
        with self.assertRaises(ValueError):
            store.query(Query(query_str="hi", embeddings=[]))

    def test_query_handles_corrupt_metadata_gracefully(self):
        store = self._store()
        self.mock_collection.aggregate.return_value = iter([
            {"_id": "m1", "text": "ok",
             "metadata_json": "not-json{", "score": 0.5},
        ])
        results = store.query(Query(embeddings=[[0.1, 0.2, 0.3]]))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].text, "ok")
        self.assertEqual(results[0].metadata["score"], 0.5)


class TestMongoDBAtlasStoreDeleteAndInspect(_MongoPatchMixin, unittest.TestCase):

    def test_delete_calls_delete_one(self):
        store = self._store()
        store.delete_document("doc-123")
        self.mock_collection.delete_one.assert_called_once_with(
            {"_id": "doc-123"})

    def test_count_returns_count_documents(self):
        store = self._store()
        self.mock_collection.count_documents.return_value = 42
        self.assertEqual(store.get_document_count(), 42)

    def test_count_on_error_returns_zero(self):
        store = self._store()
        self.mock_collection.count_documents.side_effect = RuntimeError(
            "connection lost")
        self.assertEqual(store.get_document_count(), 0)

    def test_get_document_by_id_found(self):
        store = self._store()
        self.mock_collection.find_one.return_value = {
            "_id": "d1", "text": "found", "metadata_json": '{"k":"v"}'}
        doc = store.get_document_by_id("d1")
        self.assertIsNotNone(doc)
        self.assertEqual(doc.text, "found")
        self.assertEqual(doc.metadata, {"k": "v"})

    def test_get_document_by_id_not_found_returns_none(self):
        store = self._store()
        self.mock_collection.find_one.return_value = None
        self.assertIsNone(store.get_document_by_id("missing"))

    def test_list_document_ids_returns_ids(self):
        store = self._store()
        self.mock_collection.find.return_value = iter([
            {"_id": "a"}, {"_id": "b"}, {"_id": "c"},
        ])
        ids = store.list_document_ids()
        self.assertEqual(ids, ["a", "b", "c"])


class TestMongoDBAtlasStoreConnection(unittest.TestCase):

    def test_resolve_connection_url_from_env(self):
        store = MongoDBAtlasStore(connection_url=None)
        with patch.dict("os.environ", {"MONGODB_ATLAS_URI": "mongodb://env"}):
            self.assertEqual(store._resolve_connection_url(), "mongodb://env")

    def test_resolve_connection_url_missing_raises(self):
        store = MongoDBAtlasStore(connection_url=None)
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError):
                store._resolve_connection_url()


if __name__ == "__main__":
    unittest.main(verbosity=2)
