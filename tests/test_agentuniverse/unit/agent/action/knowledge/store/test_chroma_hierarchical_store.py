# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/22
# @Author  : Zzzzzmeow
# @FileName: test_chroma_hierarchical_store.py
"""Unit tests for ChromaHierarchicalStore multi-level query.

Two layers of coverage:
- Mock-based tests: pin the exact regression (int n_results, correct merge/sort)
  without needing a working chroma collection.
- In-memory chroma tests: end-to-end level-0 -> level-1 descent with explicit
  embeddings (no default embedding model download is triggered).
"""

import unittest
from unittest.mock import MagicMock

try:
    import chromadb  # noqa: F401

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


def _build_store(search_depth, similarity_top_k, top_k_list):
    from agentuniverse.agent.action.knowledge.store.chroma_hierarchical_store import ChromaHierarchicalStore

    return ChromaHierarchicalStore(
        collection_name="hier_test",
        similarity_top_k=similarity_top_k,
        search_depth=search_depth,
        similarity_top_k_list=top_k_list,
    )


@unittest.skipUnless(CHROMA_AVAILABLE, "chromadb not available")
class TestChromaHierarchicalStoreQueryMocked(unittest.TestCase):
    """Regression tests for the level-2+ branch, using a mocked collection."""

    def test_level_two_query_passes_integer_top_k_and_parent_filter(self):
        """The second-level query must send an int n_results and the parent filter."""
        store = _build_store(search_depth=2, similarity_top_k=2, top_k_list=[2, 1])
        collection = MagicMock()
        collection.query.return_value = {
            "ids": [["parent_1"]],
            "documents": [["parent one"]],
            "metadatas": [[{"hierarchical_level": 0}]],
            "embeddings": None,
            "distances": [[0.1]],
        }
        store.collection = collection

        # The previous implementation raised TypeError here (sorted() over
        # the QueryResult dict's keys) and passed a tuple as n_results.
        store.query(Query(query_str="parent one", embeddings=[[1.0, 0.0]]))

        self.assertEqual(collection.query.call_count, 2)
        second_call = collection.query.call_args_list[1]
        self.assertEqual(second_call.kwargs["n_results"], 1)
        self.assertIsInstance(second_call.kwargs["n_results"], int)
        self.assertEqual(second_call.kwargs["where"], {"hierarchical_parent": "parent_1"})

    def test_merged_children_are_ranked_by_distance_and_capped(self):
        """Children of multiple parents must be merged, ranked by distance and capped."""
        store = _build_store(search_depth=2, similarity_top_k=2, top_k_list=[2, 2])

        level0_result = {
            "ids": [["parent_1", "parent_2"]],
            "documents": [["parent one", "parent two"]],
            "metadatas": [[{"hierarchical_level": 0}, {"hierarchical_level": 0}]],
            "embeddings": None,
            "distances": [[0.1, 0.2]],
        }
        child_results = [
            {
                "ids": [["child_a", "child_b"]],
                "documents": [["child a", "child b"]],
                "metadatas": [[{"hierarchical_level": 1}, {"hierarchical_level": 1}]],
                "embeddings": None,
                "distances": [[0.5, 0.9]],
            },
            {
                "ids": [["child_c"]],
                "documents": [["child c"]],
                "metadatas": [[{"hierarchical_level": 1}]],
                "embeddings": None,
                "distances": [[0.3]],
            },
        ]
        collection = MagicMock()
        collection.query.side_effect = [level0_result] + child_results
        store.collection = collection

        docs = store.query(Query(query_str="parents", embeddings=[[1.0, 0.0]]))

        # Merged and ranked by distance: child_c (0.3), child_a (0.5), child_b (0.9).
        # similarity_top_k_list[1] = 2, so only the two closest survive.
        self.assertEqual([doc.id for doc in docs], ["child_c", "child_a"])


@unittest.skipUnless(CHROMA_AVAILABLE, "chromadb not available")
class TestChromaHierarchicalStoreQueryInMemory(unittest.TestCase):
    """End-to-end tests against an in-memory chroma collection."""

    def _build_and_seed(self, top_k_list):
        store = _build_store(search_depth=2, similarity_top_k=2, top_k_list=top_k_list)
        store._new_client()
        store.insert_document([
            Document(id="parent_1", text="parent one",
                     metadata={"hierarchical_level": 0}, embedding=[1.0, 0.0]),
            Document(id="parent_2", text="parent two",
                     metadata={"hierarchical_level": 0}, embedding=[0.0, 1.0]),
            Document(id="child_1", text="child one",
                     metadata={"hierarchical_level": 1, "hierarchical_parent": "parent_1"},
                     embedding=[1.0, 0.1]),
            Document(id="child_2", text="child two",
                     metadata={"hierarchical_level": 1, "hierarchical_parent": "parent_2"},
                     embedding=[0.0, 1.1]),
        ])
        return store

    def test_query_descends_to_child_level(self):
        """search_depth=2 must return level-1 children instead of crashing."""
        store = self._build_and_seed(top_k_list=[2, 2])

        docs = store.query(Query(query_str="parent one", embeddings=[[1.0, 0.0]]))

        self.assertTrue(docs)
        for doc in docs:
            self.assertEqual(doc.metadata["hierarchical_level"], 1)
            self.assertIn(doc.metadata["hierarchical_parent"], {"parent_1", "parent_2"})
        # Closest to the query vector: child_1 first.
        self.assertEqual(docs[0].id, "child_1")

    def test_child_level_respects_per_level_top_k(self):
        """similarity_top_k_list[1]=1 must cap the level-1 result to one doc."""
        store = self._build_and_seed(top_k_list=[2, 1])

        docs = store.query(Query(query_str="parent one", embeddings=[[1.0, 0.0]]))

        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].id, "child_1")

    def test_depth_one_returns_level_zero_only(self):
        """search_depth=1 keeps the previous behaviour: only level-0 documents."""
        store = _build_store(search_depth=1, similarity_top_k=2, top_k_list=[2])
        store._new_client()
        store.insert_document([
            Document(id="parent_1", text="parent one",
                     metadata={"hierarchical_level": 0}, embedding=[1.0, 0.0]),
            Document(id="child_1", text="child one",
                     metadata={"hierarchical_level": 1, "hierarchical_parent": "parent_1"},
                     embedding=[1.0, 0.1]),
        ])

        docs = store.query(Query(query_str="parent one", embeddings=[[1.0, 0.0]]))

        self.assertEqual([doc.id for doc in docs], ["parent_1"])


if __name__ == "__main__":
    unittest.main()
