#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for three ChromaStore / ChromaHierarchicalStore bugs.

1. ChromaHierarchicalStore.query extended a Chroma result dict into a list
   (which extends with the dict's keys) and then sorted those string keys
   by x['distance'] — a guaranteed TypeError on every multi-parent query.
2. ChromaHierarchicalStore.search_depth was typed ``int`` but defaulted to
   ``None``, so ``range(self.search_depth)`` raised TypeError whenever the
   user did not configure it.
3. ChromaStore._new_client called ``self.persist_path.startswith(...)`` on a
   None default, crashing before any helpful message; and a remote URL
   without an explicit port passed ``str(None) == "None"`` as the HTTP port.
"""

import unittest
from unittest.mock import MagicMock, patch


def _chroma_result(ids, documents, distances, metadatas=None,
                   embeddings=None):
    """Build a Chroma-style nested-list-of-lists query result dict."""
    return {
        "ids": [list(ids)],
        "documents": [list(documents)],
        "distances": [list(distances)],
        "metadatas": [list(metadatas)] if metadatas is not None else None,
        "embeddings": [list(embeddings)] if embeddings is not None else None,
    }


class TestChromaHierarchicalStoreFlattening(unittest.TestCase):
    """Multi-parent hierarchical queries must rank real documents, not crash."""

    def _store(self):
        from agentuniverse.agent.action.knowledge.store.\
            chroma_hierarchical_store import ChromaHierarchicalStore
        store = ChromaHierarchicalStore()
        store.collection = MagicMock()
        store.search_depth = 2
        store.similarity_top_k = 2
        store.similarity_top_k_list = []
        return store

    def test_multi_parent_query_does_not_crash_and_ranks_by_distance(self):
        from agentuniverse.agent.action.knowledge.store.query import Query
        store = self._store()
        # Depth 0 (root): two parent docs.
        store.collection.query.side_effect = [
            # depth 0 query (root level)
            _chroma_result(["p1", "p2"], ["parent 1", "parent 2"],
                           [0.1, 0.2]),
            # depth 1 query under p1
            _chroma_result(["c1"], ["child 1"], [0.3]),
            # depth 1 query under p2
            _chroma_result(["c2"], ["child 2"], [0.05]),
        ]
        results = store.query(Query(query_str="q", embeddings=[[0.1, 0.2]]))
        # The previous code raised TypeError: string indices must be integers
        # on the depth-1 branch (extend(dict) then sorted(key=['distance'])).
        ids = [r.id for r in results]
        # c2 (distance 0.05) ranks above c1 (distance 0.3).
        self.assertEqual(ids, ["c2", "c1"])

    def test_search_depth_none_does_not_crash(self):
        # Regression: search_depth used to default to None, and
        # range(None) raised TypeError before the query even ran.
        from agentuniverse.agent.action.knowledge.store.\
            chroma_hierarchical_store import ChromaHierarchicalStore
        from agentuniverse.agent.action.knowledge.store.query import Query

        # Construct without configuring search_depth; default is now 1.
        store = ChromaHierarchicalStore()
        store.collection = MagicMock()
        store.similarity_top_k = 1
        # Sanity: the default is a usable int, not None.
        self.assertIsNotNone(store.search_depth)
        store.collection.query.return_value = _chroma_result(
            ["d1"], ["doc"], [0.1])
        results = store.query(Query(query_str="q", embeddings=[[0.1]]))
        self.assertEqual([r.id for r in results], ["d1"])

    def test_flatten_chroma_results_handles_missing_optional_fields(self):
        from agentuniverse.agent.action.knowledge.store.\
            chroma_hierarchical_store import ChromaHierarchicalStore
        # Distances / metadatas / embeddings may be absent.
        flat = ChromaHierarchicalStore._flatten_chroma_results({
            "ids": [["a", "b"]],
            "documents": [["da", "db"]],
        })
        self.assertEqual([d["id"] for d in flat], ["a", "b"])
        self.assertEqual([d["distance"] for d in flat], [0.0, 0.0])
        self.assertTrue(all(d["metadata"] is None for d in flat))


class TestChromaStoreNewClientPersistPath(unittest.TestCase):
    """_new_client must handle None persist_path and port-less URLs."""

    def test_none_persist_path_raises_value_error_not_attribute_error(self):
        from agentuniverse.agent.action.knowledge.store.chroma_store import \
            ChromaStore
        store = ChromaStore()  # persist_path defaults to None
        with self.assertRaises(ValueError) as ctx:
            store._new_client()
        self.assertIn("persist_path", str(ctx.exception))

    def test_remote_url_without_port_defaults_to_8000(self):
        from agentuniverse.agent.action.knowledge.store.chroma_store import \
            ChromaStore
        store = ChromaStore(persist_path="http://chroma.example.com",
                            collection_name="c")
        captured_settings = []

        class _FakeSettings:
            def __init__(self, **kwargs):
                captured_settings.append(kwargs)

        with patch("agentuniverse.agent.action.knowledge.store."
                   "chroma_store.Settings", _FakeSettings), \
                patch("agentuniverse.agent.action.knowledge.store."
                   "chroma_store.chromadb"):
            store._new_client()
        # The previous code passed str(None) == "None" as the port.
        self.assertEqual(captured_settings[0]["chroma_server_http_port"],
                         "8000")
        self.assertEqual(captured_settings[0]["chroma_server_host"],
                         "chroma.example.com")

    def test_remote_url_with_explicit_port_is_preserved(self):
        from agentuniverse.agent.action.knowledge.store.chroma_store import \
            ChromaStore
        store = ChromaStore(persist_path="http://chroma.example.com:9000",
                            collection_name="c")
        captured_settings = []

        class _FakeSettings:
            def __init__(self, **kwargs):
                captured_settings.append(kwargs)

        with patch("agentuniverse.agent.action.knowledge.store."
                   "chroma_store.Settings", _FakeSettings), \
                patch("agentuniverse.agent.action.knowledge.store."
                   "chroma_store.chromadb"):
            store._new_client()
        self.assertEqual(captured_settings[0]["chroma_server_http_port"],
                         "9000")


if __name__ == "__main__":
    unittest.main(verbosity=2)
