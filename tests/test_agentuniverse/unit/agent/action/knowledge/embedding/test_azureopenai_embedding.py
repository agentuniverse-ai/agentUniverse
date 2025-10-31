# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2/16/25 9:51 PM
# @Author  : Xinyuan Xu
# @Email   : xuxinyuan2019@gmail.com
# @FileName: test_azureopenai_embedding.py

import asyncio
import unittest
from agentuniverse.agent.action.knowledge.embedding.azureopenai_embedding import AzureOpenAIEmbedding

class EmbeddingTest(unittest.TestCase):
    """
    Test cases for Embedding class
    """

    def setUp(self) -> None:
        self.embedding = AzureOpenAIEmbedding()
        self.embedding.azure_api_key = "Your_API_Key"
        self.embedding.resource_name = "Your_Resource_Name"
        self.embedding.embedding_model_name = "text-embedding-ada-002"
        self.embedding.azure_api_version = '2023-05-15'

    def test_get_embeddings(self) -> None:
        res = self.embedding.get_embeddings(texts=["hello world"])
        print(res)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1536)

    def test_async_get_embeddings(self) -> None:
        res = asyncio.run(
            self.embedding.async_get_embeddings(texts=["hello world"]))
        print(res)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1536)

    def test_as_langchain(self) -> None:
        langchain_embedding = self.embedding.as_langchain()
        res = langchain_embedding.embed_documents(texts=["hello world"])
        print(res)
        self.assertIsInstance(res, list)  
        self.assertEqual(len(res), 1)  
        self.assertIsInstance(res[0], list)  
        self.assertEqual(len(res[0]), 1536)

if __name__ == '__main__':
    unittest.main()