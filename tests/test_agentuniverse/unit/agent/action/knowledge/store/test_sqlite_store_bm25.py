#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for SQLiteStore BM25 correctness.

Covers three bugs that each silently distorted recall:

1. ``insert_document`` did not clear stale inverted-index rows for a re-inserted
   id, so re-running ingest accumulated old keywords alongside new ones,
   polluting BM25 term-frequency / IDF and recalling stale keywords.
2. ``query`` always used the store default ``similarity_top_k``, ignoring a
   caller-supplied ``Query.similarity_top_k``.
3. ``query`` dereferenced ``fetchone()[0]`` and ``json.loads(doc_row[3])``
   without guarding None, so a stale inverted-index entry or a NULL metadata
   column crashed the whole query.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore


def _identity_keyword_extractor(document):
    """A keyword extractor that uses whitespace tokens as keywords.

    Used in place of a real DocProcessor so tests can exercise the
    insert/query path without registering a keyword-extraction component.
    """
    document.keywords = list(set((document.text or "").split()))
    return document


class _SQLiteStoreTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.store = SQLiteStore(db_path=self.tmp.name, keyword_extractor="test")
        self.store._new_client()
        # Patch DocProcessorManager so _get_document_keyword uses our
        # identity extractor instead of requiring a registered component.
        fake_mgr = type("M", (), {"get_instance_obj":
                                  staticmethod(lambda name: type(
                                      "P", (), {"process_docs":
                                                staticmethod(
                                                    lambda docs: [
                                                        _identity_keyword_extractor(d)
                                                        for d in docs])})())})
        self._patcher = patch(
            "agentuniverse.agent.action.knowledge.store.sqlite_store."
            "DocProcessorManager", return_value=fake_mgr())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        self.store.conn.close()
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def _insert(self, doc_id: str, text: str, metadata=None):
        self.store.insert_document([
            Document(id=doc_id, text=text, metadata=metadata or {}),
        ])


class TestInsertClearsStaleInvertedIndex(_SQLiteStoreTestBase):
    """insert_document must clear stale keywords for a re-inserted id."""

    def test_re_insert_replaces_keywords_not_accumulates(self) -> None:
        # First insert: doc has keywords "alpha" and "beta".
        self._insert("d1", "alpha beta", metadata={"v": 1})
        cursor = self.store.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM inverted_index WHERE doc_id = ?", ("d1",))
        before = cursor.fetchone()[0]
        cursor.close()
        self.assertEqual(before, 2)

        # Re-insert the SAME id with different text/keywords.
        self._insert("d1", "gamma delta", metadata={"v": 2})

        cursor = self.store.conn.cursor()
        # Stale rows for "alpha" and "beta" must be gone; only "gamma" and
        # "delta" remain.
        cursor.execute(
            "SELECT term FROM inverted_index WHERE doc_id = ? ORDER BY term",
            ("d1",))
        terms = [row[0] for row in cursor.fetchall()]
        cursor.close()
        self.assertEqual(terms, ["delta", "gamma"])

    def test_re_insert_does_not_pollute_bm25_term_frequency(self) -> None:
        # Insert d1 with "alpha", then re-insert d1 with "beta". A query for
        # "alpha" must NOT recall d1 anymore.
        self._insert("d1", "alpha")
        self._insert("d1", "beta")  # re-insert replaces the document

        # d2 still has "alpha" as a real keyword.
        self._insert("d2", "alpha gamma")

        results = self.store.query(Query(query_str="alpha",
                                         keywords=["alpha"],
                                         similarity_top_k=10))
        ids = [r.id for r in results]
        self.assertIn("d2", ids)
        self.assertNotIn(
            "d1", ids,
            "stale 'alpha' keyword from the first insert of d1 must not "
            "recall d1 after it was re-inserted with different text")


class TestQueryHonoursPerQueryTopK(_SQLiteStoreTestBase):
    """query must honour Query.similarity_top_k, not just the store default."""

    def test_query_returns_more_than_default_when_top_k_requested(self) -> None:
        # Insert 5 docs that all share a keyword so they are all candidates.
        for i in range(5):
            self._insert(f"d{i}", f"shared term {i}")

        # Store default is 10; ask for only 2.
        results = self.store.query(Query(query_str="shared",
                                         keywords=["shared"],
                                         similarity_top_k=2))
        self.assertEqual(len(results), 2)

    def test_query_respects_store_default_when_top_k_not_set(self) -> None:
        for i in range(15):
            self._insert(f"d{i}", f"shared term {i}")
        # Query without similarity_top_k; store default is 10.
        original_default = self.store.similarity_top_k
        self.store.similarity_top_k = 3
        try:
            results = self.store.query(Query(query_str="shared",
                                             keywords=["shared"]))
            self.assertEqual(len(results), 3)
        finally:
            self.store.similarity_top_k = original_default


class TestQueryGuardsAgainstMissingRows(_SQLiteStoreTestBase):
    """query must not crash on a stale inverted-index entry or NULL metadata."""

    def test_stale_inverted_index_entry_is_skipped_not_crash(self) -> None:
        # Manually plant an inverted_index row pointing at a doc that does not
        # exist in the documents table.
        with self.store.conn:
            self.store.conn.execute(
                "INSERT INTO inverted_index (term, doc_id) VALUES (?, ?)",
                ("ghost", "missing_doc"),
            )
        # Also insert a real doc that matches "ghost" so we can tell the query
        # completed and returned the real one.
        self._insert("real", "ghost story")

        # Previously: cursor.fetchone()[0] on the missing_doc row raised
        # TypeError: 'NoneType' object is not subscriptable.
        results = self.store.query(Query(query_str="ghost",
                                         keywords=["ghost"],
                                         similarity_top_k=10))
        ids = [r.id for r in results]
        self.assertIn("real", ids)
        self.assertNotIn("missing_doc", ids)

    def test_null_metadata_does_not_crash_query(self) -> None:
        # Insert a doc whose metadata ends up NULL in the DB (metadata=None).
        self.store.insert_document([Document(id="d1", text="alpha beta",
                                             metadata=None)])
        # Previously: json.loads(None) raised TypeError.
        results = self.store.query(Query(query_str="alpha",
                                         keywords=["alpha"],
                                         similarity_top_k=10))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "d1")
        # metadata must round-trip as None, not crash.
        self.assertIsNone(results[0].metadata)


class TestToDocumentsHandlesShapesSafely(unittest.TestCase):
    """to_documents must not crash on the shapes it can actually receive."""

    def test_none_returns_empty(self) -> None:
        self.assertEqual(SQLiteStore.to_documents(None), [])

    def test_unrecognised_shape_returns_empty(self) -> None:
        # Previously this would have raised KeyError or TypeError.
        self.assertEqual(SQLiteStore.to_documents("not a dict or list"), [])
        self.assertEqual(SQLiteStore.to_documents({"no_ids_key": []}), [])

    def test_sqlite_row_tuples_round_trip(self) -> None:
        rows = [
            ("d1", "text one", 2, json.dumps({"k": "v"})),
            ("d2", "text two", 2, None),  # NULL metadata
        ]
        docs = SQLiteStore.to_documents(rows)
        self.assertEqual([d.id for d in docs], ["d1", "d2"])
        self.assertEqual(docs[0].metadata, {"k": "v"})
        self.assertIsNone(docs[1].metadata)

    def test_chroma_style_dict_round_trip(self) -> None:
        # Cross-store compatibility: a Chroma-style nested-list-of-lists dict.
        result = {
            "ids": [["c1", "c2"]],
            "documents": [["a text", "b text"]],
            "metadatas": [[{"x": 1}, {"x": 2}]],
        }
        docs = SQLiteStore.to_documents(result)
        self.assertEqual([d.id for d in docs], ["c1", "c2"])
        self.assertEqual(docs[0].metadata, {"x": 1})

    def test_corrupt_metadata_json_does_not_crash(self) -> None:
        rows = [("d1", "text", 1, "not-valid-json{")]
        docs = SQLiteStore.to_documents(rows)
        self.assertEqual(len(docs), 1)
        self.assertIsNone(docs[0].metadata)


if __name__ == "__main__":
    unittest.main(verbosity=2)
