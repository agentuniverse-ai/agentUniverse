#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for MilvusStore upsert injection and native-upsert preference.

The previous upsert_document built the existence-check expression with an
f-string: ``f'id == "{document.id}"'``. A document id containing a double
quote could escape the Milvus filter literal and inject arbitrary predicates
(or crash the query). Also, the manual query/delete/insert sequence is
non-atomic; modern pymilvus exposes a native ``Collection.upsert`` that
sidesteps both problems.
"""

import unittest
from unittest.mock import MagicMock

from agentuniverse.agent.action.knowledge.store.document import Document


class TestMilvusValidateFilterableId(unittest.TestCase):
    """The legacy fallback path must reject ids that escape the filter literal."""

    def test_safe_id_is_accepted(self):
        from agentuniverse.agent.action.knowledge.store.milvus_store import \
            MilvusStore
        # Should not raise.
        MilvusStore._validate_filterable_id("doc-123")
        MilvusStore._validate_filterable_id("a" * 64)

    def test_id_with_double_quote_is_rejected(self):
        from agentuniverse.agent.action.knowledge.store.milvus_store import \
            MilvusStore
        with self.assertRaises(ValueError):
            MilvusStore._validate_filterable_id('a" or id != "')

    def test_id_with_backslash_is_rejected(self):
        from agentuniverse.agent.action.knowledge.store.milvus_store import \
            MilvusStore
        with self.assertRaises(ValueError):
            MilvusStore._validate_filterable_id("a\\b")

    def test_empty_or_non_string_id_is_rejected(self):
        from agentuniverse.agent.action.knowledge.store.milvus_store import \
            MilvusStore
        with self.assertRaises(ValueError):
            MilvusStore._validate_filterable_id("")
        with self.assertRaises(ValueError):
            MilvusStore._validate_filterable_id(None)


class TestMilvusUpsertUsesNativeWhenAvailable(unittest.TestCase):
    """When Collection.upsert exists, use it (atomic + no filter expression)."""

    def _store_with_collection(self, has_upsert: bool):
        from agentuniverse.agent.action.knowledge.store.milvus_store import \
            MilvusStore
        store = MilvusStore()
        collection = MagicMock()
        if not has_upsert:
            del collection.upsert
        store.collection = collection
        return store, collection

    def test_native_upsert_called_when_available(self):
        store, collection = self._store_with_collection(has_upsert=True)
        store.upsert_document(
            [Document(id="d1", text="a", embedding=[0.1, 0.2, 0.3])])
        collection.upsert.assert_called_once()
        # The query/delete path must NOT run when native upsert is available.
        collection.query.assert_not_called()
        collection.delete.assert_not_called()

    def test_fallback_path_validates_id_before_querying(self):
        store, collection = self._store_with_collection(has_upsert=False)
        collection.query.return_value = []
        # A safe id goes through query/insert.
        store.upsert_document(
            [Document(id="safe-id", text="a", embedding=[0.1, 0.2, 0.3])])
        collection.query.assert_called_once_with('id == "safe-id"')

    def test_fallback_path_rejects_injection_id(self):
        store, collection = self._store_with_collection(has_upsert=False)
        # An id that would escape the filter literal must be rejected before
        # it ever reaches query().
        with self.assertRaises(ValueError):
            store.upsert_document(
                [Document(id='x" or "1" == "1', text="a",
                          embedding=[0.1, 0.2, 0.3])])
        collection.query.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
