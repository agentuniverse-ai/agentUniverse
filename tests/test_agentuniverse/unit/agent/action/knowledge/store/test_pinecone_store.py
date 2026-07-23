#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for PineconeStore.

All tests mock the pinecone client so no server or network access is
required. Covers config validation, dimension checking, insert / upsert /
query round-trip, delete, count, fetch-by-id, list-ids, and error paths.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.pinecone_store import \
    PineconeStore
from agentuniverse.agent.action.knowledge.store.query import Query


def _mock_pinecone():
    """Build a mock pinecone module + client for patching sys.modules."""
    mock_mod = MagicMock()
    mock_mod.__version__ = "3.0.0"
    mock_mod.ServerlessSpec = MagicMock(return_value=MagicMock())

    # Pinecone(...) client
    client = MagicMock()
    index = MagicMock()

    # list_indexes().names() -> [] (empty so _ensure_index would create)
    client.list_indexes.return_value = MagicMock(names=lambda: [])
    client.create_index.return_value = None
    client.Index.return_value = index

    mock_mod.Pinecone = MagicMock(return_value=client)

    return mock_mod, client, index


class TestPineconeStoreConfig(unittest.TestCase):

    def test_valid_config_is_accepted(self):
        store = PineconeStore(
            index_name="agentuniverse-documents",
            dimensions=128,
            distance="cosine",
        )
        store._validate_config()  # must not raise

    def test_invalid_distance_rejected(self):
        store = PineconeStore(index_name="idx", distance="manhattan")
        with self.assertRaises(ValueError):
            store._validate_config()

    def test_zero_top_k_rejected(self):
        store = PineconeStore(index_name="idx", similarity_top_k=0)
        with self.assertRaises(ValueError):
            store._validate_config()

    def test_negative_dimensions_rejected(self):
        store = PineconeStore(index_name="idx", dimensions=-1)
        with self.assertRaises(ValueError):
            store._validate_config()

    def test_all_supported_distances_accepted(self):
        for d in ("cosine", "euclidean", "dotproduct"):
            store = PineconeStore(index_name="idx", distance=d)
            store._validate_config()

    def test_namespace_must_be_string(self):
        # Pydantic enforces the str type at construction; the configer path
        # can still bypass it, so _validate_config guards explicitly. Use
        # object.__setattr__ to simulate a non-str injected post-construction.
        store = PineconeStore(index_name="idx", namespace="")
        object.__setattr__(store, "namespace", 123)
        with self.assertRaises(TypeError):
            store._validate_config()


class _PineconePatchMixin:
    """Shared setUp/tearDown that installs the mocked pinecone module."""

    def setUp(self):
        self.mock_mod, self.mock_client, self.mock_index = _mock_pinecone()
        self._patcher = patch.dict("sys.modules", {"pinecone": self.mock_mod})
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def _store(self, **overrides):
        params = dict(
            api_key="fake-key",
            index_name="test-index",
            dimensions=3,
            embedding_model=None,
        )
        params.update(overrides)
        store = PineconeStore(**params)
        store._new_client()
        return store


class TestPineconeStoreInsert(_PineconePatchMixin, unittest.TestCase):

    def test_insert_single_document_upserts(self):
        store = self._store()
        doc = Document(id="d1", text="hello", embedding=[0.1, 0.2, 0.3])
        store.insert_document([doc])
        self.mock_index.upsert.assert_called_once()
        _, kwargs = self.mock_index.upsert.call_args
        vectors = kwargs.get("vectors") or self.mock_index.upsert.call_args[0][0]
        self.assertEqual(vectors[0][0], "d1")
        self.assertEqual(vectors[0][1], [0.1, 0.2, 0.3])
        self.assertEqual(vectors[0][2]["text"], "hello")

    def test_upsert_dimension_mismatch_raises(self):
        store = self._store()
        docs = [
            Document(id="d1", text="a", embedding=[0.1, 0.2, 0.3]),
            Document(id="d2", text="b", embedding=[0.1, 0.2]),  # dim 2 vs 3
        ]
        with self.assertRaises(ValueError) as ctx:
            store.upsert_document(docs)
        self.assertIn("dimension", str(ctx.exception).lower())

    def test_insert_empty_list_is_noop(self):
        store = self._store()
        store.insert_document([])
        self.mock_index.upsert.assert_not_called()

    def test_update_document_delegates_to_upsert(self):
        store = self._store()
        doc = Document(id="d1", text="updated", embedding=[0.1, 0.2, 0.3])
        store.update_document([doc])
        self.mock_index.upsert.assert_called_once()


class TestPineconeStoreQuery(_PineconePatchMixin, unittest.TestCase):

    def test_query_returns_documents_with_score(self):
        store = self._store()
        self.mock_index.query.return_value = {
            "matches": [
                {"id": "m1", "score": 0.95,
                 "metadata": {"text": "result",
                              "metadata_json": json.dumps({"k": "v"})}},
                {"id": "m2", "score": 0.80,
                 "metadata": {"text": "second", "metadata_json": "{}"}},
            ]
        }
        results = store.query(
            Query(embeddings=[[0.1, 0.2, 0.3]], similarity_top_k=5))
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].text, "result")
        self.assertEqual(results[0].metadata["k"], "v")
        self.assertEqual(results[0].metadata["score"], 0.95)

    def test_query_with_metadata_filter_passes_filter(self):
        store = self._store()
        self.mock_index.query.return_value = {"matches": []}
        store.query(Query(embeddings=[[0.1, 0.2, 0.3]]),
                    metadata_filter={"tenant": "acme"})
        _, kwargs = self.mock_index.query.call_args
        self.assertEqual(kwargs["filter"], {"tenant": "acme"})

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
        self.mock_index.query.return_value = {
            "matches": [
                {"id": "m1", "score": 0.5,
                 "metadata": {"text": "ok", "metadata_json": "not-json{"}},
            ]
        }
        results = store.query(Query(embeddings=[[0.1, 0.2, 0.3]]))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].text, "ok")
        # corrupt metadata becomes empty dict, score still attached
        self.assertEqual(results[0].metadata["score"], 0.5)


class TestPineconeStoreDeleteAndInspect(_PineconePatchMixin, unittest.TestCase):

    def test_delete_calls_index_delete(self):
        store = self._store()
        store.delete_document("doc-123")
        self.mock_index.delete.assert_called_once()
        _, kwargs = self.mock_index.delete.call_args
        self.assertEqual(kwargs["ids"], ["doc-123"])

    def test_count_returns_namespace_vector_count(self):
        store = self._store(namespace="ns1")
        self.mock_index.describe_index_stats.return_value = {
            "namespaces": {
                "ns1": {"vector_count": 42},
                "ns2": {"vector_count": 7},
            }
        }
        self.assertEqual(store.get_document_count(), 42)

    def test_count_without_namespace_sums_all(self):
        store = self._store(namespace="")
        self.mock_index.describe_index_stats.return_value = {
            "namespaces": {
                "ns1": {"vector_count": 42},
                "ns2": {"vector_count": 7},
            }
        }
        self.assertEqual(store.get_document_count(), 49)

    def test_count_on_error_returns_zero(self):
        store = self._store()
        self.mock_index.describe_index_stats.side_effect = RuntimeError(
            "connection lost")
        self.assertEqual(store.get_document_count(), 0)

    def test_get_document_by_id_found(self):
        store = self._store()
        self.mock_index.fetch.return_value = {
            "vectors": {
                "d1": {"metadata": {"text": "found",
                                    "metadata_json": '{"k":"v"}'}},
            }
        }
        doc = store.get_document_by_id("d1")
        self.assertIsNotNone(doc)
        self.assertEqual(doc.text, "found")
        self.assertEqual(doc.metadata, {"k": "v"})

    def test_get_document_by_id_not_found_returns_none(self):
        store = self._store()
        self.mock_index.fetch.return_value = {"vectors": {}}
        self.assertIsNone(store.get_document_by_id("missing"))

    def test_list_document_ids_returns_matched_ids(self):
        store = self._store(dimensions=3)
        self.mock_index.query.return_value = {
            "matches": [
                {"id": "a"}, {"id": "b"}, {"id": "c"},
            ]
        }
        ids = store.list_document_ids()
        self.assertEqual(ids, ["a", "b", "c"])

    def test_list_document_ids_without_dimensions_returns_empty(self):
        store = self._store()
        store.dimensions = None
        self.assertEqual(store.list_document_ids(), [])


class TestPineconeStoreApiAndSpec(unittest.TestCase):

    def test_resolve_api_key_from_env(self):
        store = PineconeStore(api_key=None)
        with patch.dict("os.environ", {"PINECONE_API_KEY": "env-key"}):
            self.assertEqual(store._resolve_api_key(), "env-key")

    def test_resolve_api_key_missing_raises(self):
        store = PineconeStore(api_key=None)
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError):
                store._resolve_api_key()

    def test_serverless_spec_parses_environment(self):
        store = PineconeStore(environment="aws-us-east-1")
        self.assertEqual(store._serverless_spec(), ("aws", "us-east-1"))

    def test_serverless_spec_defaults_when_unset(self):
        store = PineconeStore(environment=None)
        self.assertEqual(store._serverless_spec(), ("aws", "us-east-1"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
