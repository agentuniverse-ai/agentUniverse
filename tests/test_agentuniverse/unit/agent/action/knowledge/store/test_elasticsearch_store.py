#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for ElasticsearchStore. All mock the ES client; no server required."""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.elasticsearch_store \
    import ElasticsearchStore


def _mock_es_client():
    client = MagicMock()
    client.indices.exists.return_value = False
    client.indices.create.return_value = MagicMock()
    return client


class TestElasticsearchStoreConfig(unittest.TestCase):

    def test_valid_config(self):
        store = ElasticsearchStore(hosts="http://localhost:9200",
                                   index_name="test", dimensions=128)
        store._validate_config()

    def test_empty_hosts_rejected(self):
        with self.assertRaises(ValueError):
            ElasticsearchStore(hosts="")._validate_config()

    def test_invalid_similarity_rejected(self):
        with self.assertRaises(ValueError):
            ElasticsearchStore(hosts="http://x", similarity="jaccard")._validate_config()

    def test_zero_top_k_rejected(self):
        with self.assertRaises(ValueError):
            ElasticsearchStore(hosts="http://x", similarity_top_k=0)._validate_config()


class TestElasticsearchStoreCRUD(unittest.TestCase):

    def setUp(self):
        self.mock_client = _mock_es_client()
        self._patcher = patch.dict("sys.modules", {"elasticsearch": MagicMock(Elasticsearch=MagicMock(return_value=self.mock_client))})
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def _store(self):
        store = ElasticsearchStore(hosts="http://localhost:9200",
                                   index_name="test_idx", dimensions=3)
        store._new_client()
        return store

    def test_insert_single_doc(self):
        store = self._store()
        store.insert_document([Document(id="d1", text="hello", embedding=[0.1, 0.2, 0.3])])
        self.mock_client.index.assert_called_once()
        call = self.mock_client.index.call_args
        self.assertEqual(call.kwargs["id"], "d1")
        self.assertEqual(call.kwargs["document"]["text"], "hello")
        self.assertEqual(call.kwargs["document"]["embedding"], [0.1, 0.2, 0.3])

    def test_insert_dim_mismatch_raises(self):
        store = self._store()
        with self.assertRaises(ValueError):
            store.insert_document([
                Document(id="d1", text="a", embedding=[0.1, 0.2, 0.3]),
                Document(id="d2", text="b", embedding=[0.1, 0.2]),
            ])

    def test_query_returns_documents(self):
        store = self._store()
        self.mock_client.indices.exists.return_value = True
        self.mock_client.search.return_value = {
            "hits": {"hits": [
                {"_id": "d1", "_score": 0.95, "_source": {"text": "result"}},
                {"_id": "d2", "_score": 0.80, "_source": {"text": "second"}},
            ]}
        }
        results = store.query(Query(embeddings=[[0.1, 0.2, 0.3]], similarity_top_k=5))
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].text, "result")
        self.assertEqual(results[0].metadata["score"], 0.95)

    def test_query_no_embedding_returns_empty(self):
        store = self._store()
        results = store.query(Query(query_str="", embeddings=[]))
        self.assertEqual(results, [])

    def test_delete(self):
        store = self._store()
        store.delete_document("d1")
        self.mock_client.delete.assert_called_once_with(index="test_idx", id="d1")

    def test_count(self):
        store = self._store()
        self.mock_client.count.return_value = {"count": 42}
        self.assertEqual(store.get_document_count(), 42)

    def test_get_by_id(self):
        store = self._store()
        self.mock_client.get.return_value = {
            "found": True,
            "_source": {"text": "found", "embedding": [0.1]},
        }
        doc = store.get_document_by_id("d1")
        self.assertIsNotNone(doc)
        self.assertEqual(doc.text, "found")

    def test_get_by_id_not_found(self):
        store = self._store()
        self.mock_client.get.return_value = {"found": False}
        self.assertIsNone(store.get_document_by_id("missing"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
