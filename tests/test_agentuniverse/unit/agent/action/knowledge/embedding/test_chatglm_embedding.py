#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 6/11/25 10:51
# @Author  : Ke Jiang
# @Email   : yitong.jk@antgroup.com
# @FileName: test_chatglm_embedding.py

import asyncio
import unittest
from unittest.mock import Mock, patch
from agentuniverse.agent.action.knowledge.embedding.chatglm_embedding import (
    ChatGLMEmbedding,
    ChatGLMEmbeddingError
)

class ChatGLMEmbeddingTest(unittest.TestCase):
    """
    Test cases for ChatGLMEmbedding class
    """

    def setUp(self) -> None:
        self.embedding = ChatGLMEmbedding()
        self.embedding.chatglm_api_key = "d75f7a90180a426faef9c4d08f1c69df.ESVtzV2JiYY0pyUR"
        self.embedding.embedding_model_name = "embedding-3"
        # embedding_dims will use default value 1024

    def test_embedding_dims_default(self) -> None:
        """Test that the default embedding_dims is 1024"""
        self.assertEqual(self.embedding.embedding_dims, 1024)

    def test_embedding_dims_custom(self) -> None:
        """Test that we can set a custom embedding_dims"""
        self.embedding.embedding_dims = 512
        self.assertEqual(self.embedding.embedding_dims, 512)

    def test_missing_api_key(self) -> None:
        """Test that missing API key raises ChatGLMEmbeddingError"""
        embedding = ChatGLMEmbedding()
        embedding.chatglm_api_key = None
        embedding.embedding_model_name = "embedding-3"

        with self.assertRaises(ChatGLMEmbeddingError) as context:
            embedding.get_embeddings(texts=["hello world"])

        self.assertIn("chatglm_api_key is missing", str(context.exception))

    def test_empty_texts(self) -> None:
        """Test that empty texts list raises ValueError"""
        embedding = ChatGLMEmbedding()
        embedding.chatglm_api_key = "test_api_key"
        embedding.embedding_model_name = "embedding-3"

        with self.assertRaises(ValueError) as context:
            embedding.get_embeddings(texts=[])

        self.assertIn("Input texts cannot be empty", str(context.exception))

    def test_missing_model_name(self) -> None:
        """Test that missing model name raises ValueError"""
        embedding = ChatGLMEmbedding()
        embedding.chatglm_api_key = "test_api_key"
        # embedding_model_name is None by default

        with self.assertRaises(ValueError) as context:
            embedding.get_embeddings(texts=["hello world"])

        self.assertIn("embedding_model_name must be set", str(context.exception))

    def test_build_api_params_empty_texts(self) -> None:
        """Test that _build_api_params raises ValueError for empty texts"""
        with self.assertRaises(ValueError) as context:
            self.embedding._build_api_params([])

        self.assertIn("Input texts cannot be empty", str(context.exception))

    @patch('agentuniverse.agent.action.knowledge.embedding.chatglm_embedding.ZhipuAiClient')
    def test_get_embeddings_success(self, mock_client_class) -> None:
        """Test successful embedding retrieval"""
        # Mock the client and response
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock the response
        mock_response = Mock()
        mock_data_item = Mock()
        mock_data_item.embedding = [0.1, 0.2, 0.3]
        mock_response.data = [mock_data_item]
        mock_client.embeddings.create.return_value = mock_response

        # Create a new embedding instance to use the mocked client
        embedding = ChatGLMEmbedding()
        embedding.chatglm_api_key = "test_api_key"
        embedding.embedding_model_name = "embedding-3"

        # Call the method
        result = embedding.get_embeddings(texts=["hello world"])

        # Assertions
        self.assertEqual(result, [[0.1, 0.2, 0.3]])
        mock_client.embeddings.create.assert_called_once_with(
            input=["hello world"],
            model="embedding-3",
            dimensions=1024
        )

    @patch('agentuniverse.agent.action.knowledge.embedding.chatglm_embedding.ZhipuAiClient')
    def test_async_get_embeddings_success(self, mock_client_class) -> None:
        """Test successful async embedding retrieval"""
        # Mock the client and response
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock the async response
        mock_response = Mock()
        mock_data_item = Mock()
        mock_data_item.embedding = [0.4, 0.5, 0.6]
        mock_response.data = [mock_data_item]

        # Create a coroutine mock for the async method
        async def mock_create(**kwargs):
            return mock_response

        mock_client.embeddings.create = mock_create

        # Create a new embedding instance to use the mocked client
        embedding = ChatGLMEmbedding()
        embedding.chatglm_api_key = "test_api_key"
        embedding.embedding_model_name = "embedding-3"

        # Call the async method
        result = asyncio.run(embedding.async_get_embeddings(texts=["hello world"]))

        # Assertions
        self.assertEqual(result, [[0.4, 0.5, 0.6]])

    def test_async_empty_texts(self) -> None:
        """Test that empty texts list raises ValueError in async method"""
        embedding = ChatGLMEmbedding()
        embedding.chatglm_api_key = "test_api_key"
        embedding.embedding_model_name = "embedding-3"

        with self.assertRaises(ValueError) as context:
            asyncio.run(embedding.async_get_embeddings(texts=[]))

        self.assertIn("Input texts cannot be empty", str(context.exception))

    def test_async_missing_model_name(self) -> None:
        """Test that missing model name raises ValueError in async method"""
        embedding = ChatGLMEmbedding()
        embedding.chatglm_api_key = "test_api_key"
        # embedding_model_name is None by default

        with self.assertRaises(ValueError) as context:
            asyncio.run(embedding.async_get_embeddings(texts=["hello world"]))

        self.assertIn("embedding_model_name must be set", str(context.exception))

    @patch('agentuniverse.agent.action.knowledge.embedding.chatglm_embedding.ZhipuAiClient')
    def test_api_status_error(self, mock_client_class) -> None:
        """Test handling of APIStatusError"""
        from zai.core import APIStatusError

        # Mock the client to raise APIStatusError
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_response = Mock()
        mock_client.embeddings.create.side_effect = APIStatusError(message="API Error", response=mock_response)

        # Create a new embedding instance
        embedding = ChatGLMEmbedding()
        embedding.chatglm_api_key = "test_api_key"
        embedding.embedding_model_name = "embedding-3"

        # Call the method and expect an exception
        with self.assertRaises(ChatGLMEmbeddingError) as context:
            embedding.get_embeddings(texts=["hello world"])

        self.assertIn("ChatGLM API status error", str(context.exception))

    def test_build_api_params(self) -> None:
        """Test the _build_api_params method"""
        # Test with default parameters
        params = self.embedding._build_api_params(["hello world"])
        expected = {
            "input": ["hello world"],
            "model": "embedding-3",
            "dimensions": 1024  # Default dimensions is always included
        }
        self.assertEqual(params, expected)

        # Test with custom dimensions
        self.embedding.embedding_dims = 512
        params = self.embedding._build_api_params(["hello world"])
        expected = {
            "input": ["hello world"],
            "model": "embedding-3",
            "dimensions": 512
        }
        self.assertEqual(params, expected)

        # Test with additional kwargs
        params = self.embedding._build_api_params(["hello world"], custom_param="value")
        expected = {
            "input": ["hello world"],
            "model": "embedding-3",
            "dimensions": 512,
            "custom_param": "value"
        }
        self.assertEqual(params, expected)

        # Test that kwargs don't override required params
        params = self.embedding._build_api_params(["hello world"], input="should not override")
        self.assertEqual(params["input"], ["hello world"])  # Should not be overridden

if __name__ == '__main__':
    unittest.main()