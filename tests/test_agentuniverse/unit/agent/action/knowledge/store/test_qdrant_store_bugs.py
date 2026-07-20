#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for two QdrantStore bugs.

1. Dimension mismatch was not validated: the first document's embedding fixed
   the collection dimension, and every later document with a different
   dimension was rejected by the Qdrant server with an opaque error (or
   worse, partially written in a batch upsert).

2. delete_document passed the raw document id to Qdrant, but upsert had
   stored it under a UUID5 derived from that id. For every non-UUID document
   id the delete silently no-op'd because the ids never matched.
"""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.store.document import Document


class TestQdrantDimensionMismatch(unittest.TestCase):
    """Upsert must reject mixed-dimension batches explicitly."""

    def _store(self):
        from agentuniverse.agent.action.knowledge.store.qdrant_store import \
            QdrantStore
        store = QdrantStore()
        store.client = MagicMock()
        # Collection does not exist yet — dimension is inferred from the batch.
        store.client.collection_exists.return_value = False
        return store

    def test_mixed_dimensions_in_one_batch_raises_value_error(self):
        store = self._store()
        docs = [
            Document(id="d1", text="a", embedding=[0.1, 0.2, 0.3]),
            Document(id="d2", text="b", embedding=[0.1, 0.2]),  # dim 2 vs 3
        ]
        with self.assertRaises(ValueError) as ctx:
            store.upsert_document(docs)
        self.assertIn("dimension", str(ctx.exception).lower())
        self.assertIn("d2", str(ctx.exception))

    def test_consistent_dimensions_are_accepted(self):
        store = self._store()
        docs = [
            Document(id="d1", text="a", embedding=[0.1, 0.2]),
            Document(id="d2", text="b", embedding=[0.3, 0.4]),
        ]
        store.upsert_document(docs)
        store.client.upsert.assert_called_once()
        points = store.client.upsert.call_args.kwargs["points"]
        self.assertEqual(len(points), 2)

    def test_existing_collection_dimension_enforced_on_new_doc(self):
        from agentuniverse.agent.action.knowledge.store.qdrant_store import \
            QdrantStore
        store = QdrantStore()
        store.client = MagicMock()
        store.client.collection_exists.return_value = True
        # Existing collection is 3-dimensional.
        vector_cfg = MagicMock(size=3)
        info = MagicMock()
        info.config.params.vectors = {store.VECTOR_NAME: vector_cfg}
        store.client.get_collection.return_value = info

        # A 2-dim doc must be rejected against the 3-dim collection.
        with self.assertRaises(ValueError):
            store.upsert_document(
                [Document(id="d1", text="a", embedding=[0.1, 0.2])])


class TestQdrantDeleteIdMapping(unittest.TestCase):
    """delete must apply the same UUID5 mapping as upsert."""

    def test_non_uuid_id_uses_uuid5_on_both_upsert_and_delete(self):
        from agentuniverse.agent.action.knowledge.store.qdrant_store import \
            QdrantStore
        store = QdrantStore()
        store.client = MagicMock()
        store.client.collection_exists.return_value = False

        doc_id = "my-business-id-123"
        store.upsert_document(
            [Document(id=doc_id, text="a", embedding=[0.1, 0.2])])
        upserted_point_ids = [
            p.id for p in store.client.upsert.call_args.kwargs["points"]
        ]
        self.assertEqual(len(upserted_point_ids), 1)
        stored_id = upserted_point_ids[0]
        # The stored id is a UUID5, not the raw business id.
        self.assertNotEqual(stored_id, doc_id)

        # delete must send the SAME mapped id, not the raw business id.
        store.delete_document(doc_id)
        selector = store.client.delete.call_args.kwargs["points_selector"]
        self.assertEqual(selector, [stored_id],
                         "delete must map the document id the same way upsert "
                         "did; otherwise non-UUID ids silently fail to delete.")

    def test_uuid_id_is_preserved_on_both_paths(self):
        from agentuniverse.agent.action.knowledge.store.qdrant_store import \
            QdrantStore
        store = QdrantStore()
        store.client = MagicMock()
        store.client.collection_exists.return_value = False

        uuid_id = "12345678-1234-1234-1234-123456789abc"
        store.upsert_document(
            [Document(id=uuid_id, text="a", embedding=[0.1, 0.2])])
        stored_id = store.client.upsert.call_args.kwargs["points"][0].id
        self.assertEqual(stored_id, uuid_id)

        store.delete_document(uuid_id)
        selector = store.client.delete.call_args.kwargs["points_selector"]
        self.assertEqual(selector, [uuid_id])

    def test_point_id_helper_is_deterministic(self):
        from agentuniverse.agent.action.knowledge.store.qdrant_store import \
            QdrantStore
        # Same input always maps to same UUID5 — required so re-inserts
        # overwrite rather than create duplicates.
        a = QdrantStore._to_qdrant_point_id("consistent-id")
        b = QdrantStore._to_qdrant_point_id("consistent-id")
        self.assertEqual(a, b)
        # Different inputs map to different ids.
        c = QdrantStore._to_qdrant_point_id("other-id")
        self.assertNotEqual(a, c)


if __name__ == "__main__":
    unittest.main(verbosity=2)
