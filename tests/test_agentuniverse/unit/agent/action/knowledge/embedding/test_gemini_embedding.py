# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2025/2/13 20:00
# @Author  : wozhapen
# @Email   : wozhapen@gmail.com
# @FileName: test_gemini_embedding.py
import asyncio
import unittest
import os

from agentuniverse.agent.action.knowledge.embedding.gemini_embedding import GeminiEmbedding

class GeminiEmbeddingTest(unittest.TestCase):
    """
    Test cases for Embedding class
    """

    def setUp(self) -> None:
        self.embedding = GeminiEmbedding(embedding_model_name='text-embedding-004',
                                         embedding_dims=768,
                                         gemini_api_key='xxxxxxx')
        # Gemini does not have a native proxy solution.
        # os.environ will proxy the whole application. It's only for test
        # os.environ['https_proxy'] = 'http://127.0.0.1:10808'

    def test_get_embeddings(self) -> None:
        res = self.embedding.get_embeddings(texts=["hello world", "agentUniverse"])
        print(res)
        self.assertEqual(len(res), 2)
        self.assertEqual(len(res[0]), 768)

    def test_async_get_embeddings(self) -> None:
        res = asyncio.run(self.embedding.async_get_embeddings(texts=["hello world", "agentUniverse"]))
        print(res)
        self.assertEqual(len(res), 2)
        self.assertEqual(len(res[0]), 768)

    def test_as_langchain(self) -> None:
        langchain_embedding = self.embedding.as_langchain()
        res = langchain_embedding.embed_documents(texts=["hello world", "agentUniverse"])
        print(res)
        self.assertEqual(len(res), 2)
        self.assertEqual(len(res[0]), 768)


if __name__ == '__main__':
    unittest.main()
