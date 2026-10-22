# !/usr/bin/env python3

# @Time    : 2026/10/03
# @FileName: test_store_create_copy.py

"""Tests for Store.create_copy isolation (issue #1183).

``create_copy`` used to return ``self``, so every
``get_instance_obj(..., new_instance=True)`` caller shared one mutable
Store. The fix copies mutable state deeply for instance isolation, with live
clients kept as shared references.
"""

import os
import tempfile
import threading
import unittest

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
from agentuniverse.agent.action.knowledge.store.store import Store


class _DummyStore(Store):
    """Minimal concrete store with extra per-runtime fields."""

    embedding_model: str = ""
    options: dict = {}
    documents: list[Document] = []

    def query(self, query: Query, **kwargs):
        return []


class TestStoreCreateCopyIsolation(unittest.TestCase):
    """A copy is a distinct instance whose field writes stay local."""

    def test_copy_is_not_self(self) -> None:
        store = _DummyStore(name="s")
        self.assertIsNot(store.create_copy(), store)

    def test_successive_copies_are_distinct(self) -> None:
        # The exact isolation guarantee missing in issue #1183:
        # two create_copy calls must not hand out the same object.
        store = _DummyStore(name="s")
        a = store.create_copy()
        b = store.create_copy()
        self.assertIsNot(a, b)
        self.assertIsNot(a, store)

    def test_field_write_on_copy_does_not_leak(self) -> None:
        store = _DummyStore(name="original", description="d")
        copied = store.create_copy()
        copied.name = "changed"
        copied.description = "changed too"
        self.assertEqual(store.name, "original")
        self.assertEqual(store.description, "d")
        self.assertEqual(copied.name, "changed")

    def test_subclass_fields_are_carried_and_isolated(self) -> None:
        store = _DummyStore(name="s", embedding_model="m1")
        copied = store.create_copy()
        self.assertEqual(copied.embedding_model, "m1")
        copied.embedding_model = "m2"
        self.assertEqual(store.embedding_model, "m1")

    def test_base_component_fields_are_carried(self) -> None:
        store = _DummyStore(name="s")
        store.component_config_path = "/tmp/s.yaml"
        store.default_symbol = True
        copied = store.create_copy()
        self.assertEqual(copied.component_config_path, "/tmp/s.yaml")
        self.assertTrue(copied.default_symbol)


class TestStoreCreateCopySharedClients(unittest.TestCase):
    """Live post-fork clients stay shared references (LLM precedent)."""

    def test_client_shared_by_reference(self) -> None:
        sentinel = object()
        store = _DummyStore(name="s")
        store.client = sentinel
        copied = store.create_copy()
        self.assertIs(copied.client, sentinel)

    def test_async_client_shared_by_reference(self) -> None:
        sentinel = object()
        store = _DummyStore(name="s")
        store.async_client = sentinel
        copied = store.create_copy()
        self.assertIs(copied.async_client, sentinel)

    def test_client_rebinding_on_copy_does_not_leak(self) -> None:
        original_client = object()
        store = _DummyStore(name="s")
        store.client = original_client
        copied = store.create_copy()
        copied.client = object()
        self.assertIs(store.client, original_client)

    def test_plain_store_class_also_isolated(self) -> None:
        # The fix lives on the base class, so every store benefits.
        store = Store(name="base")
        copied = store.create_copy()
        self.assertIsNot(copied, store)
        self.assertEqual(copied.name, "base")


class TestStoreCreateCopyNestedIsolation(unittest.TestCase):
    """Mutable state is isolated while live connections remain shared."""

    def test_nested_options_are_isolated(self) -> None:
        store = _DummyStore(name="s", options={"nested": {"values": [1]}})
        copied = store.create_copy()
        copied.options["nested"]["values"].append(2)
        self.assertEqual(store.options, {"nested": {"values": [1]}})

    def test_document_embeddings_keywords_and_metadata_are_isolated(self) -> None:
        store = _DummyStore(
            name="s", documents=[Document(text="doc", embedding=[0.1], keywords={"old"}, metadata={"tags": ["old"]})]
        )
        copied = store.create_copy()
        sibling = store.create_copy()
        copied.documents[0].embedding.append(0.2)
        copied.documents[0].keywords.add("copy")
        copied.documents[0].metadata["tags"].append("copy")
        store.documents[0].embedding[0] = 0.9
        store.documents[0].keywords.add("original")
        self.assertEqual(copied.documents[0].embedding, [0.1, 0.2])
        self.assertEqual(copied.documents[0].keywords, {"old", "copy"})
        self.assertEqual(store.documents[0].embedding, [0.9])
        self.assertEqual(store.documents[0].metadata, {"tags": ["old"]})
        self.assertEqual(sibling.documents[0].embedding, [0.1])
        self.assertEqual(sibling.documents[0].keywords, {"old"})

    def test_uncopyable_client_and_nested_alias_are_preserved(self) -> None:
        lock = threading.Lock()
        store = _DummyStore(name="s", client=lock, async_client=lock, options={"connection": lock})
        copied = store.create_copy()
        self.assertIs(copied.client, lock)
        self.assertIs(copied.async_client, lock)
        self.assertIs(copied.options["connection"], lock)
        self.assertIsNot(copied.options, store.options)


class TestStoreCreateCopyBuiltinSQLiteStore(unittest.TestCase):
    """Review regression (issue #1183, P1): the built-in SQLiteStore keeps
    its live ``sqlite3.Connection`` in ``conn`` — not ``client`` — and does
    not override ``create_copy``. A whole-object deepcopy with a
    client-only memo raised ``TypeError: cannot pickle 'sqlite3.Connection'
    object`` on an initialized store. The per-field sharing fallback must
    keep initialized built-in stores working with ``new_instance=True``.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.db_path = os.path.join(self._tmp.name, "real_store.db")
        self.store = SQLiteStore(name="sqlite_copy_probe", db_path=self.db_path)
        # Really initialize: live connection + tables, exactly the state a
        # registered store has after the post-fork hook ran.
        self.store._new_client()
        self.addCleanup(self.store.conn.close)

    def test_create_copy_succeeds_on_initialized_store(self) -> None:
        # Raised TypeError (cannot pickle sqlite3.Connection) before the fix.
        copied = self.store.create_copy()
        self.assertIsNot(copied, self.store)
        self.assertIsInstance(copied, SQLiteStore)

    def test_copy_shares_the_live_connection(self) -> None:
        copied = self.store.create_copy()
        self.assertIs(copied.conn, self.store.conn)

    def test_shared_connection_stays_operational_from_the_copy(self) -> None:
        copied = self.store.create_copy()
        with copied.conn:
            copied.conn.execute("CREATE TABLE IF NOT EXISTS probe (x INTEGER)")
            copied.conn.execute("INSERT INTO probe (x) VALUES (42)")
        row = self.store.conn.execute("SELECT x FROM probe").fetchone()
        self.assertEqual(row[0], 42)

    def test_copy_isolates_sqlite_config_fields(self) -> None:
        copied = self.store.create_copy()
        copied.similarity_top_k = 99
        copied.k1 = 0.1
        copied.db_path = os.path.join(self._tmp.name, "other.db")
        self.assertEqual(self.store.similarity_top_k, 10)
        self.assertEqual(self.store.k1, 1.5)
        self.assertEqual(self.store.db_path, self.db_path)

    def test_successive_copies_of_initialized_store_are_distinct(self) -> None:
        first = self.store.create_copy()
        second = self.store.create_copy()
        self.assertIsNot(first, second)
        self.assertIs(first.conn, second.conn)


if __name__ == "__main__":
    unittest.main()
