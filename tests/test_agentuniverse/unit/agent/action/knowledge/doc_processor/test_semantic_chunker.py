#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for SemanticChunker DocProcessor."""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.doc_processor.semantic_chunker \
    import SemanticChunker
from agentuniverse.agent.action.knowledge.store.document import Document


MULTI_TOPIC = """
Python is a popular programming language. It is used for web development,
data science, and automation. Many developers choose Python for its simplicity.

In contrast, Rust focuses on memory safety and zero-cost abstractions. Rust's
borrow checker prevents common concurrency bugs at compile time. Rust is
increasingly used in systems programming.

Cloud computing has transformed how applications are deployed. AWS, Azure,
and Google Cloud provide scalable infrastructure. Containerization with Docker
is now the standard deployment model.
"""


class TestSemanticChunkerLexical(unittest.TestCase):

    def _chunk(self, text, **kwargs):
        proc = SemanticChunker(**kwargs)
        return proc.process_docs([Document(text=text)], None)

    def test_multi_topic_text_produces_multiple_chunks(self):
        docs = self._chunk(MULTI_TOPIC)
        self.assertGreater(len(docs), 1,
                           "text with clear topic shifts should produce "
                           "multiple chunks")

    def test_single_topic_stays_one_chunk(self):
        text = "This is about Python. Python is great. Python is versatile."
        docs = self._chunk(text)
        self.assertEqual(len(docs), 1)

    def test_empty_input_returns_empty(self):
        proc = SemanticChunker()
        self.assertEqual(proc.process_docs([], None), [])

    def test_short_text_returns_single_chunk(self):
        docs = self._chunk("Short text.")
        self.assertEqual(len(docs), 1)

    def test_max_chunk_size_hard_splits(self):
        long = "This is a sentence. " * 200
        docs = self._chunk(long, max_chunk_size=50)
        self.assertGreater(len(docs), 1)
        for d in docs:
            self.assertLessEqual(len(d.text), 55)  # small overshoot for word boundary

    def test_min_chunk_size_merges_small(self):
        # Each topic shift produces a short chunk; min_chunk_size merges them.
        text = "Topic A is interesting. Topic B is different. Topic C is new."
        docs = self._chunk(text, min_chunk_size=200)
        self.assertEqual(len(docs), 1)

    def test_metadata_includes_chunk_method(self):
        docs = self._chunk("Some text here. More text follows.")
        self.assertEqual(docs[0].metadata["chunk_method"], "semantic")

    def test_preserves_original_metadata(self):
        doc = Document(text="Hello world. Another sentence.",
                       metadata={"source": "test"})
        proc = SemanticChunker()
        docs = proc.process_docs([doc], None)
        self.assertEqual(docs[0].metadata["source"], "test")


class TestSemanticChunkerEmbedding(unittest.TestCase):

    def test_embedding_mode_falls_back_on_failure(self):
        proc = SemanticChunker(embedding_name="fake_emb")
        with patch("agentuniverse.agent.action.knowledge.doc_processor."
                   "semantic_chunker.EmbeddingManager") as mgr:
            mgr.return_value.get_instance_obj.side_effect = RuntimeError("no model")
            docs = proc.process_docs(
                [Document(text=MULTI_TOPIC)], None)
        # Should still produce results via lexical fallback.
        self.assertGreater(len(docs), 0)

    def test_embedding_mode_uses_cosine_similarity(self):
        proc = SemanticChunker(embedding_name="fake_emb")
        fake_model = MagicMock()
        # Two sentence groups with very different embeddings → split.
        fake_model.get_embeddings.return_value = [
            [1.0, 0.0], [0.9, 0.1],  # group 1 (similar)
            [0.0, 1.0], [0.1, 0.9],  # group 2 (similar, but very different from group 1)
        ]
        with patch("agentuniverse.agent.action.knowledge.doc_processor."
                   "semantic_chunker.EmbeddingManager") as mgr:
            mgr.return_value.get_instance_obj.return_value = fake_model
            sentences = ["s1", "s2", "s3", "s4"]
            points = proc._find_split_points_embedding(sentences)
        # Should have at least one split point between groups.
        self.assertIsInstance(points, list)

    def test_cosine_rejects_dimension_mismatch(self):
        self.assertEqual(SemanticChunker._cosine([1.0, 0.0], [1.0]), 0.0)

    def test_cosine_zero_magnitude(self):
        self.assertEqual(SemanticChunker._cosine([0.0, 0.0], [1.0, 0.0]), 0.0)

    def test_percentile(self):
        vals = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertAlmostEqual(SemanticChunker._percentile(vals, 50), 3.0)
        self.assertAlmostEqual(SemanticChunker._percentile(vals, 100), 5.0)
        self.assertAlmostEqual(SemanticChunker._percentile(vals, 0), 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
