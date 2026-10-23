"""Regression tests for FAISS index, metadata and embedding consistency."""

import os
import pickle
import shutil
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from agentuniverse.agent.action.knowledge.store import faiss_store as module
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


class FakeIndexFlat:
    """Minimal in-memory replacement for faiss.IndexFlatL2."""

    def __init__(self, dimension: int) -> None:
        self.d = dimension
        self.vectors = np.empty((0, dimension), dtype=np.float32)
        self.is_trained = True
        self.nprobe = None

    @property
    def ntotal(self) -> int:
        return int(self.vectors.shape[0])

    def add(self, values) -> None:
        values = np.asarray(values, dtype=np.float32)
        if values.ndim == 1:
            values = values.reshape(1, -1)
        self.vectors = np.vstack([self.vectors, values])

    def train(self, values) -> None:
        self.is_trained = True

    def search(self, query, k: int):
        query = np.asarray(query, dtype=np.float32)
        if query.ndim == 1:
            query = query.reshape(1, -1)
        distances = ((self.vectors[None, :, :] - query[:, None, :]) ** 2).sum(-1)
        order = np.argsort(distances, axis=1)[:, :k]
        return np.take_along_axis(distances, order, axis=1), order


class FakeFaiss:
    """The small part of the faiss API used by FAISSStore."""

    IndexFlatL2 = FakeIndexFlat
    IndexFlatIP = FakeIndexFlat

    @staticmethod
    def write_index(index, path: str) -> None:
        with open(path, "wb") as output:
            pickle.dump(index.vectors, output)

    @staticmethod
    def read_index(path: str) -> FakeIndexFlat:
        with open(path, "rb") as source:
            vectors = pickle.load(source)  # noqa: S301
        index = FakeIndexFlat(int(vectors.shape[1]))
        index.vectors = vectors
        return index


class FAISSIndexConsistencyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = os.path.join(self.temp_dir, "store.faiss")
        self.metadata_path = os.path.join(self.temp_dir, "store.pkl")
        self.original_faiss = module.faiss
        self.original_np = module.np
        module.faiss = FakeFaiss
        module.np = np

    def tearDown(self) -> None:
        module.faiss = self.original_faiss
        module.np = self.original_np
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def make_store(self, embedding_model=None):
        store = module.FAISSStore(
            index_path=self.index_path,
            metadata_path=self.metadata_path,
            embedding_model=embedding_model,
            similarity_top_k=3,
            index_config={"index_type": "IndexFlatL2", "dimension": 3},
        )
        store._new_client()
        return store

    @staticmethod
    def document(document_id: str, vector, text: str = "") -> Document:
        return Document(id=document_id, text=text or document_id, embedding=list(vector))

    def test_generated_embedding_is_written_back_to_the_document(self) -> None:
        store = self.make_store(embedding_model="test_embedding")
        with patch.object(module.FAISSStore, "_get_embedding", return_value=[1.0, 0.0, 0.0]):
            store.insert_document([Document(id="alpha", text="alpha")])

        stored = store.get_document_by_id("alpha")
        self.assertIsNotNone(stored)
        self.assertEqual(stored.embedding, [1.0, 0.0, 0.0])
        self.assertEqual(store.get_document_count(), 1)
        self.assertEqual(store.faiss_index.ntotal, 1)

    def test_delete_keeps_the_remaining_documents_searchable(self) -> None:
        store = self.make_store()
        store.insert_document(
            [
                self.document("a", [1.0, 0.0, 0.0]),
                self.document("b", [0.0, 1.0, 0.0]),
                self.document("c", [0.0, 0.0, 1.0]),
            ]
        )

        store.delete_document("b")

        self.assertEqual(store.get_document_count(), 2)
        self.assertIsNotNone(store.faiss_index)
        self.assertEqual(store.faiss_index.ntotal, 2)
        self.assertEqual(set(store.id_to_index.values()), {0, 1})
        found = {item.id for item in store.query(Query(embeddings=[[0.0, 1.0, 0.0]], similarity_top_k=3))}
        self.assertEqual(found, {"a", "c"})

    def test_deleting_the_last_document_removes_the_persisted_index(self) -> None:
        store = self.make_store()
        store.insert_document([self.document("only", [1.0, 0.0, 0.0])])

        store.delete_document("only")

        self.assertEqual(store.get_document_count(), 0)
        self.assertIsNone(store.faiss_index)
        self.assertFalse(os.path.exists(self.index_path))
        reloaded = self.make_store()
        self.assertEqual(reloaded.get_document_count(), 0)
        self.assertIsNone(reloaded.faiss_index)

    def test_upsert_replaces_the_vector_without_duplicating_the_document(self) -> None:
        store = self.make_store()
        store.insert_document([self.document("a", [1.0, 0.0, 0.0], text="old")])

        store.upsert_document([self.document("a", [0.0, 1.0, 0.0], text="new")])

        self.assertEqual(store.get_document_count(), 1)
        self.assertEqual(store.faiss_index.ntotal, 1)
        self.assertEqual(store.get_document_by_id("a").text, "new")
        found = store.query(Query(embeddings=[[0.0, 1.0, 0.0]], similarity_top_k=1))
        self.assertEqual([(item.id, item.text) for item in found], [("a", "new")])

    def test_reset_removes_vectors_and_catalog(self) -> None:
        store = self.make_store()
        store.insert_document(
            [
                self.document("a", [1.0, 0.0, 0.0]),
                self.document("b", [0.0, 1.0, 0.0]),
            ]
        )

        store._reset_faiss_index()

        self.assertEqual(store.get_document_count(), 0)
        self.assertIsNone(store.faiss_index)
        self.assertFalse(os.path.exists(self.index_path))
        reloaded = self.make_store()
        self.assertEqual(reloaded.get_document_count(), 0)

    def test_rebuild_drops_documents_that_can_no_longer_be_embedded(self) -> None:
        store = self.make_store()
        store.insert_document(
            [
                self.document("a", [1.0, 0.0, 0.0]),
                self.document("b", [0.0, 1.0, 0.0]),
            ]
        )
        # Simulate a document persisted by an older version that did not write
        # generated vectors back to the document.
        store.document_store["b"].embedding = []
        store._save_index_and_metadata()

        store.delete_document("a")

        self.assertEqual(store.get_document_count(), 0)
        self.assertIsNone(store.faiss_index)
        self.assertFalse(os.path.exists(self.index_path))
        self.assertEqual(store.id_to_index, {})
        self.assertEqual(store.index_to_id, {})


if __name__ == "__main__":
    unittest.main()
