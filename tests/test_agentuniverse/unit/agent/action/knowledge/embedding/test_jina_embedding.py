#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for the Jina AI Embedding component.

These tests mock the ``requests.post`` HTTP call so the suite can run in
CI without a live ``JINA_API_KEY``. They cover credential wiring, payload
construction, the response decoding path, batching, error handling and
the async wrapper.
"""

import asyncio
import unittest
from unittest.mock import patch, MagicMock

import requests

from agentuniverse.agent.action.knowledge.embedding.jina_embedding import (
    JINA_DEFAULT_DIMENSIONS,
    JINA_DEFAULT_EMBEDDING_MODEL,
    JINA_EMBEDDING_API_BASE,
    JinaEmbedding,
)


def _mock_response(embeddings):
    """Build a MagicMock whose .json() returns an OpenAI-style payload."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"index": i, "embedding": emb} for i, emb in enumerate(embeddings)
        ]
    }
    return mock_response


class TestJinaEmbedding(unittest.TestCase):
    """Test suite for the JinaEmbedding component."""

    def setUp(self) -> None:
        self.embedding = JinaEmbedding(
            api_key='test_api_key',
            embedding_model_name='jina-embeddings-v3',
        )

    # ---- initialization & defaults ----

    def test_initialization_defaults(self) -> None:
        """Defaults: model v3, base URL, dimensions 1024, timeout 30."""
        emb = JinaEmbedding(api_key='k')
        self.assertEqual(emb.embedding_model_name, JINA_DEFAULT_EMBEDDING_MODEL)
        self.assertEqual(emb.api_base, JINA_EMBEDDING_API_BASE)
        self.assertEqual(emb.dimensions, JINA_DEFAULT_DIMENSIONS)
        self.assertEqual(emb.request_timeout, 30)

    def test_initialization_custom(self) -> None:
        """Custom constructor values must be persisted."""
        emb = JinaEmbedding(
            api_key='k',
            embedding_model_name='jina-embeddings-v2-base-en',
            dimensions=768,
            request_timeout=10,
            batch_size=8,
        )
        self.assertEqual(emb.embedding_model_name, 'jina-embeddings-v2-base-en')
        self.assertEqual(emb.dimensions, 768)
        self.assertEqual(emb.request_timeout, 10)
        self.assertEqual(emb.batch_size, 8)

    # ---- happy path ----

    @patch('requests.post')
    def test_get_embeddings(self, mock_post) -> None:
        """get_embeddings must return vectors in input order."""
        mock_post.return_value = _mock_response([[0.1, 0.2], [0.3, 0.4]])
        result = self.embedding.get_embeddings(['hello', 'world'])
        self.assertEqual(result, [[0.1, 0.2], [0.3, 0.4]])
        # Verify the request payload and headers.
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['headers']['Authorization'], 'Bearer test_api_key')
        self.assertEqual(kwargs['headers']['Content-Type'], 'application/json')
        self.assertEqual(kwargs['json']['model'], 'jina-embeddings-v3')
        self.assertEqual(kwargs['json']['input'], ['hello', 'world'])
        self.assertEqual(kwargs['json']['dimensions'], 1024)
        self.assertEqual(kwargs['timeout'], 30)

    @patch('requests.post')
    def test_get_embeddings_batches(self, mock_post) -> None:
        """Inputs larger than batch_size must be split into multiple calls."""
        self.embedding.batch_size = 2
        mock_post.side_effect = [
            _mock_response([[1.0], [2.0]]),
            _mock_response([[3.0]]),
        ]
        result = self.embedding.get_embeddings(['a', 'b', 'c'])
        self.assertEqual(result, [[1.0], [2.0], [3.0]])
        self.assertEqual(mock_post.call_count, 2)

    @patch('requests.post')
    def test_async_get_embeddings(self, mock_post) -> None:
        """async_get_embeddings must return the same as the sync path."""
        mock_post.return_value = _mock_response([[0.5, 0.6]])
        result = asyncio.run(self.embedding.async_get_embeddings(['hi']))
        self.assertEqual(result, [[0.5, 0.6]])

    # ---- error handling ----

    def test_get_embeddings_empty_text_list(self) -> None:
        """An empty input list must raise ValueError."""
        with self.assertRaises(ValueError):
            self.embedding.get_embeddings([])

    def test_get_embeddings_no_api_key(self) -> None:
        """A missing API key must raise before any HTTP call."""
        emb = JinaEmbedding(api_key=None)
        with self.assertRaises(Exception) as ctx:
            emb.get_embeddings(['hello'])
        self.assertIn('API key is not set', str(ctx.exception))

    @patch('requests.post')
    def test_get_embeddings_http_error_is_surfaced(self, mock_post) -> None:
        """A transport/HTTP error must surface as an API call error."""
        mock_post.side_effect = requests.exceptions.Timeout('timed out')
        with self.assertRaises(Exception) as ctx:
            self.embedding.get_embeddings(['hello'])
        self.assertIn('API call error', str(ctx.exception))

    @patch('requests.post')
    def test_get_embeddings_non_json_response_is_surfaced(self, mock_post) -> None:
        """A non-JSON body must surface as a non-JSON response, not an API error."""
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b'<html>upstream error page</html>'
        mock_post.return_value = mock_response
        with self.assertRaises(Exception) as ctx:
            self.embedding.get_embeddings(['hello'])
        self.assertIn('non-JSON', str(ctx.exception))
        self.assertNotIn('API call error', str(ctx.exception))

    # ---- configer initialization & validation ----

    def _make_configer(self, extra: dict):
        from agentuniverse.base.config.component_configer.component_configer import \
            ComponentConfiger
        from agentuniverse.base.config.configer import Configer
        cfg = Configer()
        value = {
            'name': 'jina_embedding',
            'description': 'embedding use jina api',
        }
        value.update(extra)
        cfg.value = value
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def test_initialize_by_component_configer(self) -> None:
        """The configer must populate api_key, dimensions and model."""
        configer = self._make_configer({
            'api_key': 'cfg_key',
            'embedding_model_name': 'jina-embeddings-v3',
            'dimensions': 512,
        })
        emb = JinaEmbedding()
        emb._initialize_by_component_configer(configer)
        self.assertEqual(emb.api_key, 'cfg_key')
        self.assertEqual(emb.dimensions, 512)
        self.assertEqual(emb.embedding_model_name, 'jina-embeddings-v3')

    def test_initialize_rejects_invalid_request_timeout(self) -> None:
        """Non-positive / non-numeric timeouts must be rejected on init."""
        for bad in (0, -5, True, False, 'not-a-number', None):
            configer = self._make_configer({'request_timeout': bad})
            emb = JinaEmbedding()
            with self.assertRaises(Exception) as ctx:
                emb._initialize_by_component_configer(configer)
            self.assertIn('request_timeout', str(ctx.exception))

    def test_initialize_accepts_valid_request_timeout(self) -> None:
        """Positive numeric timeouts must be accepted."""
        for good in (1, 30, 5.5):
            configer = self._make_configer({'request_timeout': good})
            emb = JinaEmbedding()
            emb._initialize_by_component_configer(configer)
            self.assertEqual(emb.request_timeout, good)


if __name__ == '__main__':
    unittest.main()
