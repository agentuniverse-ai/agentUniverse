#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for CohereReranker DocProcessor."""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.doc_processor.cohere_reranker \
    import CohereReranker
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


def _mock_response(json_body, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_body
    resp.raise_for_status.return_value = None if status_code < 400 else Exception("HTTP error")
    return resp


class TestCohereReranker(unittest.TestCase):

    def _docs(self):
        return [
            Document(id="d1", text="Python is great"),
            Document(id="d2", text="Java is also good"),
            Document(id="d3", text="Rust is fast"),
        ]

    def test_rerank_reorders_by_relevance(self):
        proc = CohereReranker(api_key="fake", top_n=2)
        cohere_resp = _mock_response({
            "results": [
                {"index": 2, "relevance_score": 0.95},
                {"index": 0, "relevance_score": 0.80},
            ]
        })
        with patch("agentuniverse.agent.action.knowledge.doc_processor."
                   "cohere_reranker.requests.post", return_value=cohere_resp):
            result = proc.process_docs(self._docs(), Query(query_str="fast language"))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].text, "Rust is fast")
        self.assertEqual(result[1].text, "Python is great")
        self.assertAlmostEqual(result[0].metadata["rerank_score"], 0.95)

    def test_missing_api_key_raises(self):
        proc = CohereReranker(api_key="")
        with self.assertRaises(ValueError):
            proc.process_docs(self._docs(), Query(query_str="q"))

    def test_missing_query_returns_unchanged(self):
        proc = CohereReranker(api_key="fake")
        result = proc.process_docs(self._docs(), Query(query_str=""))
        self.assertEqual(len(result), 3)

    def test_empty_docs_returns_empty(self):
        proc = CohereReranker(api_key="fake")
        self.assertEqual(proc.process_docs([], Query(query_str="q")), [])

    def test_timeout_returns_unchanged(self):
        import requests as req_mod
        proc = CohereReranker(api_key="fake")
        with patch("agentuniverse.agent.action.knowledge.doc_processor."
                   "cohere_reranker.requests.post",
                   side_effect=req_mod.exceptions.Timeout("timed out")):
            result = proc.process_docs(self._docs(), Query(query_str="q"))
        self.assertEqual(len(result), 3)

    def test_http_error_raises_runtime_error(self):
        import requests as req_mod
        proc = CohereReranker(api_key="fake")
        bad_resp = MagicMock()
        bad_resp.status_code = 429
        bad_resp.raise_for_status.side_effect = req_mod.exceptions.HTTPError(
            response=bad_resp)
        with patch("agentuniverse.agent.action.knowledge.doc_processor."
                   "cohere_reranker.requests.post", return_value=bad_resp):
            with self.assertRaises(RuntimeError):
                proc.process_docs(self._docs(), Query(query_str="q"))

    def test_score_key_none_leaves_metadata_clean(self):
        proc = CohereReranker(api_key="fake", top_n=1, score_key=None)
        cohere_resp = _mock_response({
            "results": [{"index": 0, "relevance_score": 0.99}]
        })
        with patch("agentuniverse.agent.action.knowledge.doc_processor."
                   "cohere_reranker.requests.post", return_value=cohere_resp):
            result = proc.process_docs(self._docs(), Query(query_str="q"))
        self.assertNotIn("rerank_score", result[0].metadata or {})

    def test_top_n_capped_at_input_length(self):
        proc = CohereReranker(api_key="fake", top_n=100)
        cohere_resp = _mock_response({
            "results": [{"index": 0, "relevance_score": 0.9}]
        })
        with patch("agentuniverse.agent.action.knowledge.doc_processor."
                   "cohere_reranker.requests.post", return_value=cohere_resp):
            result = proc.process_docs(self._docs(), Query(query_str="q"))
        # top_n is capped at len(docs)=3; API returns 1, so result is 1.
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
