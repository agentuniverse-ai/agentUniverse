# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/22 10:27
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_embedding.py
import asyncio
import unittest

from agentuniverse.agent.action.knowledge.embedding.openai_embedding import OpenAIEmbedding


class EmbeddingTest(unittest.TestCase):
    """
    Test cases for Embedding class
    """

    def setUp(self) -> None:
        """Create an OpenAIEmbedding instance for the test methods."""
        self.embedding = OpenAIEmbedding(embedding_model_name='text-embedding-3-small',
                                         dimensions=1536)

    def test_get_embeddings(self) -> None:
        """Verify that get_embeddings returns a non-empty list."""
        res = self.embedding.get_embeddings(texts=["hello world"])
        print(res)
        self.assertIsNotNone(res)  
        self.assertIsInstance(res, list)  
        self.assertGreater(len(res), 0)

    def test_async_get_embeddings(self) -> None:
        """Verify that async_get_embeddings returns embeddings via asyncio.run."""
        res = asyncio.run(self.embedding.async_get_embeddings(texts=["hello world"]))
        print(res)

    def test_as_langchain(self) -> None:
        """Verify that as_langchain produces a working langchain embedding wrapper."""
        langchain_embedding = self.embedding.as_langchain()
        res = langchain_embedding.embed_documents(texts=["hello world"])
        print(res)


if __name__ == '__main__':
    unittest.main()
