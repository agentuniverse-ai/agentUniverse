# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/20 10:10
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_knowledge.py
import unittest

from agentuniverse.agent.action.knowledge.embedding.openai_embedding import OpenAIEmbedding
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.chroma_store import ChromaStore
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.document import Document


class KnowledgeTest(unittest.TestCase):
    """
    Test cases for Knowledge class
    """

    def setUp(self) -> None:
        init_params = {}
        init_params['name'] = 'test_knowledge'
        init_params['description'] = 'test_knowledge_description'
        init_params['store'] = ChromaStore(collection_name="test_knowledge", embedding_model=OpenAIEmbedding(
            embedding_model_name='text-embedding-ada-002'))
        self.knowledge = Knowledge(**init_params)

    def test_store_update_documents(self) -> None:
        store = self.knowledge.store
        store.update_document([Document(text='This is an iPhone', metadata={'type': 'Electronic products'}),
                               Document(text='This is a Tesla.', metadata={'type': 'Industrial products'})])

    def test_store_upsert_documents(self) -> None:
        store = self.knowledge.store
        store.upsert_document([Document(text='This is an iPhone', metadata={'type': 'Cell phone'}),
                               Document(text='This is a Tesla.', metadata={'type': 'Car'})])

    def test_store_insert_documents(self) -> None:
        store = self.knowledge.store
        store.insert_documents([Document(text='This is a document about engineer'),
                                Document(text='This is a document about finance')])

    def test_query(self) -> None:
        store = self.knowledge.store
        query = Query(query_str='Which one is a cell phone?', similarity_top_k=1)
        res = store.query(query)
        print(res)
        self.assertIsNotNone(res)  
        self.assertGreater(len(res), 0)  
        self.assertIn('iPhone', res[0].text)


if __name__ == '__main__':
    unittest.main()
