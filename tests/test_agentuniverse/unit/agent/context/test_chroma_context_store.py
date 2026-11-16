# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/22
# @Author  : Zzzzzmeow
# @FileName: test_chroma_context_store.py
"""Unit tests for ChromaContextStore.count per-session filtering.

The count() method must report the number of segments stored for the given
session_id and never fall back to chroma's collection-wide Collection.count().
"""

import unittest
from unittest.mock import MagicMock

from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


class TestChromaContextStoreCount(unittest.TestCase):
    """ChromaContextStore.count() must report per-session totals."""

    def setUp(self):
        self.store = ChromaContextStore(name="test_chroma_context_store")
        self.collection = MagicMock()
        # Collection-wide total (what the buggy implementation returned).
        self.collection.count.return_value = 5
        self.collection.get.side_effect = self._fake_get
        self.store._collection = self.collection

    @staticmethod
    def _fake_get(where=None, include=None, **kwargs):
        session_ids = {
            "session_1": ["session_1:seg1", "session_1:seg2", "session_1:seg3"],
            "session_2": ["session_2:seg1"],
        }
        return {"ids": session_ids.get(where["session_id"], [])}

    def test_count_returns_per_session_total(self):
        self.assertEqual(self.store.count("session_1"), 3)
        self.assertEqual(self.store.count("session_2"), 1)

    def test_count_returns_zero_for_unknown_session(self):
        self.assertEqual(self.store.count("missing_session"), 0)

    def test_count_does_not_use_collection_wide_count(self):
        """count() must never fall back to the unfiltered Collection.count()."""
        self.store.count("session_1")
        self.collection.count.assert_not_called()

    def test_count_filters_by_session_id_in_where(self):
        self.store.count("session_1")
        self.collection.get.assert_called_once()
        self.assertEqual(
            self.collection.get.call_args.kwargs["where"],
            {"session_id": "session_1"},
        )

    def test_count_returns_zero_when_collection_unavailable(self):
        store = ChromaContextStore(name="empty_store")
        self.assertEqual(store.count("any_session"), 0)


if __name__ == "__main__":
    unittest.main()
