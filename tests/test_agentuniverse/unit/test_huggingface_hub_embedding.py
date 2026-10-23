# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/25 10:00
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: test_huggingface_hub_embedding.py
import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.embedding.huggingface_hub_embedding import HuggingFaceHubEmbedding


class TestHuggingFaceHubEmbedding(unittest.TestCase):
    """Test cases for HuggingFaceHubEmbedding."""

    def setUp(self):
        self.embedding = HuggingFaceHubEmbedding()
        self.embedding.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.embedding.api_key = "test-api-key"

    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.embedding.embedding_model_name, "sentence-transformers/all-MiniLM-L6-v2")
        self.assertEqual(self.embedding.api_key, "test-api-key")

    @patch('huggingface_hub.InferenceClient')
    def test_get_embeddings(self, mock_client_class):
        """Test get_embeddings method."""
        import numpy as np
        mock_client = MagicMock()
        mock_embedding = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        mock_client.feature_extraction.return_value = mock_embedding
        mock_client_class.return_value = mock_client

        texts = ["Hello world", "Test text"]
        embeddings = self.embedding.get_embeddings(texts)

        self.assertEqual(len(embeddings), 2)
        self.assertEqual(len(embeddings[0]), 5)
        mock_client.feature_extraction.assert_called()

    def test_missing_api_key(self):
        """Test error when API key is missing."""
        self.embedding.api_key = None
        with self.assertRaises(ValueError):
            self.embedding.get_embeddings(["test"])


if __name__ == '__main__':
    unittest.main()
