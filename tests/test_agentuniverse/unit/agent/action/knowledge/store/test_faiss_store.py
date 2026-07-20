# !/usr/bin/env python3

# @Time    : 2024/12/28 12:00
# @Author  : saswatsusmoy
# @Email   : saswatsusmoy9@gmail.com
# @FileName: test_faiss_store.py

import json
import logging
import os
import pickle
import shutil
import tempfile
import unittest
from unittest.mock import Mock, patch

try:
    import faiss  # noqa: F401
    import numpy as np  # noqa: F401

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


@unittest.skipUnless(FAISS_AVAILABLE, "FAISS not available")
class TestFAISSStore(unittest.TestCase):
    """Comprehensive test cases for FAISS Store."""

    @classmethod
    def setUpClass(cls):
        """Set up class-level test fixtures."""
        # Suppress logging during tests
        logging.getLogger("agentuniverse.agent.action.knowledge.store.faiss_store").setLevel(logging.CRITICAL)

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = os.path.join(self.temp_dir, "test_faiss.index")
        self.metadata_path = os.path.join(self.temp_dir, "test_faiss_metadata.pkl")

        # Import here to avoid import error when FAISS is not available
        from agentuniverse.agent.action.knowledge.store.faiss_store import FAISSStore

        self.FAISSStore = FAISSStore

        # Create test documents with embeddings
        self.test_documents = [
            Document(
                id="doc1",
                text="Python is a high-level programming language known for its simplicity.",
                metadata={"category": "programming", "language": "python", "complexity": "beginner"},
                embedding=[0.1, 0.2, 0.3, 0.4],
            ),
            Document(
                id="doc2",
                text="Machine learning is a subset of artificial intelligence that focuses on algorithms.",
                metadata={"category": "AI", "field": "machine_learning", "complexity": "advanced"},
                embedding=[0.5, 0.6, 0.7, 0.8],
            ),
            Document(
                id="doc3",
                text="FAISS is a library for efficient similarity search and clustering of dense vectors.",
                metadata={"category": "technology", "library": "faiss", "complexity": "intermediate"},
                embedding=[0.9, 1.0, 1.1, 1.2],
            ),
            Document(
                id="doc4",
                text="Natural language processing enables computers to understand human language.",
                metadata={"category": "AI", "field": "nlp", "complexity": "advanced"},
                embedding=[0.2, 0.4, 0.6, 0.8],
            ),
            Document(
                id="doc5",
                text="Data structures are fundamental concepts in computer science.",
                metadata={"category": "programming", "topic": "data_structures", "complexity": "intermediate"},
                embedding=[0.3, 0.1, 0.4, 0.2],
            ),
        ]

        # Create large dataset for performance testing
        self.large_dataset = []
        for i in range(100):
            self.large_dataset.append(
                Document(
                    id=f"large_doc_{i}",
                    text=f"This is document number {i} for performance testing.",
                    metadata={"batch": "performance_test", "index": i},
                    embedding=[i * 0.01, (i + 1) * 0.01, (i + 2) * 0.01, (i + 3) * 0.01],
                )
            )

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_store(self, index_type="IndexFlatL2", **kwargs):
        """Helper method to create a FAISS store for testing."""
        config = {"index_type": index_type, "dimension": 4}  # Small dimension for testing
        config.update(kwargs)

        store = self.FAISSStore(
            index_path=self.index_path,
            metadata_path=self.metadata_path,
            embedding_model=None,  # No embedding model for tests
            similarity_top_k=5,
            index_config=config,
        )
        return store

    def test_initialization_and_configuration(self):
        """Test FAISS store initialization and configuration."""
        store = self.create_store()
        store._new_client()

        # Test basic configuration
        self.assertEqual(store.similarity_top_k, 5)
        self.assertEqual(store.index_config["index_type"], "IndexFlatL2")
        self.assertEqual(store.index_config["dimension"], 4)
        self.assertIsNotNone(store.document_store)
        self.assertIsNotNone(store.id_to_index)
        self.assertIsNotNone(store.index_to_id)
        self.assertEqual(store._next_index, 0)

    def test_index_creation_all_types(self):
        """Test creation of all supported index types."""
        index_configs = [
            {"index_type": "IndexFlatL2"},
            {"index_type": "IndexFlatIP"},
            {"index_type": "IndexIVFFlat", "nlist": 4, "nprobe": 2},
            {"index_type": "IndexIVFPQ", "nlist": 4, "nprobe": 2, "m": 2, "nbits": 8},
            {"index_type": "IndexHNSWFlat", "M": 8, "efConstruction": 40, "efSearch": 20},
        ]

        for config in index_configs:
            with self.subTest(index_type=config["index_type"]):
                store = self.create_store(**config)
                store._new_client()

                # Insert documents to trigger index creation
                store.insert_document(self.test_documents)
                self.assertIsNotNone(store.faiss_index)
                self.assertEqual(store.get_document_count(), 5)

    def test_unsupported_index_type(self):
        """Test handling of unsupported index types."""
        store = self.create_store(index_type="UnsupportedIndexType")

        with self.assertRaises(ValueError) as context:
            store._create_faiss_index(4)

        self.assertIn("Unsupported index type", str(context.exception))

    def test_insert_and_query_comprehensive(self):
        """Test comprehensive document insertion and querying."""
        store = self.create_store()
        store._new_client()

        # Test empty store
        self.assertEqual(store.get_document_count(), 0)

        # Insert documents
        store.insert_document(self.test_documents)
        self.assertEqual(store.get_document_count(), 5)

        # Test document retrieval by ID
        doc = store.get_document_by_id("doc1")
        self.assertIsNotNone(doc)
        self.assertEqual(doc.text, "Python is a high-level programming language known for its simplicity.")
        self.assertEqual(doc.metadata["category"], "programming")

        # Test query with exact embedding match
        query = Query(embeddings=[[0.1, 0.2, 0.3, 0.4]])  # Exact match for doc1
        results = store.query(query)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].id, "doc1")

        # Test query with similarity_top_k
        query_limited = Query(embeddings=[[0.1, 0.2, 0.3, 0.4]], similarity_top_k=3)
        results_limited = store.query(query_limited)
        self.assertLessEqual(len(results_limited), 3)

        # Test query with no embeddings and no embedding model
        empty_query = Query(query_str="test query without embeddings")
        empty_results = store.query(empty_query)
        self.assertEqual(len(empty_results), 0)

    def test_crud_operations_comprehensive(self):
        """Test comprehensive CRUD operations."""
        store = self.create_store()
        store._new_client()

        # CREATE: Insert initial documents
        initial_docs = self.test_documents[:3]
        store.insert_document(initial_docs)
        self.assertEqual(store.get_document_count(), 3)

        # READ: Query and retrieve documents
        doc = store.get_document_by_id("doc2")
        self.assertIsNotNone(doc)
        self.assertEqual(doc.metadata["field"], "machine_learning")

        # UPDATE: Update existing document
        updated_doc = Document(
            id="doc2",
            text="Updated: Machine learning is an advanced field of artificial intelligence.",
            metadata={"category": "AI", "field": "machine_learning", "complexity": "expert", "updated": True},
            embedding=[0.55, 0.65, 0.75, 0.85],
        )
        store.update_document([updated_doc])

        # Verify update
        retrieved_doc = store.get_document_by_id("doc2")
        self.assertIn("Updated:", retrieved_doc.text)
        self.assertEqual(retrieved_doc.metadata["complexity"], "expert")
        self.assertTrue(retrieved_doc.metadata["updated"])

        # UPSERT: Insert new document and update existing
        new_doc = Document(
            id="doc_new",
            text="This is a new document added via upsert.",
            metadata={"category": "test", "method": "upsert"},
            embedding=[0.7, 0.8, 0.9, 1.0],
        )
        another_update = Document(
            id="doc1",
            text="Updated doc1 via upsert operation.",
            metadata={"category": "programming", "language": "python", "updated_via": "upsert"},
            embedding=[0.15, 0.25, 0.35, 0.45],
        )

        store.upsert_document([new_doc, another_update])
        self.assertEqual(store.get_document_count(), 4)  # 3 original + 1 new

        upserted_new = store.get_document_by_id("doc_new")
        self.assertIsNotNone(upserted_new)
        self.assertEqual(upserted_new.metadata["method"], "upsert")

        upserted_existing = store.get_document_by_id("doc1")
        self.assertIn("Updated doc1", upserted_existing.text)

        # DELETE: Remove documents
        store.delete_document("doc2")
        self.assertEqual(store.get_document_count(), 3)
        self.assertIsNone(store.get_document_by_id("doc2"))

        # DELETE: Try to delete non-existent document (should not raise error)
        store.delete_document("non_existent_doc")
        self.assertEqual(store.get_document_count(), 3)

    def test_persistence_comprehensive(self):
        """Test comprehensive persistence functionality."""
        # Create and populate first store
        store1 = self.create_store()
        store1._new_client()
        store1.insert_document(self.test_documents)

        # Verify files were created
        self.assertTrue(os.path.exists(self.index_path))
        self.assertTrue(os.path.exists(self.metadata_path))

        # Create second store (should load persisted data)
        store2 = self.create_store()
        store2._new_client()

        # Verify data was loaded correctly
        self.assertEqual(store2.get_document_count(), 5)
        self.assertEqual(len(store2.list_document_ids()), 5)

        # Verify specific document
        doc = store2.get_document_by_id("doc3")
        self.assertIsNotNone(doc)
        self.assertIn("FAISS", doc.text)
        self.assertEqual(doc.metadata["library"], "faiss")

        # Test query on loaded store
        query = Query(embeddings=[[0.9, 1.0, 1.1, 1.2]])  # Should match doc3
        results = store2.query(query)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].id, "doc3")

    def test_error_handling_and_edge_cases(self):
        """Test error handling and edge cases."""
        store = self.create_store()
        store._new_client()

        # Test inserting empty document list
        store.insert_document([])
        self.assertEqual(store.get_document_count(), 0)

        # Test inserting documents without embeddings and no embedding model
        doc_no_embedding = Document(id="no_embed", text="Document without embedding", embedding=[])
        store.insert_document([doc_no_embedding])
        self.assertEqual(store.get_document_count(), 0)  # Should be skipped

        # Test duplicate document insertion
        doc1 = Document(id="dup", text="Original", embedding=[0.1, 0.2, 0.3, 0.4])
        doc2 = Document(id="dup", text="Duplicate", embedding=[0.2, 0.3, 0.4, 0.5])

        store.insert_document([doc1])
        self.assertEqual(store.get_document_count(), 1)

        store.insert_document([doc2])  # Should be skipped due to duplicate ID
        self.assertEqual(store.get_document_count(), 1)
        self.assertEqual(store.get_document_by_id("dup").text, "Original")

        # Test querying empty store
        empty_temp_dir = tempfile.mkdtemp()
        empty_index_path = os.path.join(empty_temp_dir, "empty_faiss.index")
        empty_metadata_path = os.path.join(empty_temp_dir, "empty_faiss_metadata.pkl")

        empty_store = self.FAISSStore(
            index_path=empty_index_path,
            metadata_path=empty_metadata_path,
            embedding_model=None,
            index_config={"index_type": "IndexFlatL2", "dimension": 4},
        )
        empty_store._new_client()
        query = Query(embeddings=[[0.1, 0.2, 0.3, 0.4]])
        results = empty_store.query(query)
        self.assertEqual(len(results), 0)

        # Clean up empty store temp directory
        shutil.rmtree(empty_temp_dir)

        # Test invalid query
        invalid_query = Query()  # No embeddings or query_str
        results = store.query(invalid_query)
        self.assertEqual(len(results), 0)

        # Test querying with documents that have embeddings
        query_with_embedding = Query(embeddings=[[0.1, 0.2, 0.3, 0.4]])
        results_with_embedding = store.query(query_with_embedding)
        self.assertGreater(len(results_with_embedding), 0)

    def test_performance_with_large_dataset(self):
        """Test performance with larger dataset."""
        store = self.create_store(index_type="IndexHNSWFlat", M=8, efConstruction=40)
        store._new_client()

        # Insert large dataset
        import time

        start_time = time.time()
        store.insert_document(self.large_dataset)
        insert_time = time.time() - start_time

        self.assertEqual(store.get_document_count(), 100)
        self.assertLess(insert_time, 10.0)  # Should complete within 10 seconds

        # Test batch query performance
        queries = [
            Query(embeddings=[[i * 0.01, (i + 1) * 0.01, (i + 2) * 0.01, (i + 3) * 0.01]]) for i in range(0, 10, 2)
        ]

        start_time = time.time()
        for query in queries:
            results = store.query(query)
            self.assertGreater(len(results), 0)
        query_time = time.time() - start_time

        self.assertLess(query_time, 5.0)  # Should complete within 5 seconds

    def test_different_embedding_dimensions(self):
        """Test handling of different embedding dimensions."""
        # Test with different dimensions
        dimensions = [2, 8, 16, 32]

        for dim in dimensions:
            with self.subTest(dimension=dim):
                config = {"index_type": "IndexFlatL2", "dimension": dim}
                temp_index = os.path.join(self.temp_dir, f"test_{dim}d.index")
                temp_metadata = os.path.join(self.temp_dir, f"test_{dim}d_metadata.pkl")

                store = self.FAISSStore(
                    index_path=temp_index, metadata_path=temp_metadata, embedding_model=None, index_config=config
                )
                store._new_client()

                # Create document with appropriate dimension
                doc = Document(
                    id=f"doc_{dim}d", text=f"Document with {dim}-dimensional embedding", embedding=[0.1] * dim
                )

                store.insert_document([doc])
                self.assertEqual(store.get_document_count(), 1)

                # Query with same dimension
                query = Query(embeddings=[[0.1] * dim])
                results = store.query(query)
                self.assertEqual(len(results), 1)

    def test_metadata_operations(self):
        """Test metadata-related operations."""
        store = self.create_store()
        store._new_client()

        # Insert documents with rich metadata
        store.insert_document(self.test_documents)

        # Test listing document IDs
        doc_ids = store.list_document_ids()
        expected_ids = {"doc1", "doc2", "doc3", "doc4", "doc5"}
        self.assertEqual(set(doc_ids), expected_ids)

        # Test document count
        self.assertEqual(store.get_document_count(), 5)

        # Test metadata preservation in query results
        query = Query(embeddings=[[0.1, 0.2, 0.3, 0.4]])
        results = store.query(query)

        # Check that metadata is preserved and score is added
        result_doc = results[0]
        self.assertIn("category", result_doc.metadata)
        self.assertIn("score", result_doc.metadata)
        self.assertIsInstance(result_doc.metadata["score"], float)

    def test_component_configer_initialization(self):
        """Test initialization from component configuration."""
        # Create mock configer
        configer = Mock(spec=ComponentConfiger)
        configer.name = "test_faiss_store"
        configer.description = "Test FAISS store from configer"
        configer.index_path = self.index_path
        configer.metadata_path = self.metadata_path
        configer.embedding_model = "test_embedding_model"
        configer.similarity_top_k = 10
        configer.index_config = {"index_type": "IndexHNSWFlat", "dimension": 8, "M": 12, "efConstruction": 150}

        store = self.FAISSStore()
        store._initialize_by_component_configer(configer)

        self.assertEqual(store.name, "test_faiss_store")
        self.assertEqual(store.description, "Test FAISS store from configer")
        self.assertEqual(store.index_path, self.index_path)
        self.assertEqual(store.metadata_path, self.metadata_path)
        self.assertEqual(store.embedding_model, "test_embedding_model")
        self.assertEqual(store.similarity_top_k, 10)
        self.assertEqual(store.index_config["index_type"], "IndexHNSWFlat")
        self.assertEqual(store.index_config["M"], 12)

    def test_concurrent_operations_safety(self):
        """Test thread safety and concurrent operations."""
        import threading
        import time

        store = self.create_store()
        store._new_client()

        # Insert initial documents
        store.insert_document(self.test_documents[:3])

        results = []
        errors = []

        def query_worker():
            try:
                for i in range(10):
                    query = Query(embeddings=[[0.1 + i * 0.01, 0.2, 0.3, 0.4]])
                    result = store.query(query)
                    results.append(len(result))
                    time.sleep(0.01)
            except Exception as e:
                errors.append(str(e))

        def insert_worker():
            try:
                for i in range(5):
                    doc = Document(
                        id=f"concurrent_{i}", text=f"Concurrent document {i}", embedding=[0.1 + i * 0.1, 0.2, 0.3, 0.4]
                    )
                    store.insert_document([doc])
                    time.sleep(0.02)
            except Exception as e:
                errors.append(str(e))

        # Start concurrent operations
        query_thread = threading.Thread(target=query_worker)
        insert_thread = threading.Thread(target=insert_worker)

        query_thread.start()
        insert_thread.start()

        query_thread.join(timeout=5.0)
        insert_thread.join(timeout=5.0)

        # Check that operations completed without errors
        self.assertEqual(len(errors), 0, f"Concurrent operations failed: {errors}")
        self.assertEqual(len(results), 10)  # All queries should have completed
        self.assertGreaterEqual(store.get_document_count(), 3)  # At least original documents

    def test_memory_efficiency(self):
        """Test memory efficiency with various index types."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Test memory usage with different index types
        index_types = ["IndexFlatL2", "IndexIVFPQ"]

        for index_type in index_types:
            with self.subTest(index_type=index_type):
                config = {"nlist": 4, "m": 2, "nbits": 8} if "IVF" in index_type else {}

                store = self.create_store(index_type=index_type, **config)
                store._new_client()

                # Insert moderate dataset
                store.insert_document(self.large_dataset[:50])

                current_memory = process.memory_info().rss
                memory_increase = current_memory - initial_memory

                # Memory increase should be reasonable (less than 100MB for test data)
                self.assertLess(
                    memory_increase,
                    100 * 1024 * 1024,
                    f"Memory usage too high for {index_type}: {memory_increase / 1024 / 1024:.2f}MB",
                )

    def test_data_integrity_after_operations(self):
        """Test data integrity after various operations."""
        store = self.create_store()
        store._new_client()

        # Insert initial data
        store.insert_document(self.test_documents)
        original_count = store.get_document_count()

        # Perform various operations
        store.delete_document("doc2")
        store.upsert_document(
            [Document(id="new_doc", text="New document for integrity test", embedding=[0.8, 0.7, 0.6, 0.5])]
        )

        # Verify integrity
        current_ids = set(store.list_document_ids())
        self.assertNotIn("doc2", current_ids)
        self.assertIn("new_doc", current_ids)
        self.assertEqual(len(current_ids), original_count)  # Same count (deleted 1, added 1)

        # Verify each document can be retrieved and queried
        for doc_id in current_ids:
            doc = store.get_document_by_id(doc_id)
            self.assertIsNotNone(doc, f"Document {doc_id} should be retrievable")

            # Query with document's own embedding
            if doc.embedding:
                query = Query(embeddings=[doc.embedding])
                results = store.query(query)
                self.assertGreater(len(results), 0, f"Document {doc_id} should be queryable")


class _RCEPickleBomb:
    """A pickle payload that creates a marker file when unpickled.

    Defined at module scope so it is genuinely unpicklable. Used to prove the
    FAISS metadata loader never calls ``pickle.load``: if it did, unpickling an
    instance would create the marker file.
    """

    def __init__(self, marker_path: str):
        self._marker = marker_path

    def __reduce__(self):
        return (open, (self._marker, "w"))


class TestFAISSStoreMetadataSerialization(unittest.TestCase):
    """Metadata persistence is JSON (not pickle) and round-trips without FAISS.

    These tests exercise the metadata read/write helpers directly, so they run
    even when the optional FAISS dependency is absent. They lock in the security
    fix: persisted metadata is JSON, so loading it cannot execute code.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.metadata_path = os.path.join(self.temp_dir, "metadata.json")
        from agentuniverse.agent.action.knowledge.store.faiss_store import FAISSStore

        self.FAISSStore = FAISSStore

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _store(self, metadata_path=None) -> "FAISSStore":
        return self.FAISSStore(
            index_path=None,
            metadata_path=self.metadata_path if metadata_path is None else metadata_path,
            embedding_model=None,
        )

    def test_metadata_round_trips_as_json(self):
        store = self._store()
        store.document_store = {
            "doc1": Document(
                id="doc1",
                text="hello world",
                metadata={"category": "demo", "score": 0.5},
                embedding=[0.1, 0.2, 0.3],
                keywords={"ai", "rag"},
            ),
        }
        store.id_to_index = {"doc1": 0}
        store.index_to_id = {0: "doc1"}
        store._next_index = 1

        store._write_metadata_file()

        # The file on disk is genuine JSON, not a pickle bytestream.
        with open(self.metadata_path, encoding="utf-8") as f:
            raw = json.load(f)
        self.assertEqual(raw["format"], "faiss-store-metadata-v1")

        loaded = self._store()
        self.assertTrue(loaded._read_metadata_file())

        doc = loaded.document_store["doc1"]
        self.assertEqual(doc.text, "hello world")
        self.assertEqual(doc.metadata["category"], "demo")
        self.assertEqual(doc.embedding, [0.1, 0.2, 0.3])
        self.assertEqual(doc.keywords, {"ai", "rag"})
        self.assertEqual(loaded.id_to_index, {"doc1": 0})
        # Integer FAISS positions survive the JSON string-key round-trip.
        self.assertEqual(loaded.index_to_id, {0: "doc1"})
        self.assertIsInstance(next(iter(loaded.index_to_id)), int)
        self.assertEqual(loaded._next_index, 1)

    def test_missing_metadata_file_returns_false(self):
        store = self._store(metadata_path=os.path.join(self.temp_dir, "absent.json"))
        self.assertFalse(store._read_metadata_file())

    def test_legacy_pickle_payload_is_not_executed(self):
        marker = os.path.join(self.temp_dir, "pwned_marker")
        with open(self.metadata_path, "wb") as f:
            pickle.dump(_RCEPickleBomb(marker), f)

        store = self._store()
        # The loader must treat the pickle file as invalid JSON and reset,
        # without ever unpickling (executing) it.
        self.assertFalse(store._read_metadata_file())
        self.assertFalse(os.path.exists(marker), "pickle payload was executed during metadata load — RCE!")
        self.assertEqual(store.get_document_count(), 0)

    # -- reviewer regressions: schema validation + atomic write --

    def _seed_valid_store(self):
        store = self._store()
        store.document_store = {
            "doc1": Document(id="doc1", text="hello", embedding=[0.1, 0.2]),
        }
        store.id_to_index = {"doc1": 0}
        store.index_to_id = {0: "doc1"}
        store._next_index = 1
        store._write_metadata_file()
        return store

    def test_wrong_format_marker_resets_store(self):
        self._seed_valid_store()
        # Tamper with the format marker only; everything else is valid JSON.
        with open(self.metadata_path, encoding="utf-8") as f:
            data = json.load(f)
        data["format"] = "some-other-format-v2"
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        store = self._store()
        self.assertFalse(store._read_metadata_file())
        # The store is fully reset, not half-populated.
        self.assertEqual(store.get_document_count(), 0)
        self.assertEqual(store.id_to_index, {})
        self.assertEqual(store.index_to_id, {})

    def test_top_level_non_object_resets_store(self):
        # Syntactically valid JSON, but the top level is a list, not an object.
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump([{"format": "faiss-store-metadata-v1"}], f)
        store = self._store()
        self.assertFalse(store._read_metadata_file())
        self.assertEqual(store.get_document_count(), 0)

    def test_invalid_document_payload_resets_store(self):
        self._seed_valid_store()
        with open(self.metadata_path, encoding="utf-8") as f:
            data = json.load(f)
        # document_store entry is not a dict -> Document(**doc_data) would fail.
        data["document_store"]["doc1"] = "not-an-object"
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        store = self._store()
        self.assertFalse(store._read_metadata_file())
        # Whole set discarded; no partial population.
        self.assertEqual(store.get_document_count(), 0)

    def test_non_integer_index_to_id_key_resets_store(self):
        self._seed_valid_store()
        with open(self.metadata_path, encoding="utf-8") as f:
            data = json.load(f)
        # A non-integer position key cannot be restored to an int FAISS slot.
        data["index_to_id"] = {"not-a-number": "doc1"}
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        store = self._store()
        self.assertFalse(store._read_metadata_file())
        self.assertEqual(store.index_to_id, {})

    def test_metadata_write_is_atomic(self):
        # An interrupted write must not corrupt the last good file: write a
        # valid file, then force a failure during the atomic replace step, and
        # verify the previous version is intact and no temp file leaked.
        store = self._seed_valid_store()
        with open(self.metadata_path, encoding="utf-8") as f:
            first_snapshot = f.read()

        # Patch os.replace to raise; the write must swallow the error and clean
        # up its temp file rather than leaving a half-written metadata.json.
        with patch(
            "agentuniverse.agent.action.knowledge.store.faiss_store.os.replace",
            side_effect=OSError("simulated crash"),
        ):
            store._write_metadata_file()

        # The previously-written good file is untouched.
        with open(self.metadata_path, encoding="utf-8") as f:
            self.assertEqual(f.read(), first_snapshot)
        # No stale temp files leaked in the directory.
        leftovers = [n for n in os.listdir(self.temp_dir) if n.startswith(".faiss-metadata-")]
        self.assertEqual(leftovers, [], f"stale temp files left behind: {leftovers}")

        # And a subsequent clean write still round-trips.
        store.document_store["doc2"] = Document(id="doc2", text="two", embedding=[0.3, 0.4])
        store.id_to_index["doc2"] = 1
        store.index_to_id[1] = "doc2"
        store._next_index = 2
        store._write_metadata_file()
        reloaded = self._store()
        self.assertTrue(reloaded._read_metadata_file())
        self.assertEqual(reloaded.get_document_count(), 2)


class TestFAISSStoreMetadataRelationalInvariants(unittest.TestCase):
    """The payload must satisfy cross-field invariants, not just field types.

    The index file and the metadata file are persisted separately, so a crash
    (or a hand-edit) can leave them internally inconsistent. These tests pin
    each invariant the loader enforces.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.metadata_path = os.path.join(self.temp_dir, "metadata.json")
        from agentuniverse.agent.action.knowledge.store.faiss_store import FAISSStore
        self.FAISSStore = FAISSStore

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _store(self):
        return self.FAISSStore(
            index_path=None,
            metadata_path=self.metadata_path,
            embedding_model=None,
        )

    def _valid_payload(self) -> dict:
        return {
            "format": "faiss-store-metadata-v1",
            "document_store": {
                "doc1": {"id": "doc1", "text": "one", "embedding": [0.1, 0.2]},
                "doc2": {"id": "doc2", "text": "two", "embedding": [0.3, 0.4]},
            },
            "id_to_index": {"doc1": 0, "doc2": 1},
            "index_to_id": {"0": "doc1", "1": "doc2"},
            "next_index": 2,
        }

    def _write_payload(self, payload: dict) -> None:
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(payload, f)

    def test_document_id_mismatch_with_key_is_rejected(self) -> None:
        payload = self._valid_payload()
        # Key says doc1, but the persisted Document.id disagrees.
        payload["document_store"]["doc1"] = {"id": "docX", "text": "one", "embedding": [0.1, 0.2]}
        self._write_payload(payload)
        self.assertFalse(self._store()._read_metadata_file())

    def test_non_inverse_mappings_are_rejected(self) -> None:
        payload = self._valid_payload()
        # id_to_index maps doc1 -> 0, but index_to_id maps 0 -> doc2.
        payload["index_to_id"] = {"0": "doc2", "1": "doc1"}
        self._write_payload(payload)
        self.assertFalse(self._store()._read_metadata_file())

    def test_mapping_references_missing_document_is_rejected(self) -> None:
        payload = self._valid_payload()
        # id_to_index references doc3 which is not in document_store.
        payload["id_to_index"]["doc3"] = 2
        payload["index_to_id"]["2"] = "doc3"
        payload["next_index"] = 3
        self._write_payload(payload)
        self.assertFalse(self._store()._read_metadata_file())

    def test_next_index_not_past_highest_position_is_rejected(self) -> None:
        payload = self._valid_payload()
        # Highest used position is 1, but next_index says 1 — the next insert
        # would collide with position 1.
        payload["next_index"] = 1
        self._write_payload(payload)
        self.assertFalse(self._store()._read_metadata_file())

    def test_negative_position_is_rejected(self) -> None:
        payload = self._valid_payload()
        payload["id_to_index"] = {"doc1": -1, "doc2": 1}
        payload["index_to_id"] = {"-1": "doc1", "1": "doc2"}
        self._write_payload(payload)
        self.assertFalse(self._store()._read_metadata_file())

    def test_ntotal_mismatch_against_loaded_index_is_rejected(self) -> None:
        # The metadata maps 2 vectors, but we tell validation the loaded FAISS
        # index holds 5 — a generation mismatch between the two files.
        store = self._store()
        self._write_payload(self._valid_payload())
        self.assertFalse(store._read_metadata_file(faiss_ntotal=5))

    def test_ntotal_match_is_accepted(self) -> None:
        store = self._store()
        self._write_payload(self._valid_payload())
        self.assertTrue(store._read_metadata_file(faiss_ntotal=2))


@unittest.skipUnless(FAISS_AVAILABLE, "FAISS not available")
class TestFAISSStoreIndexMetadataCoherence(unittest.TestCase):
    """End-to-end: a corrupt-metadata reload must discard the FAISS index too.

    Reproduces the exact regression the reviewer reported: one persisted
    document, a corrupted metadata file, reload, and a new insert. Before the
    fix the loaded index stayed in memory with stale ntotal while metadata was
    empty, so the next insert produced an index with two vectors but a
    metadata map of {0: "new"} — and querying the old vector returned the new
    document. The store must now fail closed as one unit.
    """

    def setUp(self):
        import faiss
        import numpy as np
        self.faiss = faiss
        self.np = np
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = os.path.join(self.temp_dir, "index.faiss")
        self.metadata_path = os.path.join(self.temp_dir, "metadata.json")
        from agentuniverse.agent.action.knowledge.store.faiss_store import FAISSStore
        self.FAISSStore = FAISSStore

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _new_store(self) -> "FAISSStore":
        store = self.FAISSStore(
            index_path=self.index_path,
            metadata_path=self.metadata_path,
            embedding_model=None,
        )
        store._new_client()
        return store

    def _persist_one_document(self) -> None:
        store = self._new_store()
        store.insert_document([
            Document(id="old_doc", text="old text", embedding=[1.0, 0.0, 0.0]),
        ])
        self.assertEqual(store.faiss_index.ntotal, 1)

    def _corrupt_metadata_format_marker(self) -> None:
        with open(self.metadata_path, encoding="utf-8") as f:
            payload = json.load(f)
        payload["format"] = "some-other-format"
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(payload, f)

    def test_corrupt_metadata_discards_loaded_index(self) -> None:
        # Persist one document, corrupt the metadata format marker, reload.
        self._persist_one_document()
        # Sanity: the index file exists and holds one vector.
        self.assertEqual(self.faiss.read_index(self.index_path).ntotal, 1)
        self._corrupt_metadata_format_marker()

        store = self._new_store()
        # The loaded index must have been discarded — the store starts empty
        # and coherent, not index-only.
        self.assertIsNone(store.faiss_index)
        self.assertEqual(store.get_document_count(), 0)
        self.assertEqual(store.id_to_index, {})
        self.assertEqual(store.index_to_id, {})
        self.assertEqual(store._next_index, 0)

    def test_insert_after_corrupt_reload_does_not_orphan_vectors(self) -> None:
        # The end-to-end regression: corrupt reload + new insert must not
        # leave the index with a vector that maps to the wrong document.
        self._persist_one_document()
        self._corrupt_metadata_format_marker()

        store = self._new_store()
        store.insert_document([
            Document(id="new_doc", text="new text", embedding=[0.0, 1.0, 0.0]),
        ])

        # Exactly one vector now (the new one), and it maps to new_doc only.
        self.assertIsNotNone(store.faiss_index)
        self.assertEqual(store.faiss_index.ntotal, 1)
        self.assertEqual(set(store.index_to_id.values()), {"new_doc"})
        self.assertEqual(store.get_document_count(), 1)

        # Querying must never return a stale mapping: the only retrievable
        # document is new_doc.
        from agentuniverse.agent.action.knowledge.store.query import Query
        results = store.query(Query(embeddings=[[0.0, 1.0, 0.0]]))
        result_ids = [r.id for r in results]
        self.assertEqual(result_ids, ["new_doc"])
        self.assertNotIn("old_doc", result_ids)

    def test_generation_mismatch_between_index_and_metadata_discards_both(self) -> None:
        # Persist one document, then hand-write a metadata file that maps zero
        # vectors while the index still holds one — a generation mismatch.
        self._persist_one_document()
        # Overwrite metadata with an empty-but-valid payload (0 vectors).
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump({
                "format": "faiss-store-metadata-v1",
                "document_store": {},
                "id_to_index": {},
                "index_to_id": {},
                "next_index": 0,
            }, f)

        store = self._new_store()
        # The mismatch (index ntotal=1 vs metadata 0 vectors) must fail closed.
        self.assertIsNone(store.faiss_index)
        self.assertEqual(store.get_document_count(), 0)


if __name__ == "__main__":
    # Configure test logging
    logging.basicConfig(level=logging.WARNING)

    # Run tests with verbose output
    unittest.main(verbosity=2)
