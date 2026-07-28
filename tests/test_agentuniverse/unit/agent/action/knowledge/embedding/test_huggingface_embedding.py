#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for HuggingFaceEmbedding."""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.embedding.huggingface_embedding \
    import HuggingFaceEmbedding


class TestHuggingFaceEmbedding(unittest.TestCase):

    def test_get_embeddings_single_text(self):
        emb = HuggingFaceEmbedding(
            embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
            api_key="fake-key")
        mock_client = MagicMock()
        mock_client.feature_extraction.return_value = [0.1, 0.2, 0.3]
        emb._client = mock_client

        result = emb.get_embeddings(["hello world"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [0.1, 0.2, 0.3])

    def test_get_embeddings_multiple_texts(self):
        emb = HuggingFaceEmbedding(api_key="k")
        mock_client = MagicMock()
        mock_client.feature_extraction.side_effect = [
            [0.1, 0.2], [0.3, 0.4],
        ]
        emb._client = mock_client

        result = emb.get_embeddings(["text1", "text2"])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [0.1, 0.2])
        self.assertEqual(result[1], [0.3, 0.4])

    def test_get_embeddings_handles_nested_list(self):
        emb = HuggingFaceEmbedding(api_key="k")
        mock_client = MagicMock()
        # Model returns [[token1_emb]] — single sentence, token-level.
        mock_client.feature_extraction.return_value = [[0.1, 0.2], [0.3, 0.4]]
        emb._client = mock_client

        result = emb.get_embeddings(["test"])
        # Mean-pool: [(0.1+0.3)/2, (0.2+0.4)/2] = [0.2, 0.3]
        self.assertAlmostEqual(result[0][0], 0.2, places=5)
        self.assertAlmostEqual(result[0][1], 0.3, places=5)

    def test_empty_input_returns_empty(self):
        emb = HuggingFaceEmbedding(api_key="k")
        result = emb.get_embeddings([])
        self.assertEqual(result, [])

    def test_missing_model_name_raises(self):
        emb = HuggingFaceEmbedding(api_key="k")
        emb.embedding_model_name = None
        with self.assertRaises(ValueError):
            emb.get_embeddings(["text"])

    def test_api_error_returns_empty_vector(self):
        emb = HuggingFaceEmbedding(api_key="k")
        mock_client = MagicMock()
        mock_client.feature_extraction.side_effect = RuntimeError("API down")
        emb._client = mock_client

        result = emb.get_embeddings(["text"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [])

    def test_env_var_defaults(self):
        with patch.dict("os.environ", {"HUGGINGFACE_API_KEY": "env-key"}):
            emb = HuggingFaceEmbedding()
            self.assertEqual(emb.api_key, "env-key")

    def test_hf_token_fallback(self):
        with patch.dict("os.environ", {"HF_TOKEN": "token-val"}, clear=True):
            emb = HuggingFaceEmbedding()
            self.assertEqual(emb.api_key, "token-val")

    def test_mean_pool(self):
        result = HuggingFaceEmbedding._mean_pool([[1.0, 2.0], [3.0, 4.0]])
        self.assertEqual(result, [2.0, 3.0])

    def test_mean_pool_empty(self):
        self.assertEqual(HuggingFaceEmbedding._mean_pool([]), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
