#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/12 18:00
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: test_huggingface_hub_embedding_integrate.py

import asyncio
import os
import unittest


from agentuniverse.agent.action.knowledge.embedding.huggingface_hub_embedding import HuggingFaceHubEmbedding


class HuggingFaceHubEmbeddingIntegrateTest(unittest.TestCase):
    """
    Integration test cases for HuggingFaceHubEmbedding class
    """

    def setUp(self) -> None:
        """Set up test fixtures with real API key and model for integration testing."""
        self.embedding = HuggingFaceHubEmbedding(api_key="your_huggingface_hub_api_key", embedding_model_name="intfloat/multilingual-e5-large")
        # Hugging Face does not have a native proxy solution.
        # os.environ will proxy the whole application. It's only for test
        # os.environ['https_proxy'] = 'socks5://127.0.0.1:13659'
        # os.environ['http_proxy'] = 'socks5://127.0.0.1:13659'

    def test_get_embeddings(self) -> None:
        """Test successful synchronous embedding retrieval with real API."""
        res = self.embedding.get_embeddings(texts=["hello world", "你好"])
        self.assertEqual(len(res), 2)
        self.assertEqual(len(res[0]), 1024)
        self.assertEqual(len(res[1]), 1024)

    def test_async_get_embeddings(self) -> None:
        """Test successful asynchronous embedding retrieval with real API."""
        res = asyncio.run(self.embedding.async_get_embeddings(texts=["hello world", "你好"]))
        self.assertEqual(len(res), 2)
        self.assertEqual(len(res[0]), 1024)
        self.assertEqual(len(res[1]), 1024)

    def test_as_langchain_embed_documents(self) -> None:
        """Test Langchain adapter embed_documents method with real API."""
        langchain_embedding = self.embedding.as_langchain()
        res = langchain_embedding.embed_documents(texts=["hello world", "你好"])
        self.assertEqual(len(res), 2)
        self.assertEqual(len(res[0]), 1024)
        self.assertEqual(len(res[1]), 1024)

    def test_as_langchain_embed_query(self) -> None:
        """Test Langchain adapter embed_query method with real API."""
        langchain_embedding = self.embedding.as_langchain()
        res = langchain_embedding.embed_query(text="hello world")
        self.assertEqual(len(res), 1024)



if __name__ == '__main__':
    unittest.main()