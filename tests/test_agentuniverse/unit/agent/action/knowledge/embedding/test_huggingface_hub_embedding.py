#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/12 18:00
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: test_huggingface_hub_embedding.py

import asyncio
import unittest
from unittest.mock import Mock, patch
import numpy as np

from agentuniverse.agent.action.knowledge.embedding.huggingface_hub_embedding import HuggingFaceHubEmbedding, HuggingFaceHubEmbeddingError
from huggingface_hub.errors import InferenceTimeoutError, HfHubHTTPError


class HuggingFaceHubEmbeddingTest(unittest.TestCase):
    """
    Test cases for HuggingFaceHubEmbedding class
    """

    def setUp(self) -> None:        
        self.embedding = HuggingFaceHubEmbedding(api_key="test_api_key", embedding_model_name="test_model")
        
        # Mock the clients
        self.embedding.client = Mock()
        self.embedding.async_client = Mock()

    def test_get_embeddings_success(self) -> None:
        """Test successful synchronous embedding retrieval."""
        # Mock the feature_extraction method to return a numpy array
        mock_embedding = np.array([0.1, 0.2, 0.3])
        self.embedding.client.feature_extraction.return_value = mock_embedding
        
        texts = ["Hello world", "Test text"]
        result = self.embedding.get_embeddings(texts)
        
        # Verify the client method was called correctly
        self.assertEqual(self.embedding.client.feature_extraction.call_count, 2)
        self.embedding.client.feature_extraction.assert_any_call(text="Hello world", model="test_model")
        self.embedding.client.feature_extraction.assert_any_call(text="Test text", model="test_model")
        
        # Verify the result
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [0.1, 0.2, 0.3])
        self.assertEqual(result[1], [0.1, 0.2, 0.3])

    def test_get_embeddings_missing_model_name(self) -> None:
        """Test embedding retrieval with missing model name."""
        self.embedding.embedding_model_name = None
        
        with self.assertRaises(ValueError) as context:
            self.embedding.get_embeddings(["test text"])
        
        self.assertIn("Must provide `embedding_model_name`", str(context.exception))

    def test_get_embeddings_timeout_error(self) -> None:
        """Test embedding retrieval with timeout error."""
        self.embedding.client.feature_extraction.side_effect = InferenceTimeoutError("Request timed out")
        
        with self.assertRaises(HuggingFaceHubEmbeddingError) as context:
            self.embedding.get_embeddings(["test text"])
        
        self.assertIn("Model is unavailable or the request times out", str(context.exception))

    def test_get_embeddings_http_error(self) -> None:
        """Test embedding retrieval with HTTP error."""
        # Create a mock response object for HfHubHTTPError
        mock_response = Mock()
        mock_response.status_code = 404
        self.embedding.client.feature_extraction.side_effect = HfHubHTTPError("HTTP 404 error", response=mock_response)
        
        with self.assertRaises(HuggingFaceHubEmbeddingError) as context:
            self.embedding.get_embeddings(["test text"])
        
        self.assertIn("Request failed with an HTTP error status code", str(context.exception))

    def test_get_embeddings_generic_error(self) -> None:
        """Test embedding retrieval with generic error."""
        self.embedding.client.feature_extraction.side_effect = Exception("Unexpected error")
        
        with self.assertRaises(HuggingFaceHubEmbeddingError) as context:
            self.embedding.get_embeddings(["test text"])
        
        self.assertIn("Unexpected error getting embeddings from Hugging Face Hub", str(context.exception))

    def test_async_get_embeddings_success(self) -> None:
        """Test successful asynchronous embedding retrieval."""
        async def mock_feature_extraction(*args, **kwargs):
            return np.array([0.1, 0.2, 0.3])
        
        # Mock the async client method
        self.embedding.async_client.feature_extraction = mock_feature_extraction
        
        texts = ["Hello world", "Test text"]
        result = asyncio.run(self.embedding.async_get_embeddings(texts))
        
        # Verify the result
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [0.1, 0.2, 0.3])
        self.assertEqual(result[1], [0.1, 0.2, 0.3])

    def test_async_get_embeddings_missing_model_name(self) -> None:
        """Test async embedding retrieval with missing model name."""
        self.embedding.embedding_model_name = None
        
        with self.assertRaises(ValueError) as context:
            asyncio.run(self.embedding.async_get_embeddings(["test text"]))
        
        self.assertIn("Must provide `embedding_model_name`", str(context.exception))

    def test_async_get_embeddings_timeout_error(self) -> None:
        """Test async embedding retrieval with timeout error."""
        async def mock_feature_extraction_timeout(*args, **kwargs):
            raise InferenceTimeoutError("Request timed out")
        
        self.embedding.async_client.feature_extraction = mock_feature_extraction_timeout
        
        with self.assertRaises(HuggingFaceHubEmbeddingError) as context:
            asyncio.run(self.embedding.async_get_embeddings(["test text"]))
        
        self.assertIn("Model is unavailable or the request times out", str(context.exception))

    def test_async_get_embeddings_http_error(self) -> None:
        """Test async embedding retrieval with HTTP error."""
        async def mock_feature_extraction_http_error(*args, **kwargs):
            # Create a mock response object for HfHubHTTPError
            mock_response = Mock()
            mock_response.status_code = 404
            raise HfHubHTTPError("HTTP 404 error", response=mock_response)
        
        self.embedding.async_client.feature_extraction = mock_feature_extraction_http_error
        
        with self.assertRaises(HuggingFaceHubEmbeddingError) as context:
            asyncio.run(self.embedding.async_get_embeddings(["test text"]))
        
        self.assertIn("Request failed with an HTTP error status code", str(context.exception))

    def test_async_get_embeddings_generic_error(self) -> None:
        """Test async embedding retrieval with generic error."""
        async def mock_feature_extraction_generic_error(*args, **kwargs):
            raise Exception("Unexpected error")
        
        self.embedding.async_client.feature_extraction = mock_feature_extraction_generic_error
        
        with self.assertRaises(HuggingFaceHubEmbeddingError) as context:
            asyncio.run(self.embedding.async_get_embeddings(["test text"]))
        
        self.assertIn("Unexpected error getting embeddings from Hugging Face Hub", str(context.exception))

    def test_as_langchain(self) -> None:
        """Test the Langchain adapter."""
        # Create a real instance for testing the langchain adapter
        with patch.object(HuggingFaceHubEmbedding, 'get_embeddings', return_value=[[0.1, 0.2, 0.3]]):
            langchain_embedding = self.embedding.as_langchain()
            
            # Test embed_documents
            result = langchain_embedding.embed_documents(["test text"])
            self.assertEqual(result, [[0.1, 0.2, 0.3]])
            
            # Test embed_query
            with patch.object(HuggingFaceHubEmbedding, 'get_embeddings', return_value=[[0.4, 0.5, 0.6]]):
                result = langchain_embedding.embed_query("query text")
                self.assertEqual(result, [0.4, 0.5, 0.6])

    def test_initialize_clients_without_api_key(self) -> None:
        """Test client initialization without API key."""
        with self.assertRaises(ValueError) as context:
            HuggingFaceHubEmbedding(api_key=None)
        
        self.assertIn("Must provide `api_key` for Hugging Face Hub Inference", str(context.exception))

    def test_initialize_clients_with_api_key(self) -> None:
        """Test client initialization with API key."""
        with patch('agentuniverse.agent.action.knowledge.embedding.huggingface_hub_embedding.InferenceClient') as mock_client, \
             patch('agentuniverse.agent.action.knowledge.embedding.huggingface_hub_embedding.AsyncInferenceClient') as mock_async_client:
            
            with patch.object(HuggingFaceHubEmbedding, '_initialize_clients'):
                embedding = HuggingFaceHubEmbedding(api_key="test_api_key", embedding_model_name="test_model")
                embedding.provider = "test_provider"
                embedding.timeout = 30
                
            # Now test _initialize_clients separately
            mock_client.reset_mock()
            mock_async_client.reset_mock()
            embedding._initialize_clients()
            
            # Verify clients were initialized with correct parameters
            mock_client.assert_called_once_with(
                provider="test_provider",
                api_key="test_api_key",
                timeout=30
            )
            
            mock_async_client.assert_called_once_with(
                provider="test_provider",
                api_key="test_api_key",
                timeout=30
            )


if __name__ == '__main__':
    unittest.main()