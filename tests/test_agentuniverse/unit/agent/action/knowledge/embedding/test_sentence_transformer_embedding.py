#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for SentenceTransformerEmbedding."""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.embedding.sentence_transformer_embedding \
    import SentenceTransformerEmbedding


class TestSentenceTransformerEmbedding(unittest.TestCase):

    def test_get_embeddings_single(self):
        emb = SentenceTransformerEmbedding()
        mock_model = MagicMock()
        mock_model.encode.return_value = MagicMock(
            tolist=lambda: [[0.1, 0.2, 0.3]])
        emb._model = mock_model

        result = emb.get_embeddings(["hello"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [0.1, 0.2, 0.3])

    def test_get_embeddings_multiple(self):
        emb = SentenceTransformerEmbedding()
        mock_model = MagicMock()
        mock_model.encode.return_value = MagicMock(
            tolist=lambda: [[0.1], [0.2], [0.3]])
        emb._model = mock_model

        result = emb.get_embeddings(["a", "b", "c"])
        self.assertEqual(len(result), 3)

    def test_empty_input(self):
        emb = SentenceTransformerEmbedding()
        self.assertEqual(emb.get_embeddings([]), [])

    def test_error_returns_empty_vectors(self):
        emb = SentenceTransformerEmbedding()
        mock_model = MagicMock()
        mock_model.encode.side_effect = RuntimeError("model crashed")
        emb._model = mock_model

        result = emb.get_embeddings(["text"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [])

    def test_normalize_embeddings_passed_to_model(self):
        emb = SentenceTransformerEmbedding(normalize_embeddings=True)
        mock_model = MagicMock()
        mock_model.encode.return_value = MagicMock(
            tolist=lambda: [[0.1]])
        emb._model = mock_model

        emb.get_embeddings(["text"])
        call_kwargs = mock_model.encode.call_args.kwargs
        self.assertTrue(call_kwargs["normalize_embeddings"])

    def test_batch_size_passed(self):
        emb = SentenceTransformerEmbedding(batch_size=64)
        mock_model = MagicMock()
        mock_model.encode.return_value = MagicMock(
            tolist=lambda: [[0.1]])
        emb._model = mock_model

        emb.get_embeddings(["text"])
        call_kwargs = mock_model.encode.call_args.kwargs
        self.assertEqual(call_kwargs["batch_size"], 64)

    def test_default_model_name(self):
        emb = SentenceTransformerEmbedding()
        self.assertEqual(emb.embedding_model_name, "all-MiniLM-L6-v2")

    def test_default_device_cpu(self):
        emb = SentenceTransformerEmbedding()
        self.assertEqual(emb.device, "cpu")

    def test_model_lazy_load(self):
        """Model should not be loaded until get_embeddings is called."""
        emb = SentenceTransformerEmbedding()
        self.assertIsNone(emb._model)

    def test_numpy_array_without_tolist(self):
        """If encode returns a plain list, it should still work."""
        emb = SentenceTransformerEmbedding()
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.1, 0.2], [0.3, 0.4]]
        emb._model = mock_model

        result = emb.get_embeddings(["a", "b"])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [0.1, 0.2])


if __name__ == "__main__":
    unittest.main(verbosity=2)
