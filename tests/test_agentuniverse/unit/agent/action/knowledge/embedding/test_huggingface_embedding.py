#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/05
# @FileName: test_huggingface_embedding.py

"""Unit tests for the HuggingFace embedding implementation.

The huggingface inference clients are mocked, no real network call is made.
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from agentuniverse.agent.action.knowledge.embedding.huggingface_embedding import HuggingFaceEmbedding


class HuggingFaceEmbeddingTest(unittest.TestCase):
    """Test suite for HuggingFaceEmbedding."""

    def setUp(self) -> None:
        self.embedding = HuggingFaceEmbedding(huggingface_api_key='hf_test_token')

    def test_default_model_name(self) -> None:
        self.assertEqual(self.embedding.embedding_model_name,
                         'sentence-transformers/all-MiniLM-L6-v2')

    def test_api_key_fallback_to_hf_token(self) -> None:
        with patch.dict('os.environ', {'HF_TOKEN': 'hf_env_token'}, clear=False):
            embedding = HuggingFaceEmbedding()
            self.assertEqual(embedding.huggingface_api_key, 'hf_env_token')

    def test_get_embeddings(self) -> None:
        self.embedding.client = MagicMock()
        self.embedding.async_client = MagicMock()
        self.embedding.client.feature_extraction.return_value = [[0.1, 0.2, 0.3]]

        result = self.embedding.get_embeddings(['hello', 'world'])

        self.assertEqual(result, [[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]])
        self.assertEqual(self.embedding.client.feature_extraction.call_count, 2)

    def test_get_embeddings_mean_pooling(self) -> None:
        self.embedding.client = MagicMock()
        self.embedding.async_client = MagicMock()
        # token level embeddings: 2 tokens x 2 dims
        self.embedding.client.feature_extraction.return_value = [[1.0, 2.0], [3.0, 6.0]]

        self.assertEqual(self.embedding.get_embeddings(['hello']), [[2.0, 4.0]])

    def test_get_embeddings_raises_on_client_error(self) -> None:
        self.embedding.client = MagicMock()
        self.embedding.async_client = MagicMock()
        self.embedding.client.feature_extraction.side_effect = ValueError('boom')

        with self.assertRaises(Exception) as context:
            self.embedding.get_embeddings(['hello'])
        self.assertIn('Failed to get embedding from HuggingFace API', str(context.exception))

    def test_async_get_embeddings(self) -> None:
        self.embedding.client = MagicMock()
        self.embedding.async_client = MagicMock()
        self.embedding.async_client.feature_extraction = AsyncMock(return_value=[0.5, 0.6])

        result = asyncio.run(self.embedding.async_get_embeddings(['hello', 'world']))

        self.assertEqual(result, [[0.5, 0.6], [0.5, 0.6]])
        self.assertEqual(self.embedding.async_client.feature_extraction.await_count, 2)

    def test_initialize_clients_uses_model_name(self) -> None:
        sync_client, async_client = MagicMock(), MagicMock()
        module = MagicMock(InferenceClient=MagicMock(return_value=sync_client),
                           AsyncInferenceClient=MagicMock(return_value=async_client))
        with patch.dict('sys.modules', {'huggingface_hub': module}):
            self.embedding._initialize_clients()

        self.assertIs(self.embedding.client, sync_client)
        self.assertIs(self.embedding.async_client, async_client)
        client_kwargs = module.InferenceClient.call_args.kwargs
        self.assertEqual(client_kwargs['model'], 'sentence-transformers/all-MiniLM-L6-v2')
        self.assertEqual(client_kwargs['api_key'], 'hf_test_token')
        self.assertNotIn('base_url', client_kwargs)

    def test_initialize_clients_uses_base_url(self) -> None:
        self.embedding.huggingface_base_url = 'http://localhost:8080'
        module = MagicMock()
        with patch.dict('sys.modules', {'huggingface_hub': module}):
            self.embedding._initialize_clients()

        client_kwargs = module.InferenceClient.call_args.kwargs
        self.assertEqual(client_kwargs['base_url'], 'http://localhost:8080')
        self.assertNotIn('model', client_kwargs)

    def test_initialize_clients_missing_model_name(self) -> None:
        self.embedding.embedding_model_name = None
        with self.assertRaises(Exception) as context:
            self.embedding._initialize_clients()
        self.assertIn('embedding_model_name is missing', str(context.exception))

    def test_initialize_clients_missing_dependency(self) -> None:
        with patch.dict('sys.modules', {'huggingface_hub': None}):
            with self.assertRaises(ImportError) as context:
                self.embedding._initialize_clients()
        self.assertIn('huggingface_hub is required', str(context.exception))

    def test_to_vector_shapes(self) -> None:
        self.assertEqual(HuggingFaceEmbedding._to_vector([1.0, 2.0]), [1.0, 2.0])
        self.assertEqual(HuggingFaceEmbedding._to_vector([[1.0, 2.0]]), [1.0, 2.0])
        self.assertEqual(HuggingFaceEmbedding._to_vector([[[1.0, 2.0]]]), [1.0, 2.0])
        self.assertEqual(HuggingFaceEmbedding._to_vector([[1.0, 2.0], [3.0, 6.0]]), [2.0, 4.0])

    def test_to_vector_numpy_result(self) -> None:
        import numpy as np
        self.assertEqual(HuggingFaceEmbedding._to_vector(np.array([[1.0, 2.0], [3.0, 6.0]])),
                         [2.0, 4.0])

    def test_to_vector_invalid_result(self) -> None:
        with self.assertRaises(Exception):
            HuggingFaceEmbedding._to_vector([])

    def test_as_langchain_inference_api(self) -> None:
        langchain_embedding = self.embedding.as_langchain()
        self.assertIsNotNone(langchain_embedding)
        self.assertIn('HuggingFace', type(langchain_embedding).__name__)

    def test_as_langchain_endpoint(self) -> None:
        self.embedding.huggingface_base_url = 'http://localhost:8080'
        langchain_embedding = self.embedding.as_langchain()
        self.assertIsNotNone(langchain_embedding)
        self.assertIn('HuggingFace', type(langchain_embedding).__name__)

    def test_as_langchain_falls_back_to_adapter(self) -> None:
        """No maintained langchain class available -> use the self delegating adapter.

        The legacy `HuggingFaceHubEmbeddings` must never be used as a fallback since it
        calls `InferenceClient.post`, which was removed in huggingface_hub v1.0.
        """
        with patch.object(HuggingFaceEmbedding, '_load_langchain_clz', return_value=None):
            langchain_embedding = self.embedding.as_langchain()
        self.assertEqual(type(langchain_embedding).__name__, '_HuggingFaceLangchainEmbeddings')

    def test_langchain_adapter_delegates_to_component(self) -> None:
        self.embedding.client = MagicMock()
        self.embedding.async_client = MagicMock()
        self.embedding.client.feature_extraction.return_value = [[0.1, 0.2]]
        with patch.object(HuggingFaceEmbedding, '_load_langchain_clz', return_value=None):
            adapter = self.embedding.as_langchain()

        self.assertEqual(adapter.embed_documents(['a', 'b']), [[0.1, 0.2], [0.1, 0.2]])
        self.assertEqual(adapter.embed_query('a'), [0.1, 0.2])

    def test_load_langchain_clz_optional_returns_none(self) -> None:
        self.assertIsNone(
            HuggingFaceEmbedding._load_langchain_clz([('no_such_module', 'X')], required=False))

    def test_load_langchain_clz_required_raises(self) -> None:
        with self.assertRaises(ImportError):
            HuggingFaceEmbedding._load_langchain_clz([('no_such_module', 'X')])


if __name__ == '__main__':
    unittest.main()
