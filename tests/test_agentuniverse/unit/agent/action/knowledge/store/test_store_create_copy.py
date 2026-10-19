# !/usr/bin/env python3

# @Time    : 2026/10/03
# @FileName: test_store_create_copy.py

"""Tests for Store.create_copy isolation (issue #1183).

``create_copy`` used to return ``self``, so every
``get_instance_obj(..., new_instance=True)`` caller shared one mutable
Store. The fix copies mutable state deeply for instance isolation, with live
clients kept as shared references.
"""

import threading
import unittest

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
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


if __name__ == "__main__":
    unittest.main()
