#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/15
# @Author  : dxz0069
# @FileName: test_lancedb_store.py

import shutil
import tempfile
import unittest

try:
    import lancedb  # noqa: F401

    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


@unittest.skipUnless(LANCEDB_AVAILABLE, "lancedb not available")
class TestLanceDBStore(unittest.TestCase):
    """Test cases for the LanceDB store, run against a real embedded database."""

    def setUp(self):
        from agentuniverse.agent.action.knowledge.store.lancedb_store import LanceDBStore
        self.LanceDBStore = LanceDBStore
        self.temp_dir = tempfile.mkdtemp()
        self.store = LanceDBStore(uri=self.temp_dir, table_name="test_table")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_distance_type_mapping(self):
        self.assertEqual(self.store._distance_type(), "cosine")
        self.assertEqual(self.LanceDBStore(distance="EUCLID")._distance_type(), "l2")
        self.assertEqual(self.LanceDBStore(distance="DOT")._distance_type(), "dot")
        self.assertEqual(self.LanceDBStore(distance="unknown")._distance_type(), "cosine")

    def test_quote_formats_sql_literals(self):
        from agentuniverse.agent.action.knowledge.store.lancedb_store import _quote
        self.assertEqual(_quote('simple'), "'simple'")
        self.assertEqual(_quote("has 'single'"), "'has ''single'''")
        self.assertEqual(_quote('has "double"'), '\'has "double"\'')

    def test_insert_and_query_roundtrip(self):
        documents = [
            Document(id="doc1", text="hello world", embedding=[1.0, 0.0], metadata={"k": "v"}),
            Document(id="doc2", text="goodbye world", embedding=[0.0, 1.0]),
        ]
        self.store.insert_document(documents)

        results = self.store.query(Query(query_str="hi", embeddings=[[1.0, 0.0]], similarity_top_k=1))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "doc1")
        self.assertEqual(results[0].text, "hello world")
        self.assertEqual(results[0].metadata, {"k": "v"})

        both = self.store.query(Query(query_str="hi", embeddings=[[0.7, 0.7]], similarity_top_k=2))
        self.assertEqual(len(both), 2)

    def test_query_with_vectors(self):
        self.store.insert_document([Document(id="doc1", text="hello", embedding=[1.0, 0.0])])
        results = self.store.query(Query(query_str="hi", embeddings=[[1.0, 0.0]], similarity_top_k=1))
        self.assertEqual(results[0].embedding, [])

        store_with_vectors = self.LanceDBStore(uri=self.temp_dir + "_vectors", table_name="t", with_vectors=True)
        store_with_vectors.insert_document([Document(id="doc1", text="hello", embedding=[1.0, 0.0])])
        results = store_with_vectors.query(Query(query_str="hi", embeddings=[[1.0, 0.0]], similarity_top_k=1))
        self.assertEqual(len(results[0].embedding), 2)

    def test_insert_skips_empty_embeddings(self):
        self.store.insert_document([Document(id="doc1", text="no embedding")])
        # no table created, queries stay empty
        self.assertEqual(self.store.query(Query(query_str="hi", embeddings=[[1.0, 0.0]])), [])

    def test_upsert_replaces_existing_rows(self):
        self.store.insert_document([Document(id="doc1", text="first", embedding=[1.0, 0.0])])
        self.store.upsert_document([Document(id="doc1", text="second", embedding=[1.0, 0.1])])

        results = self.store.query(Query(query_str="hi", embeddings=[[1.0, 0.0]], similarity_top_k=10))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].text, "second")

    def test_delete_document(self):
        self.store.insert_document([
            Document(id="doc1", text="hello", embedding=[1.0, 0.0]),
            Document(id="doc2", text="world", embedding=[0.0, 1.0]),
        ])
        self.store.delete_document("doc1")
        results = self.store.query(Query(query_str="hi", embeddings=[[1.0, 0.0]], similarity_top_k=10))
        self.assertEqual([document.id for document in results], ["doc2"])

    def test_delete_document_with_quotes_in_id(self):
        self.store.insert_document([Document(id='we"ird', text="hello", embedding=[1.0, 0.0])])
        self.store.delete_document('we"ird')
        results = self.store.query(Query(query_str="hi", embeddings=[[1.0, 0.0]], similarity_top_k=10))
        self.assertEqual(results, [])

    def test_query_without_client(self):
        store = self.LanceDBStore()
        self.assertEqual(store.query(Query(query_str="hi")), [])

    def test_to_documents(self):
        rows = [{"id": "a", "text": "t", "vector": [0.1], "metadata": {"m": 1}, "_distance": 0.5}]
        documents = self.LanceDBStore.to_documents(rows, with_vectors=True)
        self.assertEqual(documents[0].id, "a")
        self.assertEqual(documents[0].embedding, [0.1])
        self.assertEqual(documents[0].metadata, {"m": 1})


if __name__ == "__main__":
    unittest.main()
