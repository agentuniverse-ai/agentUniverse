# ruff: noqa: TRY003
"""Deterministic FAISSStore validation tests without the optional FAISS package."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import numpy as numpy

import agentuniverse.agent.action.knowledge.store.faiss_store as faiss_module
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.faiss_store import FAISSStore
from agentuniverse.agent.action.knowledge.store.query import Query


class _FakeIndex:
    """Minimal in-memory index for validation and query-boundary tests."""

    def __init__(self, dimension: int) -> None:
        self.d = dimension
        self.ntotal = 0
        self.is_trained = True
        self.nprobe = None
        self.hnsw = SimpleNamespace(efConstruction=None, efSearch=None)
        self.last_search_k: int | None = None

    def add(self, vectors: Any) -> None:
        if vectors.ndim != 2 or vectors.shape[1] != self.d:
            raise AssertionError("invalid vectors reached the fake FAISS backend")
        self.ntotal += len(vectors)

    def search(self, vectors: Any, k: int):
        if vectors.ndim != 2 or vectors.shape[1] != self.d:
            raise AssertionError("invalid query reached the fake FAISS backend")
        self.last_search_k = k
        distances = numpy.zeros((len(vectors), k), dtype=numpy.float32)
        indices = numpy.tile(numpy.arange(k, dtype=numpy.int64), (len(vectors), 1))
        return distances, indices


class _FakeFaiss:
    """Construct the supported index shapes without importing native FAISS."""

    @staticmethod
    def IndexFlatL2(dimension: int) -> _FakeIndex:
        return _FakeIndex(dimension)

    @staticmethod
    def IndexFlatIP(dimension: int) -> _FakeIndex:
        return _FakeIndex(dimension)

    @staticmethod
    def IndexIVFFlat(quantizer: _FakeIndex, dimension: int, nlist: int) -> _FakeIndex:
        return _FakeIndex(dimension)

    @staticmethod
    def IndexIVFPQ(
        quantizer: _FakeIndex,
        dimension: int,
        nlist: int,
        m: int,
        nbits: int,
    ) -> _FakeIndex:
        return _FakeIndex(dimension)

    @staticmethod
    def IndexHNSWFlat(dimension: int, m: int) -> _FakeIndex:
        return _FakeIndex(dimension)


class TestFAISSStoreValidation(unittest.TestCase):
    """Invalid input fails before native index or metadata mutation."""

    def setUp(self) -> None:
        self.original_faiss = faiss_module.faiss
        self.original_numpy = faiss_module.np
        faiss_module.faiss = _FakeFaiss()
        faiss_module.np = numpy

    def tearDown(self) -> None:
        faiss_module.faiss = self.original_faiss
        faiss_module.np = self.original_numpy

    @staticmethod
    def store(**overrides: Any) -> FAISSStore:
        values = {
            "index_path": None,
            "metadata_path": None,
            "embedding_model": None,
            "similarity_top_k": 5,
            "index_config": {"index_type": "IndexFlatL2", "dimension": 4},
        }
        values.update(overrides)
        return FAISSStore(**values)

    @staticmethod
    def document(document_id: str, embedding: Any) -> Document:
        document = Document(id=document_id, text=f"document {document_id}", embedding=[0.0])
        document.embedding = embedding
        return document

    def assert_pristine(self, store: FAISSStore) -> None:
        self.assertIsNone(store.faiss_index)
        self.assertEqual(store.document_store, {})
        self.assertEqual(store.id_to_index, {})
        self.assertEqual(store.index_to_id, {})
        self.assertEqual(store._next_index, 0)

    def test_rejects_invalid_common_configuration(self) -> None:
        cases = [
            ({"index_type": "Unknown", "dimension": 4}, "Unsupported index type"),
            ({"index_type": "IndexFlatL2", "dimension": 0}, "dimension"),
            ({"index_type": "IndexFlatL2", "dimension": -1}, "dimension"),
            ({"index_type": "IndexFlatL2", "dimension": True}, "dimension"),
            ({"index_type": "IndexFlatL2", "dimension": 4.0}, "dimension"),
        ]
        for config, message in cases:
            with self.subTest(config=config), self.assertRaisesRegex(ValueError, message):
                self.store(index_config=config)._validate_config()

        store = self.store()
        store.index_config = []
        with self.assertRaisesRegex(TypeError, "index_config"):
            store._validate_config()

        store.index_config = {"index_type": []}
        with self.assertRaisesRegex(TypeError, "index_type must be a string"):
            store._validate_config()

    def test_component_configuration_rejects_non_object_index_config(self) -> None:
        configer = SimpleNamespace(name=None, description=None, index_config=[])
        with (
            patch("agentuniverse.agent.action.knowledge.store.store.add_post_fork") as add_post_fork,
            self.assertRaisesRegex(TypeError, "index_config must be an object"),
        ):
            self.store()._initialize_by_component_configer(configer)
        add_post_fork.assert_not_called()

    def test_default_and_component_configuration_infer_first_batch_dimension(self) -> None:
        default_store = FAISSStore(index_path=None, metadata_path=None, similarity_top_k=5)
        default_store.insert_document([self.document("default", [0.1, 0.2, 0.3, 0.4])])
        self.assertEqual(default_store.faiss_index.d, 4)

        configured_store = FAISSStore(index_path=None, metadata_path=None, similarity_top_k=5)
        configer = SimpleNamespace(
            name=None,
            description=None,
            index_config={"index_type": "IndexFlatL2"},
        )
        with patch("agentuniverse.agent.action.knowledge.store.store.add_post_fork"):
            configured_store._initialize_by_component_configer(configer)
        configured_store.insert_document([self.document("configured", [0.1, 0.2, 0.3, 0.4])])
        self.assertEqual(configured_store.faiss_index.d, 4)

    def test_component_configuration_preserves_existing_partial_index_settings(self) -> None:
        store = self.store(
            index_config={
                "index_type": "IndexHNSWFlat",
                "dimension": 8,
                "M": 64,
            }
        )
        configer = SimpleNamespace(
            name=None,
            description=None,
            index_config={"efSearch": 20},
        )
        with patch("agentuniverse.agent.action.knowledge.store.store.add_post_fork"):
            store._initialize_by_component_configer(configer)
        self.assertEqual(
            store.index_config,
            {
                "index_type": "IndexHNSWFlat",
                "dimension": 8,
                "M": 64,
                "efSearch": 20,
            },
        )

    def test_rejects_invalid_index_specific_configuration(self) -> None:
        cases = [
            ({"index_type": "IndexIVFFlat", "dimension": 4, "nlist": 0}, "nlist"),
            ({"index_type": "IndexIVFFlat", "dimension": 4, "nprobe": False}, "nprobe"),
            ({"index_type": "IndexIVFPQ", "dimension": 4, "m": 0}, "index_config.m"),
            ({"index_type": "IndexIVFPQ", "dimension": 4, "m": 2, "nbits": 0}, "nbits"),
            ({"index_type": "IndexIVFPQ", "dimension": 4, "m": 2, "nbits": 25}, "nbits"),
            ({"index_type": "IndexIVFPQ", "dimension": 5, "m": 2}, "divisible"),
            ({"index_type": "IndexHNSWFlat", "dimension": 4, "M": 0}, "index_config.M"),
            ({"index_type": "IndexHNSWFlat", "dimension": 4, "efConstruction": -1}, "efConstruction"),
            ({"index_type": "IndexHNSWFlat", "dimension": 4, "efSearch": 1.5}, "efSearch"),
        ]
        for config, message in cases:
            with self.subTest(config=config), self.assertRaisesRegex(ValueError, message):
                self.store(index_config=config)._validate_config()

    def test_supported_index_configurations_remain_valid(self) -> None:
        configs = [
            {"index_type": "IndexFlatL2", "dimension": 4},
            {"index_type": "IndexFlatIP", "dimension": 4},
            {"index_type": "IndexIVFFlat", "dimension": 4, "nlist": 4, "nprobe": 8},
            {"index_type": "IndexIVFPQ", "dimension": 4, "nlist": 4, "m": 2, "nbits": 8},
            {"index_type": "IndexHNSWFlat", "dimension": 4, "M": 8, "efConstruction": 40, "efSearch": 20},
        ]
        for config in configs:
            with self.subTest(index_type=config["index_type"]):
                store = self.store(index_config=config)
                store._validate_config()
                self.assertEqual(store._create_faiss_index(4).d, 4)

    def test_first_batch_must_match_configured_dimension(self) -> None:
        store = self.store()
        with self.assertRaisesRegex(ValueError, "dimension 2 does not match expected dimension 4"):
            store.insert_document([self.document("wrong-dimension", [0.1, 0.2])])
        self.assert_pristine(store)

    def test_batch_dimensions_are_validated_before_index_creation(self) -> None:
        store = self.store(index_config={"index_type": "IndexFlatL2"})
        documents = [
            self.document("valid", [0.1, 0.2, 0.3, 0.4]),
            self.document("different", [0.1, 0.2, 0.3]),
        ]
        with self.assertRaisesRegex(ValueError, "dimension 3 does not match expected dimension 4"):
            store.insert_document(documents)
        self.assert_pristine(store)

    def test_non_finite_non_numeric_and_float32_overflow_fail_before_index_creation(self) -> None:
        invalid_values = [float("nan"), float("inf"), -float("inf"), 1e39, True, "0.2"]
        for invalid in invalid_values:
            with self.subTest(invalid=invalid):
                store = self.store()
                documents = [
                    self.document("valid", [0.1, 0.2, 0.3, 0.4]),
                    self.document("invalid", [0.1, invalid, 0.3, 0.4]),
                ]
                with self.assertRaisesRegex(ValueError, "finite"):
                    store.insert_document(documents)
                self.assert_pristine(store)

    def test_duplicate_document_ids_reject_the_entire_batch(self) -> None:
        store = self.store()
        documents = [
            self.document("duplicate", [0.1, 0.2, 0.3, 0.4]),
            self.document("duplicate", [0.5, 0.6, 0.7, 0.8]),
        ]
        with self.assertRaisesRegex(ValueError, "duplicate IDs"):
            store.insert_document(documents)
        self.assert_pristine(store)

    def test_invalid_upsert_preserves_existing_state(self) -> None:
        store = self.store()
        store.insert_document([self.document("existing", [0.1, 0.2, 0.3, 0.4])])
        original_index = store.faiss_index
        original_document = store.document_store["existing"]
        original_mappings = (store.id_to_index.copy(), store.index_to_id.copy(), store._next_index)

        with self.assertRaisesRegex(ValueError, "dimension 2 does not match expected dimension 4"):
            store.upsert_document([self.document("existing", [0.1, 0.2])])

        self.assertIs(store.faiss_index, original_index)
        self.assertIs(store.document_store["existing"], original_document)
        self.assertEqual(
            (store.id_to_index, store.index_to_id, store._next_index),
            original_mappings,
        )

    def test_generator_batch_is_materialized_once(self) -> None:
        store = self.store()
        documents = (
            self.document(document_id, embedding)
            for document_id, embedding in (
                ("one", [0.1, 0.2, 0.3, 0.4]),
                ("two", [0.5, 0.6, 0.7, 0.8]),
            )
        )
        store.insert_document(documents)
        self.assertEqual(store.get_document_count(), 2)

    def test_top_k_is_validated_even_for_an_empty_index(self) -> None:
        invalid_values = [0, -1, True, 1.5]
        for invalid in invalid_values:
            with self.subTest(invalid=invalid):
                store = self.store()
                query = Query()
                query.similarity_top_k = invalid
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    store.query(query)

        store = self.store()
        store.similarity_top_k = 0
        with self.assertRaisesRegex(ValueError, "positive integer"):
            store.query(Query())

    def test_invalid_query_vectors_fail_before_search(self) -> None:
        invalid_vectors = [
            [[0.1, 0.2]],
            [[0.1, float("nan"), 0.3, 0.4]],
            [[0.1, float("inf"), 0.3, 0.4]],
            [[0.1, 1e39, 0.3, 0.4]],
        ]
        for embeddings in invalid_vectors:
            with self.subTest(embeddings=embeddings):
                store = self.store()
                store.faiss_index = _FakeIndex(4)
                store.faiss_index.ntotal = 1
                with self.assertRaises(ValueError):
                    store.query(Query(embeddings=embeddings))
                self.assertIsNone(store.faiss_index.last_search_k)

    def test_invalid_query_shape_is_rejected_even_when_index_is_empty(self) -> None:
        store = self.store()
        with self.assertRaisesRegex(ValueError, "exactly one"):
            store.query(Query(embeddings=[[0.1] * 4, [0.2] * 4]))
        with self.assertRaisesRegex(ValueError, "non-empty"):
            store.query(Query(embeddings=[[]]))
        self.assert_pristine(store)

    def test_query_accepts_exactly_one_embedding(self) -> None:
        store = self.store()
        store.faiss_index = _FakeIndex(4)
        store.faiss_index.ntotal = 1
        query = Query(embeddings=[[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]])
        with self.assertRaisesRegex(ValueError, "exactly one"):
            store.query(query)
        self.assertIsNone(store.faiss_index.last_search_k)

    def test_loaded_index_dimension_must_match_configuration(self) -> None:
        store = self.store()
        store.faiss_index = _FakeIndex(3)
        store.faiss_index.ntotal = 1
        with self.assertRaisesRegex(ValueError, "index dimension 3"):
            store.query(Query(embeddings=[[0.1, 0.2, 0.3]]))
        self.assertIsNone(store.faiss_index.last_search_k)

    def test_valid_query_truncates_top_k_to_index_size(self) -> None:
        store = self.store()
        store.insert_document(
            [
                self.document("one", [0.1, 0.2, 0.3, 0.4]),
                self.document("two", [0.5, 0.6, 0.7, 0.8]),
            ]
        )
        results = store.query(Query(embeddings=[[0.1, 0.2, 0.3, 0.4]], similarity_top_k=100))
        self.assertEqual(len(results), 2)
        self.assertEqual(store.faiss_index.last_search_k, 2)

    def test_query_override_works_without_a_store_default_top_k(self) -> None:
        store = self.store(similarity_top_k=None)
        store.insert_document([self.document("one", [0.1, 0.2, 0.3, 0.4])])
        self.assertEqual(
            len(store.query(Query(embeddings=[[0.1, 0.2, 0.3, 0.4]], similarity_top_k=1))),
            1,
        )
        with self.assertRaisesRegex(ValueError, "positive integer"):
            store.query(Query(embeddings=[[0.1, 0.2, 0.3, 0.4]]))


if __name__ == "__main__":
    unittest.main()
