#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for CohereEmbedding."""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.embedding.cohere_embedding \
    import CohereEmbedding


def _mock_response(embeddings, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = {"embeddings": {"float": embeddings}}
    resp.raise_for_status.return_value = None if status_code < 400 else Exception()
    return resp


class TestCohereEmbedding(unittest.TestCase):

    def test_get_embeddings_single(self):
        emb = CohereEmbedding(api_key="fake")
        with patch("agentuniverse.agent.action.knowledge.embedding."
                   "cohere_embedding.requests.post",
                   return_value=_mock_response([[0.1, 0.2, 0.3]])):
            result = emb.get_embeddings(["hello"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [0.1, 0.2, 0.3])

    def test_get_embeddings_multiple(self):
        emb = CohereEmbedding(api_key="fake")
        with patch("agentuniverse.agent.action.knowledge.embedding."
                   "cohere_embedding.requests.post",
                   return_value=_mock_response([[0.1], [0.2], [0.3]])):
            result = emb.get_embeddings(["a", "b", "c"])
        self.assertEqual(len(result), 3)

    def test_empty_input(self):
        emb = CohereEmbedding(api_key="fake")
        self.assertEqual(emb.get_embeddings([]), [])

    def test_missing_api_key(self):
        emb = CohereEmbedding(api_key="")
        with self.assertRaises(ValueError):
            emb.get_embeddings(["text"])

    def test_timeout_returns_empty_vectors(self):
        import requests as req_mod
        emb = CohereEmbedding(api_key="fake")
        with patch("agentuniverse.agent.action.knowledge.embedding."
                   "cohere_embedding.requests.post",
                   side_effect=req_mod.exceptions.Timeout("slow")):
            result = emb.get_embeddings(["text"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [])

    def test_http_error_raises(self):
        import requests as req_mod
        emb = CohereEmbedding(api_key="fake")
        bad_resp = MagicMock()
        bad_resp.status_code = 401
        bad_resp.raise_for_status.side_effect = req_mod.exceptions.HTTPError(
            response=bad_resp)
        with patch("agentuniverse.agent.action.knowledge.embedding."
                   "cohere_embedding.requests.post", return_value=bad_resp):
            with self.assertRaises(RuntimeError):
                emb.get_embeddings(["text"])

    def test_input_type_passed(self):
        emb = CohereEmbedding(api_key="fake", input_type="document")
        with patch("agentuniverse.agent.action.knowledge.embedding."
                   "cohere_embedding.requests.post",
                   return_value=_mock_response([[0.1]])) as mock_post:
            emb.get_embeddings(["q"], text_type="query")
            body = mock_post.call_args.kwargs["json"]
            self.assertEqual(body["input_type"], "query")

    def test_env_var_default(self):
        with patch.dict("os.environ", {"COHERE_API_KEY": "env-key"}):
            emb = CohereEmbedding()
            self.assertEqual(emb.api_key, "env-key")


if __name__ == "__main__":
    unittest.main(verbosity=2)
