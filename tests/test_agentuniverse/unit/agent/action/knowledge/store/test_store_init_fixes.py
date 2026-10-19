# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for store initialization bug fixes.

Covers three critical bugs:
1. MilvusStore: query_embedding config was assigned to similarity_top_k (typo)
2. ChromaStore: _new_client crashed with AttributeError when persist_path=None
3. FAISSStore: faiss/np module-level names were not set by lazy import in _new_client
"""

import unittest
from unittest.mock import MagicMock, patch

# ------------------------------------------------------------------ #
# Detect optional dependencies
# ------------------------------------------------------------------ #
try:
    import chromadb  # noqa: F401
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    import pymilvus  # noqa: F401
    PYMILVUS_AVAILABLE = True
except ImportError:
    PYMILVUS_AVAILABLE = False

try:
    import faiss  # noqa: F401
    import numpy as np  # noqa: F401
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


# ------------------------------------------------------------------ #
# 1. MilvusStore — query_embedding config assignment typo
# ------------------------------------------------------------------ #
@unittest.skipUnless(PYMILVUS_AVAILABLE, "pymilvus not available")
class TestMilvusStoreQueryEmbeddingConfig(unittest.TestCase):
    """Verify that query_embedding config is correctly assigned."""

    def test_query_embedding_config_assigned_correctly(self):
        """query_embedding=True should set self.query_embedding, not similarity_top_k."""
        from agentuniverse.agent.action.knowledge.store.milvus_store import MilvusStore

        store = MilvusStore()
        configer = MagicMock()
        configer.query_embedding = True
        configer.similarity_top_k = 42

        store._initialize_by_component_configer(configer)

        # query_embedding should be True (was previously ignored due to typo)
        self.assertTrue(store.query_embedding)
        # similarity_top_k should remain 42, not overwritten by the boolean True
        self.assertEqual(store.similarity_top_k, 42)

    def test_query_embedding_defaults_to_false(self):
        """When query_embedding is not in configer, default should be False."""
        from agentuniverse.agent.action.knowledge.store.milvus_store import MilvusStore

        store = MilvusStore()
        configer = MagicMock()
        # Don't set query_embedding attribute → hasattr returns False
        del configer.query_embedding

        store._initialize_by_component_configer(configer)

        self.assertFalse(store.query_embedding)


# ------------------------------------------------------------------ #
# 2. ChromaStore — persist_path=None guard
# ------------------------------------------------------------------ #
@unittest.skipUnless(CHROMA_AVAILABLE, "chromadb not available")
class TestChromaStorePersistPathNone(unittest.TestCase):
    """Verify that _new_client handles persist_path=None gracefully."""

    def test_new_client_with_none_persist_path(self):
        """_new_client should not crash with AttributeError when persist_path is None."""
        from agentuniverse.agent.action.knowledge.store.chroma_store import ChromaStore

        store = ChromaStore(persist_path=None)
        # This should not raise AttributeError: 'NoneType' object has no attribute 'startswith'
        try:
            client = store._new_client()
            self.assertIsNotNone(client)
        except AttributeError as e:
            if "'NoneType'" in str(e) and "startswith" in str(e):
                self.fail(f"_new_client crashed on persist_path=None: {e}")
            raise  # re-raise if it's a different AttributeError


# ------------------------------------------------------------------ #
# 3. FAISSStore — module-level faiss/np after _new_client
# ------------------------------------------------------------------ #
@unittest.skipUnless(FAISS_AVAILABLE, "faiss not available")
class TestFAISSStoreImportScope(unittest.TestCase):
    """Verify that faiss and np are accessible at module level after _new_client."""

    def test_new_client_populates_module_level_imports(self):
        """After _new_client, faiss and np should be available at module level."""
        import agentuniverse.agent.action.knowledge.store.faiss_store as faiss_module

        store = faiss_module.FAISSStore(
            index_path=None,
            metadata_path=None,
        )
        store._new_client()

        # faiss and np should now be set at module level
        self.assertIsNotNone(faiss_module.faiss, "module-level faiss should be populated")
        self.assertIsNotNone(faiss_module.np, "module-level np should be populated")

    def test_create_faiss_index_uses_module_level_faiss(self):
        """_create_faiss_index should not raise NameError after _new_client."""
        import agentuniverse.agent.action.knowledge.store.faiss_store as faiss_module

        store = faiss_module.FAISSStore(
            index_path=None,
            metadata_path=None,
        )
        store._new_client()

        # _create_faiss_index references faiss at module level — should not NameError
        index = store._create_faiss_index(dimension=4)
        self.assertIsNotNone(index)


if __name__ == '__main__':
    unittest.main()
