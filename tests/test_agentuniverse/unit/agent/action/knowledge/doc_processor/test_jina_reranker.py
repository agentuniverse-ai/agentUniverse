# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/8/10 23:00
# @Author  : xmhu2001
# @Email   : xmhu2001@qq.com
# @FileName: test_jina_reranker.py

import unittest
from unittest.mock import patch, MagicMock

from agentuniverse.agent.action.knowledge.doc_processor.jina_reranker import JinaReranker
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class TestJinaReranker(unittest.TestCase):

    def setUp(self):
        cfg = Configer()
        cfg.value = {
            'name': 'jina_reranker',
            'description': 'reranker use jina api',
            'api_key': 'test_api_key',
            'model_name': 'test_model',
            'top_n': 5
        }
        self.configer = ComponentConfiger()
        self.configer.load_by_configer(cfg)
        self.reranker = JinaReranker()

        self.test_docs = [
            Document(text='Document 1', metadata={'id': 1}),
            Document(text='Document 2', metadata={'id': 2}),
            Document(text='Document 3', metadata={'id': 3}),
            Document(text='Document 4', metadata={'id': 4}),
            Document(text='Document 5', metadata={'id': 5})
        ]

        self.test_query = Query(query_str='test query')

    def test_initialize_by_component_configer_with_env(self):
        with patch('agentuniverse.base.util.env_util.get_from_env') as mock_get_env:
            mock_get_env.return_value = 'test_api_key'
            self.reranker = JinaReranker()
            self.reranker._initialize_by_component_configer(self.configer)

            self.assertEqual(self.reranker.api_key, 'test_api_key')
            self.assertEqual(self.reranker.model_name, 'test_model')
            self.assertEqual(self.reranker.top_n, 5)

    @patch('requests.post')
    def test_process_docs(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [
                {'index': 2, 'relevance_score': 0.9},
                {'index': 0, 'relevance_score': 0.8},
                {'index': 4, 'relevance_score': 0.7},
                {'index': 1, 'relevance_score': 0.6},
                {'index': 3, 'relevance_score': 0.5}
            ]
        }
        mock_post.return_value = mock_response

        self.reranker.api_key = 'test_api_key'

        result_docs = self.reranker._process_docs(self.test_docs, self.test_query)

        mock_post.assert_called_once_with(
            'https://api.jina.ai/v1/rerank  ',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer test_api_key'
            },
            json={
                'model': 'jina-reranker-v2-base-multilingual',
                'query': 'test query',
                'documents': [doc.text for doc in self.test_docs]
            }
        )

        self.assertEqual(len(result_docs), 5)
        self.assertEqual(result_docs[0].metadata['id'], 3)
        self.assertEqual(result_docs[0].metadata['relevance_score'], 0.9)
        self.assertEqual(result_docs[1].metadata['id'], 1)
        self.assertEqual(result_docs[1].metadata['relevance_score'], 0.8)

    @patch('requests.post')
    def test_process_docs_with_top_n(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [
                {'index': 2, 'relevance_score': 0.9},
                {'index': 0, 'relevance_score': 0.8}
            ]
        }
        mock_post.return_value = mock_response

        self.reranker.api_key = 'test_api_key'
        self.reranker.top_n = 2

        result_docs = self.reranker._process_docs(self.test_docs, self.test_query)

        mock_post.assert_called_once_with(
            'https://api.jina.ai/v1/rerank  ',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer test_api_key'
            },
            json={
                'model': 'jina-reranker-v2-base-multilingual',
                'query': 'test query',
                'documents': [doc.text for doc in self.test_docs],
                'top_n': 2
            }
        )

        self.assertEqual(len(result_docs), 2)

    def test_process_docs_no_api_key(self):
        with self.assertRaises(Exception) as context:
            self.reranker._process_docs(self.test_docs, self.test_query)

        self.assertTrue('Jina AI API key is not set' in str(context.exception))

    def test_process_docs_no_docs(self):
        self.reranker.api_key = 'test_api_key'
        result_docs = self.reranker._process_docs([], self.test_query)
        self.assertEqual(len(result_docs), 0)

if __name__ == '__main__':
    unittest.main()