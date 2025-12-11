# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/10 14:35
# @Author  : kaichuan
# @FileName: test_aws_bedrock_embedding.py

import asyncio
import unittest
from agentuniverse.agent.action.knowledge.embedding.aws_bedrock_embedding import AWSBedrockEmbedding


class EmbeddingTest(unittest.TestCase):
    """
    Test cases for AWS Bedrock Embedding class

    Note: These tests require valid AWS credentials and access to AWS Bedrock.
    Set the following environment variables before running:
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - AWS_REGION (optional, defaults to us-east-1)

    Or configure them directly in setUp() method.
    """

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.embedding = AWSBedrockEmbedding()
        # Configure with your AWS credentials
        # Option 1: Use environment variables (recommended)
        # Option 2: Set directly (for testing only, not for production)
        # self.embedding.aws_access_key_id = "your_access_key"
        # self.embedding.aws_secret_access_key = "your_secret_key"
        self.embedding.aws_region = "us-east-1"
        self.embedding.embedding_model_name = "amazon.titan-embed-text-v1"

    def test_get_embeddings_titan_v1(self) -> None:
        """Test synchronous embedding generation with Titan v1."""
        self.embedding.embedding_model_name = "amazon.titan-embed-text-v1"
        res = self.embedding.get_embeddings(texts=["hello world"])
        print(f"Titan v1 embedding result shape: {len(res)}x{len(res[0])}")
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1536)  # Titan v1 has 1536 dimensions

    def test_get_embeddings_titan_v2(self) -> None:
        """Test synchronous embedding generation with Titan v2 (configurable dimensions)."""
        self.embedding.embedding_model_name = "amazon.titan-embed-text-v2"
        self.embedding.dimensions = 1024
        res = self.embedding.get_embeddings(texts=["hello world"])
        print(f"Titan v2 embedding result shape: {len(res)}x{len(res[0])}")
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1024)  # Configured dimension

    def test_get_embeddings_cohere(self) -> None:
        """Test synchronous embedding generation with Cohere."""
        self.embedding.embedding_model_name = "cohere.embed-english-v3"
        res = self.embedding.get_embeddings(texts=["hello world"])
        print(f"Cohere embedding result shape: {len(res)}x{len(res[0])}")
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1024)  # Cohere has 1024 dimensions

    def test_get_embeddings_multiple_texts(self) -> None:
        """Test embedding generation with multiple texts."""
        texts = ["hello world", "artificial intelligence", "machine learning"]
        res = self.embedding.get_embeddings(texts=texts)
        print(f"Multiple texts embedding result: {len(res)} embeddings")
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 3)
        for embedding in res:
            self.assertEqual(len(embedding), 1536)  # Titan v1 default

    def test_async_get_embeddings(self) -> None:
        """Test asynchronous embedding generation."""
        res = asyncio.run(
            self.embedding.async_get_embeddings(texts=["hello world"]))
        print(f"Async embedding result shape: {len(res)}x{len(res[0])}")
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1536)

    def test_as_langchain(self) -> None:
        """Test LangChain conversion."""
        langchain_embedding = self.embedding.as_langchain()
        res = langchain_embedding.embed_documents(texts=["hello world"])
        print(f"LangChain embedding result shape: {len(res)}x{len(res[0])}")
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertIsInstance(res[0], list)
        self.assertEqual(len(res[0]), 1536)

    def test_normalize_option(self) -> None:
        """Test normalization option for Titan models."""
        # Test with normalization (default)
        self.embedding.normalize = True
        res_normalized = self.embedding.get_embeddings(texts=["hello world"])

        # Test without normalization
        self.embedding.normalize = False
        res_unnormalized = self.embedding.get_embeddings(texts=["hello world"])

        # Both should return embeddings, but values may differ
        self.assertEqual(len(res_normalized[0]), len(res_unnormalized[0]))
        print("Normalization test passed")

    def test_error_handling_missing_model(self) -> None:
        """Test error handling when model_id is not set."""
        self.embedding.embedding_model_name = None
        self.embedding.model_id = None
        with self.assertRaises(ValueError) as context:
            self.embedding.get_embeddings(texts=["test"])
        self.assertIn("embedding_model_name", str(context.exception))

    def test_error_handling_unsupported_model(self) -> None:
        """Test error handling for unsupported models."""
        self.embedding.embedding_model_name = "unsupported.model"
        with self.assertRaises(ValueError) as context:
            self.embedding.get_embeddings(texts=["test"])
        self.assertIn("Unsupported model", str(context.exception))


if __name__ == '__main__':
    unittest.main()
