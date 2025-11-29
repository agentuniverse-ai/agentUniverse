#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-11-29
# @Author  : guangxu
# @Email   : guangxu.sgx@antgroup.com
# @FileName: test_huggingface_embedding.py

import asyncio
import unittest
from unittest.mock import patch, MagicMock

from agentuniverse.agent.action.knowledge.embedding.huggingface_embedding import HuggingFaceEmbedding


class EmbeddingTest(unittest.TestCase):
    """
    Test cases for HuggingFaceEmbedding class
    """

    def setUp(self) -> None:        
        self.embedding = HuggingFaceEmbedding()
        # Use a lightweight model as default
        self.embedding.model_name = "sentence-transformers/all-MiniLM-L6-v2"

    @patch('agentuniverse.agent.action.knowledge.embedding.huggingface_embedding.HuggingFaceEmbeddings')
    def test_get_embeddings(self, mock_hf_embeddings_class) -> None:
        # Mock the HuggingFaceEmbeddings instance
        mock_embeddings_instance = MagicMock()
        mock_embeddings_instance.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        mock_hf_embeddings_class.return_value = mock_embeddings_instance
        
        # Test the embeddings functionality
        res = self.embedding.get_embeddings(texts=["hello world"])
        print(f"test_get_embeddings result: {res}")
        
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertGreater(len(res[0]), 0)  # embeddings should not be empty
        # Verify that the mock was called correctly
        mock_hf_embeddings_class.assert_called_once()
        mock_embeddings_instance.embed_documents.assert_called_once_with(["hello world"])

    @patch('agentuniverse.agent.action.knowledge.embedding.huggingface_embedding.HuggingFaceEmbeddings')
    def test_async_get_embeddings(self, mock_hf_embeddings_class) -> None:
        # Mock the HuggingFaceEmbeddings instance
        mock_embeddings_instance = MagicMock()
        mock_embeddings_instance.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        mock_hf_embeddings_class.return_value = mock_embeddings_instance
        
        # Test async method
        res = asyncio.run(
            self.embedding.async_get_embeddings(texts=["hello world"]))
        print(f"test_async_get_embeddings result: {res}")
        
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertGreater(len(res[0]), 0)  # embeddings should not be empty

    @patch('agentuniverse.agent.action.knowledge.embedding.huggingface_embedding.HuggingFaceEmbeddings')
    def test_multiple_texts(self, mock_hf_embeddings_class) -> None:
        # Mock the HuggingFaceEmbeddings instance
        mock_embeddings_instance = MagicMock()
        mock_embeddings_instance.embed_documents.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
        mock_hf_embeddings_class.return_value = mock_embeddings_instance
        
        texts = ["hello", "world", "huggingface embedding test"]
        res = self.embedding.get_embeddings(texts=texts)
        print(f"test_multiple_texts result: {res}")
        
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 3)  # Should have one embedding for each text
        for embedding in res:
            self.assertGreater(len(embedding), 0)  # All embeddings should not be empty
        # Ensure embed_documents was called with the right parameter
        mock_embeddings_instance.embed_documents.assert_called_once_with(texts)

    def test_initialization(self):
        """Test basic initialization of HuggingFaceEmbedding class."""
        self.assertIsInstance(self.embedding, HuggingFaceEmbedding)
        self.assertEqual(self.embedding.model_name, "sentence-transformers/all-MiniLM-L6-v2")


if __name__ == '__main__':
    unittest.main()