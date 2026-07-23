# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: test_voyage_reranker.py

import unittest
from unittest.mock import patch, MagicMock

import requests

from agentuniverse.agent.action.knowledge.doc_processor.voyage_reranker \
    import VoyageReranker
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer \
    import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class TestVoyageReranker(unittest.TestCase):

    def setUp(self):
        cfg = Configer()
        cfg.value = {
            'name': 'voyage_reranker',
            'description': 'reranker use voyage ai api',
            'api_key': 'test_api_key',
            'model_name': 'rerank-2',
            'top_n': 5,
        }
        self.configer = ComponentConfiger()
        self.configer.load_by_configer(cfg)
        self.reranker = VoyageReranker()

        self.test_docs = [
            Document(text='Document 1', metadata={'id': 1}),
            Document(text='Document 2', metadata={'id': 2}),
            Document(text='Document 3', metadata={'id': 3}),
            Document(text='Document 4', metadata={'id': 4}),
            Document(text='Document 5', metadata={'id': 5}),
        ]
        self.test_query = Query(query_str='test query')

    def test_initialize_by_component_configer_with_env(self):
        with patch('agentuniverse.base.util.env_util.get_from_env') \
                as mock_get_env:
            mock_get_env.return_value = 'env_key'
            self.reranker = VoyageReranker()
            self.reranker._initialize_by_component_configer(self.configer)

            self.assertEqual(self.reranker.api_key, 'test_api_key')
            self.assertEqual(self.reranker.model_name, 'rerank-2')
            self.assertEqual(self.reranker.top_n, 5)

    @patch('agentuniverse.agent.action.knowledge.doc_processor.'
           'voyage_reranker.requests.post')
    def test_process_docs(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': [
                {'index': 2, 'relevance_score': 0.9},
                {'index': 0, 'relevance_score': 0.8},
                {'index': 4, 'relevance_score': 0.7},
                {'index': 1, 'relevance_score': 0.6},
                {'index': 3, 'relevance_score': 0.5},
            ]
        }
        mock_post.return_value = mock_response

        self.reranker.api_key = 'test_api_key'
        result_docs = self.reranker._process_docs(
            self.test_docs, self.test_query)

        mock_post.assert_called_once_with(
            'https://api.voyageai.com/v1/rerank',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer test_api_key',
            },
            json={
                'model': 'rerank-2',
                'query': 'test query',
                'documents': [doc.text for doc in self.test_docs],
                'top_k': 5,
                'return_documents': False,
                'truncation': True,
            },
            timeout=30,
        )

        self.assertEqual(len(result_docs), 5)
        # results come back pre-sorted by relevance
        self.assertEqual(result_docs[0].metadata['id'], 3)
        self.assertEqual(result_docs[0].metadata['rerank_score'], 0.9)
        self.assertEqual(result_docs[1].metadata['id'], 1)
        self.assertEqual(result_docs[1].metadata['rerank_score'], 0.8)
        # original metadata is preserved alongside the stamped score
        self.assertEqual(result_docs[2].metadata['id'], 5)

    @patch('agentuniverse.agent.action.knowledge.doc_processor.'
           'voyage_reranker.requests.post')
    def test_process_docs_top_n_capped_to_doc_count(self, mock_post):
        # top_n larger than the number of docs must be capped so the API is
        # never asked for more results than exist.
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': [
                {'index': 1, 'relevance_score': 0.9},
                {'index': 0, 'relevance_score': 0.8},
            ]
        }
        mock_post.return_value = mock_response

        self.reranker.api_key = 'test_api_key'
        self.reranker.top_n = 10
        small_docs = [self.test_docs[0], self.test_docs[1]]

        result_docs = self.reranker._process_docs(small_docs, self.test_query)

        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['top_k'], 2)
        self.assertEqual(len(result_docs), 2)

    def test_process_docs_no_api_key(self):
        with self.assertRaises(Exception) as context:
            self.reranker._process_docs(self.test_docs, self.test_query)
        self.assertIn('Voyage AI API key is not set', str(context.exception))

    def test_process_docs_no_query(self):
        self.reranker.api_key = 'test_api_key'
        with self.assertRaises(Exception) as context:
            self.reranker._process_docs(self.test_docs, None)
        self.assertIn('needs an origin string query', str(context.exception))

    def test_process_docs_no_docs(self):
        self.reranker.api_key = 'test_api_key'
        result_docs = self.reranker._process_docs([], self.test_query)
        self.assertEqual(len(result_docs), 0)

    @patch('agentuniverse.agent.action.knowledge.doc_processor.'
           'voyage_reranker.requests.post')
    def test_process_docs_timeout_error_is_surfaced(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout('timed out')
        self.reranker.api_key = 'test_api_key'
        with self.assertRaises(Exception) as context:
            self.reranker._process_docs(self.test_docs, self.test_query)
        self.assertIn('Voyage AI rerank API call error', str(context.exception))

    @patch('agentuniverse.agent.action.knowledge.doc_processor.'
           'voyage_reranker.requests.post')
    def test_process_docs_non_json_response_is_surfaced(self, mock_post):
        # Use a real Response whose .json() raises
        # requests.exceptions.JSONDecodeError — the actual exception a
        # non-JSON body produces. JSONDecodeError inherits from BOTH
        # RequestException and ValueError, so a naive except-ordering would
        # misreport it as an API-call error; this test pins the non-JSON
        # path.
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b'<html>upstream error page</html>'
        mock_post.return_value = mock_response
        self.reranker.api_key = 'test_api_key'
        with self.assertRaises(Exception) as context:
            self.reranker._process_docs(self.test_docs, self.test_query)
        self.assertIn('non-JSON', str(context.exception))
        self.assertNotIn('API call error', str(context.exception))

    @patch('agentuniverse.agent.action.knowledge.doc_processor.'
           'voyage_reranker.requests.post')
    def test_process_docs_skips_out_of_range_index(self, mock_post):
        # An out-of-range index must be skipped rather than crash the rerank.
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': [
                {'index': 0, 'relevance_score': 0.9},
                {'index': 99, 'relevance_score': 0.8},
                {'index': 'oops', 'relevance_score': 0.7},
            ]
        }
        mock_post.return_value = mock_response

        self.reranker.api_key = 'test_api_key'
        result_docs = self.reranker._process_docs(
            self.test_docs, self.test_query)
        self.assertEqual(len(result_docs), 1)
        self.assertEqual(result_docs[0].metadata['rerank_score'], 0.9)

    @patch('agentuniverse.agent.action.knowledge.doc_processor.'
           'voyage_reranker.requests.post')
    def test_process_docs_custom_score_key(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': [
                {'index': 0, 'relevance_score': 0.9},
            ]
        }
        mock_post.return_value = mock_response

        self.reranker.api_key = 'test_api_key'
        self.reranker.score_key = 'voyage_relevance'
        result_docs = self.reranker._process_docs(
            [self.test_docs[0]], self.test_query)
        self.assertIn('voyage_relevance', result_docs[0].metadata)
        self.assertNotIn('rerank_score', result_docs[0].metadata)

    def _make_configer_with_timeout(self, request_timeout):
        cfg = Configer()
        cfg.value = {
            'name': 'voyage_reranker',
            'description': 'reranker use voyage ai api',
            'request_timeout': request_timeout,
        }
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def test_initialize_rejects_non_numeric_request_timeout(self):
        for bad in ('not-a-number', None, [30]):
            reranker = VoyageReranker()
            with self.assertRaises(Exception) as context:
                reranker._initialize_by_component_configer(
                    self._make_configer_with_timeout(bad))
            self.assertIn('request_timeout', str(context.exception))

    def test_initialize_rejects_non_positive_request_timeout(self):
        # 0 / negative are invalid; True/False are bools (an int subclass)
        # and must also be rejected so a YAML `true` does not become 1.
        for bad in (0, -5, True, False):
            reranker = VoyageReranker()
            with self.assertRaises(Exception) as context:
                reranker._initialize_by_component_configer(
                    self._make_configer_with_timeout(bad))
            self.assertIn('request_timeout', str(context.exception))

    def test_initialize_accepts_valid_request_timeout(self):
        for good in (1, 30, 5.5):
            reranker = VoyageReranker()
            reranker._initialize_by_component_configer(
                self._make_configer_with_timeout(good))
            self.assertEqual(reranker.request_timeout, good)


if __name__ == '__main__':
    unittest.main()
