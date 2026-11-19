# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/02/15 23:35
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: test_doubao_embedding.py

import asyncio
import unittest

from agentuniverse.agent.action.knowledge.embedding.doubao_embedding import DoubaoEmbedding


class EmbeddingTest(unittest.TestCase):
    """
    Test cases for Embedding class
    """

    def setUp(self) -> None:
        self.embedding = DoubaoEmbedding()
        self.embedding.ark_api_key = "replace with your api key"
        self.embedding.endpoint_id = "replace with your endpoint id :)"
        self.embedding.embedding_dims = 1024

    def test_get_embeddings(self) -> None:
        res = self.embedding.get_embeddings(texts=["hello world"])
        print(res)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1024)

    def test_async_get_embeddings(self) -> None:
        res = asyncio.run(
            self.embedding.async_get_embeddings(texts=["hello world"]))
        print(res)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1024)


if __name__ == '__main__':
    unittest.main()
