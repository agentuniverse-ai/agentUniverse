# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_cohere_rerank.py

import json
import unittest
from unittest.mock import patch, MagicMock

import httpx

from agentuniverse.agent.action.knowledge.doc_processor.cohere_rerank import \
    CohereRerank, COHERE_RERANK_API_BASE
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer

COHERE_RERANKER_MODULE = ('agentuniverse.agent.action.knowledge.'
                          'doc_processor.cohere_rerank')


def post_via_transport(transport):
    """Build an ``httpx.post`` replacement routing through a mock transport.

    The real httpx request/response pipeline keeps running (header assembly,
    JSON encoding, status handling), so the observed request shape and the
    error paths are the ones production code exercises — only the network
    is replaced.
    """

    def _post(url, **kwargs):
        with httpx.Client(transport=transport) as client:
            return client.post(url, **kwargs)

    return _post


class TestCohereRerank(unittest.TestCase):

    def setUp(self):
        self.reranker = CohereRerank()
        self.reranker.api_key = 'test_api_key'

        self.test_docs = [
            Document(text='Document 1', metadata={'id': 1}),
            Document(text='Document 2', metadata={'id': 2}),
            Document(text='Document 3', metadata={'id': 3}),
            Document(text='Document 4'),
            Document(text='Document 5', metadata={'id': 5})
        ]
        self.test_query = Query(query_str='test query')

    @staticmethod
    def success_handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode('utf-8'))
        # Rank the documents in a non-trivial order and reverse the scores.
        order = [2, 0, 4, 1, 3]
        results = [
            {'index': i, 'relevance_score': round(0.9 - 0.1 * pos, 2)}
            for pos, i in enumerate(order[:len(body['documents'])])
        ]
        return httpx.Response(200, json={'id': 'test', 'results': results,
                                         'meta': {'billed_units': {}}})

    # ------------------------------------------------------------------
    # Request shape
    # ------------------------------------------------------------------

    def test_request_shape_defaults(self):
        captured = {}

        def capture_handler(request: httpx.Request) -> httpx.Response:
            captured['request'] = request
            return httpx.Response(200, json={'results': []})

        transport = httpx.MockTransport(capture_handler)
        with patch('httpx.post', side_effect=post_via_transport(transport)) \
                as mock_post:
            self.reranker._process_docs(self.test_docs, self.test_query)

        self.assertEqual(mock_post.call_count, 1)
        self.assertEqual(mock_post.call_args.args[0], COHERE_RERANK_API_BASE)

        request = captured['request']
        self.assertEqual(str(request.url), COHERE_RERANK_API_BASE)
        self.assertEqual(request.headers['authorization'],
                         'Bearer test_api_key')
        self.assertEqual(request.headers['content-type'], 'application/json')

        body = json.loads(request.content.decode('utf-8'))
        self.assertEqual(body['model'], 'rerank-v3.5')
        self.assertEqual(body['query'], 'test query')
        self.assertEqual(body['documents'],
                         [doc.text for doc in self.test_docs])
        self.assertEqual(body['top_n'], 10)
        # Optional Cohere parameter must be omitted when unset.
        self.assertNotIn('max_chunks_per_doc', body)

    def test_request_shape_custom_options(self):
        captured = {}

        def capture_handler(request: httpx.Request) -> httpx.Response:
            captured['request'] = request
            return httpx.Response(200, json={'results': []})

        transport = httpx.MockTransport(capture_handler)
        self.reranker.model_name = 'rerank-custom'
        self.reranker.top_n = 3
        self.reranker.max_chunks_per_doc = 16

        with patch('httpx.post', side_effect=post_via_transport(transport)):
            self.reranker._process_docs(self.test_docs, self.test_query)

        body = json.loads(captured['request'].content.decode('utf-8'))
        self.assertEqual(body['model'], 'rerank-custom')
        self.assertEqual(body['top_n'], 3)
        self.assertEqual(body['max_chunks_per_doc'], 16)

    # ------------------------------------------------------------------
    # Response handling
    # ------------------------------------------------------------------

    def test_response_ordering_and_relevance_score_metadata(self):
        transport = httpx.MockTransport(self.success_handler)
        with patch('httpx.post', side_effect=post_via_transport(transport)):
            result_docs = self.reranker._process_docs(self.test_docs,
                                                      self.test_query)

        # success_handler ranks [2, 0, 4, 1, 3] with descending scores.
        self.assertEqual(len(result_docs), 5)
        self.assertEqual(result_docs[0].text, 'Document 3')
        self.assertEqual(result_docs[0].metadata['id'], 3)
        self.assertEqual(result_docs[0].metadata['relevance_score'], 0.9)
        self.assertEqual(result_docs[1].text, 'Document 1')
        self.assertEqual(result_docs[1].metadata['relevance_score'], 0.8)
        self.assertEqual(result_docs[2].text, 'Document 5')
        self.assertEqual(result_docs[2].metadata['relevance_score'], 0.7)
        self.assertEqual(result_docs[3].text, 'Document 2')
        self.assertEqual(result_docs[3].metadata['relevance_score'], 0.6)
        self.assertEqual(result_docs[4].text, 'Document 4')
        # A document without prior metadata gets a fresh metadata dict.
        self.assertEqual(result_docs[4].metadata,
                         {'relevance_score': 0.5})

    # ------------------------------------------------------------------
    # API key handling
    # ------------------------------------------------------------------

    def test_missing_api_key_raises_clear_error(self):
        reranker = CohereRerank()
        reranker.api_key = None
        with patch('httpx.post') as mock_post:
            with self.assertRaises(Exception) as context:
                reranker._process_docs(self.test_docs, self.test_query)
        self.assertIn('COHERE_API_KEY', str(context.exception))
        mock_post.assert_not_called()

    def test_empty_string_api_key_is_never_sent(self):
        # A placeholder like COHERE_API_KEY="" must fail loudly at call
        # time instead of being sent to the API as a bearer token.
        reranker = CohereRerank()
        reranker.api_key = ''
        with patch('httpx.post') as mock_post:
            with self.assertRaises(Exception) as context:
                reranker._process_docs(self.test_docs, self.test_query)
        self.assertIn('empty value', str(context.exception))
        self.assertIn('COHERE_API_KEY', str(context.exception))
        mock_post.assert_not_called()

    def test_whitespace_api_key_is_rejected(self):
        reranker = CohereRerank()
        reranker.api_key = '   '
        with patch('httpx.post') as mock_post:
            with self.assertRaises(Exception):
                reranker._process_docs(self.test_docs, self.test_query)
        mock_post.assert_not_called()

    # ------------------------------------------------------------------
    # Error paths
    # ------------------------------------------------------------------

    def test_http_error_is_structured(self):
        transport = httpx.MockTransport(
            lambda request: httpx.Response(
                401, json={'message': 'invalid api token'})
        )
        with patch('httpx.post', side_effect=post_via_transport(transport)):
            with self.assertRaises(Exception) as context:
                self.reranker._process_docs(self.test_docs, self.test_query)
        message = str(context.exception)
        self.assertIn('HTTP 401', message)
        self.assertIn('invalid api token', message)

    def test_timeout_error_is_surfaced(self):
        def timeout_handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout('timed out')

        transport = httpx.MockTransport(timeout_handler)
        with patch('httpx.post', side_effect=post_via_transport(transport)):
            with self.assertRaises(Exception) as context:
                self.reranker._process_docs(self.test_docs, self.test_query)
        self.assertIn('Cohere rerank API call error', str(context.exception))

    def test_connect_error_is_surfaced(self):
        def connect_handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError('connection refused')

        transport = httpx.MockTransport(connect_handler)
        with patch('httpx.post', side_effect=post_via_transport(transport)):
            with self.assertRaises(Exception) as context:
                self.reranker._process_docs(self.test_docs, self.test_query)
        self.assertIn('Cohere rerank API call error', str(context.exception))

    def test_non_json_response_is_surfaced(self):
        transport = httpx.MockTransport(
            lambda request: httpx.Response(
                200, text='<html>upstream error page</html>')
        )
        with patch('httpx.post', side_effect=post_via_transport(transport)):
            with self.assertRaises(Exception) as context:
                self.reranker._process_docs(self.test_docs, self.test_query)
        message = str(context.exception)
        self.assertIn('non-JSON', message)
        self.assertNotIn('API call error', message)

    # ------------------------------------------------------------------
    # Degenerate-input passthrough
    # ------------------------------------------------------------------

    def test_empty_docs_passthrough(self):
        with patch('httpx.post') as mock_post:
            result_docs = self.reranker._process_docs([], self.test_query)
        self.assertEqual(result_docs, [])
        mock_post.assert_not_called()

    def test_empty_query_passthrough(self):
        for query in (None, Query(query_str='')):
            with patch('httpx.post') as mock_post:
                result_docs = self.reranker._process_docs(
                    self.test_docs, query)
            self.assertEqual(result_docs, self.test_docs)
            self.assertEqual([doc.text for doc in result_docs],
                             [doc.text for doc in self.test_docs])
            mock_post.assert_not_called()

    # ------------------------------------------------------------------
    # Component configer initialization
    # ------------------------------------------------------------------

    def test_initialize_by_component_configer(self):
        cfg = Configer()
        cfg.value = {
            'name': 'cohere_rerank',
            'description': 'reranker use cohere api',
            'api_key': 'yaml_api_key',
            'model_name': 'yaml_model',
            'top_n': 5,
            'max_chunks_per_doc': 64,
            'request_timeout': 12
        }
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)

        reranker = CohereRerank()
        reranker.api_key = None
        reranker._initialize_by_component_configer(configer)

        self.assertEqual(reranker.name, 'cohere_rerank')
        self.assertEqual(reranker.api_key, 'yaml_api_key')
        self.assertEqual(reranker.model_name, 'yaml_model')
        self.assertEqual(reranker.top_n, 5)
        self.assertEqual(reranker.max_chunks_per_doc, 64)
        self.assertEqual(reranker.request_timeout, 12)

    def test_initialize_by_component_configer_env_fallback(self):
        cfg = Configer()
        cfg.value = {
            'name': 'cohere_rerank',
            'description': 'reranker use cohere api'
        }
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)

        reranker = CohereRerank()
        with patch(f'{COHERE_RERANKER_MODULE}.get_from_env') as mock_env:
            mock_env.return_value = 'env_api_key'
            reranker._initialize_by_component_configer(configer)
            mock_env.assert_called_once_with('COHERE_API_KEY')
        self.assertEqual(reranker.api_key, 'env_api_key')
        # Class defaults remain untouched when the yaml omits them.
        self.assertEqual(reranker.model_name, 'rerank-v3.5')
        self.assertEqual(reranker.top_n, 10)
        self.assertIsNone(reranker.max_chunks_per_doc)
        self.assertEqual(reranker.request_timeout, 30)

    def test_api_key_env_default_factory(self):
        reranker = CohereRerank()
        self.assertEqual(reranker.model_name, 'rerank-v3.5')
        self.assertEqual(reranker.top_n, 10)
        self.assertIsNone(reranker.max_chunks_per_doc)
        self.assertEqual(reranker.request_timeout, 30)

    def test_api_key_env_default_factory_reads_env(self):
        with patch.dict('os.environ', {'COHERE_API_KEY': 'env_value'}):
            reranker = CohereRerank()
            self.assertEqual(reranker.api_key, 'env_value')
        with patch.dict('os.environ', {}, clear=False):
            import os
            os.environ.pop('COHERE_API_KEY', None)
            reranker = CohereRerank()
            self.assertIsNone(reranker.api_key)


if __name__ == '__main__':
    unittest.main()
