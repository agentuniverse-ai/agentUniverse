#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/15
# @Author  : dxz0069
# @FileName: test_huggingface_embedding.py

import asyncio
import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.embedding.huggingface_embedding import (
    HUGGINGFACE_INFERENCE_API_BASE,
    HuggingFaceEmbedding,
    _mean_pool_if_needed,
)


def _embedding(model='sentence-transformers/all-MiniLM-L6-v2', api_key='hf-token', **overrides):
    params = dict(embedding_model_name=model, api_key=api_key)
    params.update(overrides)
    return HuggingFaceEmbedding(**params)


def _response(payload):
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


class TestHuggingFaceEmbedding(unittest.TestCase):
    """Test suite for the Hugging Face embedding, run against mocked httpx."""

    def setUp(self):
        self.embedding = _embedding()

    def test_defaults(self):
        self.assertEqual(self.embedding.api_base, HUGGINGFACE_INFERENCE_API_BASE)
        self.assertEqual(self.embedding.timeout, 30)

    def test_get_embeddings_pooled_output(self):
        payload = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        with patch('agentuniverse.agent.action.knowledge.embedding.huggingface_embedding.httpx.Client') as client_cls:
            client_cls.return_value.post.return_value = _response(payload)
            result = self.embedding.get_embeddings(["hello", "world"])
        request = client_cls.return_value.post.call_args
        self.assertEqual(
            request.args[0],
            f"{HUGGINGFACE_INFERENCE_API_BASE}/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2")
        self.assertEqual(request.kwargs['headers']['Authorization'], 'Bearer hf-token')
        self.assertEqual(request.kwargs['json'], {"inputs": ["hello", "world"], "options": {"wait_for_model": True}})
        self.assertEqual(result, payload)

    def test_get_embeddings_token_level_output_is_mean_pooled(self):
        payload = [
            [[1.0, 3.0], [3.0, 5.0]],  # mean -> [2.0, 4.0]
        ]
        with patch('agentuniverse.agent.action.knowledge.embedding.huggingface_embedding.httpx.Client') as client_cls:
            client_cls.return_value.post.return_value = _response(payload)
            result = self.embedding.get_embeddings(["hello"])
        self.assertEqual(result, [[2.0, 4.0]])

    def test_async_get_embeddings(self):
        payload = [[0.1, 0.2], [0.3, 0.4]]
        with patch('agentuniverse.agent.action.knowledge.embedding.huggingface_embedding.httpx.AsyncClient') as client_cls:

            async def _post(*args, **kwargs):
                return _response(payload)

            client_cls.return_value.post = _post
            result = asyncio.run(self.embedding.async_get_embeddings(["a", "b"]))
        self.assertEqual(result, payload)

    def test_missing_api_key_raises(self):
        embedding = HuggingFaceEmbedding(embedding_model_name='m')
        with self.assertRaises(ValueError):
            embedding.get_embeddings(["hello"])

    def test_missing_model_raises(self):
        embedding = HuggingFaceEmbedding(api_key='hf-token')
        with self.assertRaises(ValueError):
            embedding.get_embeddings(["hello"])

    def test_answer_count_mismatch_raises(self):
        with patch('agentuniverse.agent.action.knowledge.embedding.huggingface_embedding.httpx.Client') as client_cls:
            client_cls.return_value.post.return_value = _response([[0.1, 0.2]])
            with self.assertRaises(ValueError):
                self.embedding.get_embeddings(["hello", "world"])

    def test_custom_api_base(self):
        embedding = _embedding(api_base='https://my-proxy.example.com/')
        with patch('agentuniverse.agent.action.knowledge.embedding.huggingface_embedding.httpx.Client') as client_cls:
            client_cls.return_value.post.return_value = _response([[0.1]])
            embedding.get_embeddings(["hello"])
        url = client_cls.return_value.post.call_args.args[0]
        self.assertEqual(url, "https://my-proxy.example.com/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2")

    def test_mean_pool_helper(self):
        self.assertEqual(_mean_pool_if_needed([1.0, 2.0]), [1.0, 2.0])
        self.assertEqual(_mean_pool_if_needed([[2.0], [4.0]]), [3.0])
        self.assertEqual(_mean_pool_if_needed([]), [])
        self.assertEqual(_mean_pool_if_needed("bad"), [])


if __name__ == '__main__':
    unittest.main()
