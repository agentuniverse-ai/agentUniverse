#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/11 16:00
# @Author  : kaichuan
# @FileName: test_aws_bedrock_embedding_with_mock.py

"""
Test cases for AWS Bedrock Embedding class with mock support.

This test file includes both:
1. Mock tests that run without AWS credentials
2. Real API tests that require AWS credentials (skipped if not available)
"""

import json
import unittest
from unittest.mock import Mock, patch
import asyncio

from agentuniverse.agent.action.knowledge.embedding.aws_bedrock_embedding import AWSBedrockEmbedding


def create_mock_response(model_id, dimensions=None):
    """Helper function to create mock Bedrock API response."""
    if 'titan' in model_id.lower():
        if dimensions:
            mock_embedding = [0.1] * dimensions
        else:
            mock_embedding = [0.1] * 1536  # Titan v1 default
        response_body = {'embedding': mock_embedding}
    elif 'cohere' in model_id.lower():
        mock_embedding = [0.2] * 1024
        response_body = {'embeddings': [mock_embedding]}
    else:
        raise ValueError(f"Unsupported model: {model_id}")

    # Create mock response with read() method
    mock_body = Mock()
    mock_body.read = Mock(return_value=json.dumps(response_body).encode('utf-8'))

    return {
        'body': mock_body,
        'contentType': 'application/json',
        'ResponseMetadata': {
            'RequestId': 'mock-request-id',
            'HTTPStatusCode': 200
        }
    }


class EmbeddingTestWithMock(unittest.TestCase):
    """Test cases for AWS Bedrock Embedding class with mock support."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.embedding = AWSBedrockEmbedding()
        self.embedding.aws_region = 'us-east-1'
        self.embedding.embedding_model_name = 'amazon.titan-embed-text-v1'

    # ========== Mock Tests (No AWS credentials required) ==========

    @patch('boto3.Session')
    def test_get_embeddings_titan_v1_mock(self, mock_session_class) -> None:
        """Test Titan v1 embeddings with mock."""
        # Setup mock
        mock_client = Mock()
        mock_client.invoke_model = Mock(
            return_value=create_mock_response('amazon.titan-embed-text-v1'))

        mock_session = Mock()
        mock_session.client = Mock(return_value=mock_client)
        mock_session_class.return_value = mock_session

        # Test
        res = self.embedding.get_embeddings(texts=["hello world"])

        # Assertions
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1536)  # Titan v1 dimensions
        self.assertAlmostEqual(res[0][0], 0.1)
        print("✓ test_get_embeddings_titan_v1_mock passed")

    @patch('boto3.Session')
    def test_get_embeddings_titan_v2_mock(self, mock_session_class) -> None:
        """Test Titan v2 with custom dimensions using mock."""
        # Setup
        self.embedding.embedding_model_name = "amazon.titan-embed-text-v2"
        self.embedding.dimensions = 1024

        mock_client = Mock()
        mock_client.invoke_model = Mock(
            return_value=create_mock_response('amazon.titan-embed-text-v2', 1024))

        mock_session = Mock()
        mock_session.client = Mock(return_value=mock_client)
        mock_session_class.return_value = mock_session

        # Test
        res = self.embedding.get_embeddings(texts=["hello world"])

        # Assertions
        self.assertEqual(len(res[0]), 1024)  # Custom dimensions
        print("✓ test_get_embeddings_titan_v2_mock passed")

    @patch('boto3.Session')
    def test_get_embeddings_cohere_mock(self, mock_session_class) -> None:
        """Test Cohere embeddings with mock."""
        # Setup
        self.embedding.embedding_model_name = "cohere.embed-multilingual-v3"

        mock_client = Mock()
        mock_client.invoke_model = Mock(
            return_value=create_mock_response('cohere.embed-multilingual-v3'))

        mock_session = Mock()
        mock_session.client = Mock(return_value=mock_client)
        mock_session_class.return_value = mock_session

        # Test
        res = self.embedding.get_embeddings(texts=["hello world"])

        # Assertions
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1024)  # Cohere dimensions
        self.assertAlmostEqual(res[0][0], 0.2)
        print("✓ test_get_embeddings_cohere_mock passed")

    @patch('boto3.Session')
    def test_get_embeddings_multiple_texts_mock(self, mock_session_class) -> None:
        """Test multiple texts with mock."""
        # Setup
        mock_client = Mock()
        mock_client.invoke_model = Mock(
            return_value=create_mock_response('amazon.titan-embed-text-v1'))

        mock_session = Mock()
        mock_session.client = Mock(return_value=mock_client)
        mock_session_class.return_value = mock_session

        # Test
        texts = ["text 1", "text 2", "text 3"]
        res = self.embedding.get_embeddings(texts=texts)

        # Assertions
        self.assertEqual(len(res), 3)
        for embedding in res:
            self.assertEqual(len(embedding), 1536)
        print("✓ test_get_embeddings_multiple_texts_mock passed")

    @patch('boto3.Session')
    def test_async_get_embeddings_mock(self, mock_session_class) -> None:
        """Test async embeddings with mock."""
        # Setup
        mock_client = Mock()
        mock_client.invoke_model = Mock(
            return_value=create_mock_response('amazon.titan-embed-text-v1'))

        mock_session = Mock()
        mock_session.client = Mock(return_value=mock_client)
        mock_session_class.return_value = mock_session

        # Test
        res = asyncio.run(
            self.embedding.async_get_embeddings(texts=["hello world"]))

        # Assertions
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1536)
        print("✓ test_async_get_embeddings_mock passed")

    @patch('boto3.Session')
    def test_normalize_option_mock(self, mock_session_class) -> None:
        """Test normalization option with mock."""
        # Setup
        mock_client = Mock()
        mock_client.invoke_model = Mock(
            return_value=create_mock_response('amazon.titan-embed-text-v1'))

        mock_session = Mock()
        mock_session.client = Mock(return_value=mock_client)
        mock_session_class.return_value = mock_session

        # Test with normalization enabled
        self.embedding.normalize = True
        res_normalized = self.embedding.get_embeddings(texts=["hello world"])

        # Test with normalization disabled
        self.embedding.client = None  # Reset client
        self.embedding.normalize = False
        res_not_normalized = self.embedding.get_embeddings(texts=["hello world"])

        # Assertions - both should work
        self.assertEqual(len(res_normalized[0]), 1536)
        self.assertEqual(len(res_not_normalized[0]), 1536)
        print("✓ test_normalize_option_mock passed")

    @patch('boto3.Session')
    def test_as_langchain_mock(self, mock_session_class) -> None:
        """Test LangChain conversion with mock."""
        # Setup
        mock_client = Mock()
        mock_session = Mock()
        mock_session.client = Mock(return_value=mock_client)
        mock_session_class.return_value = mock_session

        # Test
        langchain_embedding = self.embedding.as_langchain()

        # Assertions
        self.assertIsNotNone(langchain_embedding)
        # Verify it's a BedrockEmbeddings instance
        from langchain_community.embeddings import BedrockEmbeddings
        self.assertIsInstance(langchain_embedding, BedrockEmbeddings)
        print("✓ test_as_langchain_mock passed")

    def test_error_handling_missing_model(self) -> None:
        """Test error handling when model name is missing."""
        self.embedding.embedding_model_name = None

        with self.assertRaises(ValueError) as context:
            self.embedding.get_embeddings(texts=["test"])

        self.assertIn("embedding_model_name", str(context.exception))
        print("✓ test_error_handling_missing_model passed")

    @patch('boto3.Session')
    def test_error_handling_unsupported_model_mock(self, mock_session_class) -> None:
        """Test error handling for unsupported model with mock."""
        # Setup
        self.embedding.embedding_model_name = "unsupported.model"

        mock_client = Mock()
        mock_session = Mock()
        mock_session.client = Mock(return_value=mock_client)
        mock_session_class.return_value = mock_session

        # Test
        with self.assertRaises(Exception) as context:
            self.embedding.get_embeddings(texts=["test"])

        self.assertIn("Unsupported model", str(context.exception))
        print("✓ test_error_handling_unsupported_model_mock passed")

    # ========== Real API Tests (Require AWS credentials) ==========

    def test_get_embeddings_titan_v1_real(self) -> None:
        """Test Titan v1 embeddings with real API.

        This test requires:
        - boto3 installed
        - Valid AWS credentials configured
        - Access to AWS Bedrock Titan v1 model
        """
        try:
            res = self.embedding.get_embeddings(texts=["hello world"])

            self.assertIsInstance(res, list)
            self.assertEqual(len(res), 1)
            self.assertEqual(len(res[0]), 1536)
            print(f"✓ Titan v1 embedding generated: {len(res[0])} dimensions")

        except ImportError as e:
            self.skipTest(f"boto3 not installed: {e}")
        except Exception as e:
            if "credentials" in str(e).lower() or "unauthorized" in str(e).lower():
                self.skipTest(f"AWS credentials not available: {e}")
            else:
                raise

    def test_get_embeddings_titan_v2_real(self) -> None:
        """Test Titan v2 with custom dimensions using real API."""
        try:
            self.embedding.embedding_model_name = "amazon.titan-embed-text-v2"
            self.embedding.dimensions = 1024

            res = self.embedding.get_embeddings(texts=["hello world"])

            self.assertEqual(len(res[0]), 1024)
            print(f"✓ Titan v2 embedding generated: {len(res[0])} dimensions")

        except ImportError as e:
            self.skipTest(f"boto3 not installed: {e}")
        except Exception as e:
            if "credentials" in str(e).lower() or "unauthorized" in str(e).lower():
                self.skipTest(f"AWS credentials not available: {e}")
            else:
                raise

    def test_get_embeddings_cohere_real(self) -> None:
        """Test Cohere embeddings with real API."""
        try:
            self.embedding.embedding_model_name = "cohere.embed-multilingual-v3"

            res = self.embedding.get_embeddings(texts=["hello world"])

            self.assertEqual(len(res[0]), 1024)
            print(f"✓ Cohere embedding generated: {len(res[0])} dimensions")

        except ImportError as e:
            self.skipTest(f"boto3 not installed: {e}")
        except Exception as e:
            if "credentials" in str(e).lower() or "unauthorized" in str(e).lower():
                self.skipTest(f"AWS credentials not available: {e}")
            else:
                raise


if __name__ == '__main__':
    unittest.main()
