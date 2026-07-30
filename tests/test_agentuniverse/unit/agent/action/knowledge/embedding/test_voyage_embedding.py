# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: test_voyage_embedding.py

import asyncio
import unittest
from unittest.mock import patch, MagicMock

import requests

from agentuniverse.agent.action.knowledge.embedding.voyage_embedding import \
    VoyageEmbedding
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _mock_response(payload, status_code=200):
    """Build a MagicMock response carrying ``payload`` and a status code."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload

    def _raise_for_status():
        if status_code >= 400:
            raise requests.exceptions.HTTPError(
                f"{status_code} error", response=resp)

    resp.raise_for_status = _raise_for_status
    return resp


class TestVoyageEmbedding(unittest.TestCase):
    """Unit tests for the VoyageEmbedding component (mocks requests)."""

    def setUp(self):
        self.embedding = VoyageEmbedding(
            embedding_model_name='voyage-3',
            embedding_dims=1024,
            api_key='test_api_key',
        )
        self.sample_payload = {
            'data': [
                {'embedding': [0.1, 0.2, 0.3]},
                {'embedding': [0.4, 0.5, 0.6]},
            ]
        }

    # 1. happy-path sync embed
    @patch('agentuniverse.agent.action.knowledge.embedding.'
           'voyage_embedding.requests.post')
    def test_get_embeddings_returns_vectors(self, mock_post):
        mock_post.return_value = _mock_response(self.sample_payload)

        result = self.embedding.get_embeddings(['hello', 'world'])

        self.assertEqual(result, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['model'], 'voyage-3')
        self.assertEqual(kwargs['json']['inputs'], ['hello', 'world'])
        self.assertEqual(kwargs['json']['input_type'], 'document')
        self.assertEqual(kwargs['timeout'], 30)
        self.assertEqual(kwargs['headers']['Authorization'],
                         'Bearer test_api_key')

    # 2. empty input short-circuits without an HTTP call
    @patch('agentuniverse.agent.action.knowledge.embedding.'
           'voyage_embedding.requests.post')
    def test_get_embeddings_empty_input(self, mock_post):
        self.assertEqual(self.embedding.get_embeddings([]), [])
        mock_post.assert_not_called()

    # 3. input_type override per call
    @patch('agentuniverse.agent.action.knowledge.embedding.'
           'voyage_embedding.requests.post')
    def test_get_embeddings_input_type_override(self, mock_post):
        mock_post.return_value = _mock_response(self.sample_payload)

        self.embedding.get_embeddings(['q'], input_type='query')

        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['input_type'], 'query')

    # 4. invalid per-call input_type falls back to component default
    @patch('agentuniverse.agent.action.knowledge.embedding.'
           'voyage_embedding.requests.post')
    def test_get_embeddings_invalid_input_type_falls_back(self, mock_post):
        mock_post.return_value = _mock_response(self.sample_payload)

        self.embedding.get_embeddings(['q'], input_type='weird')

        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['input_type'], 'document')

    # 5. missing api_key raises ValueError
    def test_get_embeddings_missing_api_key(self):
        emb = VoyageEmbedding(api_key=None)
        with self.assertRaises(ValueError) as ctx:
            emb.get_embeddings(['hello'])
        self.assertIn('api_key', str(ctx.exception))

    # 6. timeout returns empty vectors instead of raising
    @patch('agentuniverse.agent.action.knowledge.embedding.'
           'voyage_embedding.requests.post')
    def test_get_embeddings_timeout_returns_empty_vectors(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout('timed out')

        result = self.embedding.get_embeddings(['a', 'b'])

        self.assertEqual(result, [[], []])

    # 7. HTTP error surfaces as RuntimeError
    @patch('agentuniverse.agent.action.knowledge.embedding.'
           'voyage_embedding.requests.post')
    def test_get_embeddings_http_error(self, mock_post):
        mock_post.return_value = _mock_response({}, status_code=500)

        with self.assertRaises(RuntimeError) as ctx:
            self.embedding.get_embeddings(['a'])
        self.assertIn('500', str(ctx.exception))

    # 8. non-JSON body surfaces as RuntimeError
    @patch('agentuniverse.agent.action.knowledge.embedding.'
           'voyage_embedding.requests.post')
    def test_get_embeddings_non_json_response(self, mock_post):
        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        resp.json.side_effect = ValueError('not json')
        mock_post.return_value = resp

        with self.assertRaises(RuntimeError) as ctx:
            self.embedding.get_embeddings(['a'])
        self.assertIn('non-JSON', str(ctx.exception))

    # 9. async wraps sync
    @patch('agentuniverse.agent.action.knowledge.embedding.'
           'voyage_embedding.requests.post')
    def test_async_get_embeddings(self, mock_post):
        mock_post.return_value = _mock_response(self.sample_payload)

        result = asyncio.run(
            self.embedding.async_get_embeddings(['hello', 'world']))

        self.assertEqual(result, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

    # 10. langchain adapter
    @patch('agentuniverse.agent.action.knowledge.embedding.'
           'voyage_embedding.requests.post')
    def test_as_langchain(self, mock_post):
        mock_post.return_value = _mock_response(self.sample_payload)

        lc = self.embedding.as_langchain()
        docs = lc.embed_documents(['a', 'b'])
        query = lc.embed_query('q')

        self.assertEqual(docs, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        self.assertEqual(query, [0.1, 0.2, 0.3])
        # embed_documents -> input_type document, embed_query -> query
        types = [c.kwargs['json']['input_type']
                 for c in mock_post.call_args_list]
        self.assertEqual(types, ['document', 'query'])

    # 11. configer initialization
    def test_initialize_by_component_configer(self):
        cfg = Configer()
        cfg.value = {
            'name': 'voyage_embedding',
            'description': 'voyage embedding',
            'embedding_model_name': 'voyage-large-2',
            'input_type': 'query',
            'request_timeout': 12,
        }
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)

        emb = VoyageEmbedding()
        with patch('agentuniverse.base.util.env_util.get_from_env') \
                as mock_env:
            mock_env.return_value = 'env_key'
            emb._initialize_by_component_configer(configer)

        self.assertEqual(emb.name, 'voyage_embedding')
        self.assertEqual(emb.embedding_model_name, 'voyage-large-2')
        self.assertEqual(emb.input_type, 'query')
        self.assertEqual(emb.request_timeout, 12)

    # 12. invalid request_timeout rejected at init
    def test_initialize_rejects_invalid_request_timeout(self):
        for bad in (-1, 0, True, 'oops', None):
            cfg = Configer()
            cfg.value = {
                'name': 'voyage_embedding',
                'description': 'voyage embedding',
                'request_timeout': bad,
            }
            configer = ComponentConfiger()
            configer.load_by_configer(cfg)

            emb = VoyageEmbedding()
            with self.assertRaises(ValueError) as ctx:
                emb._initialize_by_component_configer(configer)
            self.assertIn('request_timeout', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
