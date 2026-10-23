#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/15
# @Author  : dxz0069
# @FileName: test_lancedb_store.py

import shutil
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock

try:
    import lancedb  # noqa: F401

    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False
    # Inject a minimal fake of the client library so the component's lazy
    # import resolves and the behavioral tests below still run everywhere;
    # the fake is only the module entry point, all connection behavior is
    # mocked by the tests themselves.
    _fake_lancedb = types.ModuleType("lancedb")
    _fake_lancedb.connect = MagicMock()
    sys.modules.setdefault("lancedb", _fake_lancedb)

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


def _doc(text, doc_id="1", metadata=None, embedding=None):
    return Document(id=doc_id, text=text, metadata=metadata, embedding=embedding)


class TestLanceDBStoreUnit(unittest.TestCase):
    """Behavioral tests for the LanceDB store, run against mocked clients.

    These do not require the lancedb package; installing it additionally
    enables the real embedded-database tests in TestLanceDBStoreIntegration.
    """

    def setUp(self):
        from agentuniverse.agent.action.knowledge.store.lancedb_store import LanceDBStore
        self.LanceDBStore = LanceDBStore
        self.store = LanceDBStore(uri="./lancedb_test", table_name="test_table")
        self.db = MagicMock()
        self.store.client = self.db

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

    def test_to_documents(self):
        rows = [{"id": "a", "text": "t", "vector": [0.1], "metadata": {"m": 1}, "_distance": 0.5}]
        documents = self.LanceDBStore.to_documents(rows, with_vectors=True)
        self.assertEqual(documents[0].id, "a")
        self.assertEqual(documents[0].embedding, [0.1])
        self.assertEqual(documents[0].metadata, {"m": 1})

    def test_insert_creates_table_on_first_write(self):
        self.db.table_names.return_value = []
        documents = [_doc("hello", "doc1", {"k": "v"}, [0.1, 0.2])]
        self.store.insert_document(documents)
        self.db.create_table.assert_called_once()
        call = self.db.create_table.call_args
        self.assertEqual(call.args[0], "test_table")
        rows = call.kwargs["data"]
        self.assertEqual(rows[0]["id"], "doc1")
        self.assertEqual(rows[0]["vector"], [0.1, 0.2])
        self.assertEqual(rows[0]["metadata"], {"k": "v"})
        # rows are written by create_table itself, no add afterwards
        table = self.db.open_table.return_value
        table.add.assert_not_called()

    def test_insert_appends_when_table_exists(self):
        self.db.table_names.return_value = ["test_table"]
        documents = [_doc("hello", "doc1", None, [0.1, 0.2])]
        self.store.insert_document(documents)
        table = self.db.open_table.return_value
        table.add.assert_called_once()
        self.assertEqual(table.add.call_args.args[0][0]["id"], "doc1")

    def test_upsert_deletes_then_adds(self):
        self.db.table_names.return_value = ["test_table"]
        documents = [_doc("hello", "doc1", None, [0.1, 0.2])]
        self.store.upsert_document(documents)
        table = self.db.open_table.return_value
        table.delete.assert_called_once_with("id IN ('doc1')")
        table.add.assert_called_once()

    def test_delete_document(self):
        self.db.table_names.return_value = ["test_table"]
        self.store.delete_document("doc1")
        table = self.db.open_table.return_value
        table.delete.assert_called_once_with("id = 'doc1'")

    def test_delete_document_missing_table(self):
        self.db.table_names.return_value = []
        self.store.delete_document("doc1")
        self.db.open_table.assert_not_called()

    def test_query_builds_search_chain(self):
        self.db.table_names.return_value = ["test_table"]
        table = self.db.open_table.return_value
        search_builder = table.search.return_value
        search_builder.distance_type.return_value.limit.return_value.to_list.return_value = [
            {"id": "doc1", "text": "hello", "vector": [0.1, 0.2], "metadata": {"k": "v"}}
        ]
        results = self.store.query(Query(query_str="hi", embeddings=[[0.1, 0.2]], similarity_top_k=5))
        table.search.assert_called_once_with([0.1, 0.2])
        search_builder.distance_type.assert_called_once_with("cosine")
        search_builder.distance_type.return_value.limit.assert_called_once_with(5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].text, "hello")

    def test_query_without_client(self):
        store = self.LanceDBStore()
        self.assertEqual(store.query(Query(query_str="hi")), [])

    def test_new_client_connection_args(self):
        import lancedb
        store = self.LanceDBStore(uri="./lancedb_test", api_key="secret", region="cn-north-1")
        with unittest.mock.patch.object(lancedb, "connect") as connect:
            client = store._new_client()
        self.assertIs(client, connect.return_value)
        kwargs = connect.call_args.kwargs
        self.assertEqual(kwargs["api_key"], "secret")
        self.assertEqual(kwargs["region"], "cn-north-1")


@unittest.skipUnless(LANCEDB_AVAILABLE, "lancedb not available")
class TestLanceDBStoreIntegration(unittest.TestCase):
    """Test cases for the LanceDB store, run against a real embedded database.

    LanceDB is embedded: with the package installed these roundtrips run
    for real, no server is needed.
    """

    def setUp(self):
        from agentuniverse.agent.action.knowledge.store.lancedb_store import LanceDBStore
        self.LanceDBStore = LanceDBStore
        self.temp_dir = tempfile.mkdtemp()
        self.store = LanceDBStore(uri=self.temp_dir, table_name="test_table")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

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


if __name__ == "__main__":
    unittest.main()
