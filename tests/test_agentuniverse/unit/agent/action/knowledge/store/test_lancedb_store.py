#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for LanceDBStore.

Uses a real embedded LanceDB (no server needed) in a temp directory, so
the tests exercise the actual insert/query/delete paths end-to-end.
"""

import os
import shutil
import tempfile
import unittest

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.lancedb_store import LanceDBStore
from agentuniverse.agent.action.knowledge.store.query import Query


class TestLanceDBStoreConfig(unittest.TestCase):

    def test_valid_config_accepted(self):
        store = LanceDBStore(db_path="/tmp/test", table_name="T", dimensions=3)
        store._validate_config()

    def test_empty_db_path_rejected(self):
        with self.assertRaises(ValueError):
            LanceDBStore(db_path="", table_name="T")._validate_config()

    def test_empty_table_name_rejected(self):
        with self.assertRaises(ValueError):
            LanceDBStore(db_path="/tmp/x", table_name="")._validate_config()

    def test_invalid_distance_rejected(self):
        with self.assertRaises(ValueError):
            LanceDBStore(db_path="/tmp/x", table_name="T",
                         distance="manhattan")._validate_config()

    def test_zero_top_k_rejected(self):
        with self.assertRaises(ValueError):
            LanceDBStore(db_path="/tmp/x", table_name="T",
                         similarity_top_k=0)._validate_config()

    def test_negative_dimensions_rejected(self):
        with self.assertRaises(ValueError):
            LanceDBStore(db_path="/tmp/x", table_name="T",
                         dimensions=-1)._validate_config()


class TestLanceDBStoreCRUD(unittest.TestCase):
    """End-to-end CRUD with a real embedded LanceDB in a temp directory."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.store = LanceDBStore(
            db_path=self.tmp, table_name="test_table", dimensions=3)
        # Don't pre-create the table; let first insert infer the schema.
        self.store._new_client()

    def tearDown(self):
        self.store.client = None
        self.store._table = None
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_insert_and_query(self):
        self.store.insert_document([
            Document(id="d1", text="hello world", embedding=[1.0, 0.0, 0.0]),
            Document(id="d2", text="goodbye world", embedding=[0.0, 1.0, 0.0]),
        ])
        self.assertEqual(self.store.get_document_count(), 2)

        results = self.store.query(
            Query(embeddings=[[1.0, 0.0, 0.0]], similarity_top_k=2))
        self.assertEqual(len(results), 2)
        # Nearest to [1,0,0] should be d1.
        self.assertEqual(results[0].text, "hello world")
        self.assertIn("score", results[0].metadata)

    def test_insert_dimension_mismatch_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.store.insert_document([
                Document(id="d1", text="a", embedding=[0.1, 0.2, 0.3]),
                Document(id="d2", text="b", embedding=[0.1, 0.2]),
            ])
        self.assertIn("dim", str(ctx.exception).lower())

    def test_insert_empty_list_noop(self):
        self.store.insert_document([])
        self.assertEqual(self.store.get_document_count(), 0)

    def test_delete(self):
        self.store.insert_document([
            Document(id="d1", text="hello", embedding=[1.0, 0.0, 0.0]),
        ])
        self.assertEqual(self.store.get_document_count(), 1)
        self.store.delete_document("d1")
        self.assertEqual(self.store.get_document_count(), 0)

    def test_upsert_replaces_existing(self):
        self.store.insert_document([
            Document(id="d1", text="original", embedding=[1.0, 0.0, 0.0]),
        ])
        self.store.upsert_document([
            Document(id="d1", text="updated", embedding=[0.0, 1.0, 0.0]),
        ])
        self.assertEqual(self.store.get_document_count(), 1)
        doc = self.store.get_document_by_id("d1")
        self.assertIsNotNone(doc)
        self.assertEqual(doc.text, "updated")

    def test_get_document_by_id_not_found(self):
        doc = self.store.get_document_by_id("nonexistent")
        self.assertIsNone(doc)

    def test_list_document_ids(self):
        self.store.insert_document([
            Document(id="d1", text="a", embedding=[1.0, 0.0, 0.0]),
            Document(id="d2", text="b", embedding=[0.0, 1.0, 0.0]),
        ])
        ids = set(self.store.list_document_ids())
        self.assertEqual(ids, {"d1", "d2"})

    def test_metadata_round_trip(self):
        self.store.insert_document([
            Document(id="d1", text="hello",
                     embedding=[1.0, 0.0, 0.0],
                     metadata={"category": "news", "source": "web"}),
        ])
        results = self.store.query(
            Query(embeddings=[[1.0, 0.0, 0.0]], similarity_top_k=1))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].metadata["category"], "news")
        self.assertEqual(results[0].metadata["source"], "web")

    def test_query_no_embedding_returns_empty(self):
        results = self.store.query(Query(query_str="", embeddings=[]))
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
