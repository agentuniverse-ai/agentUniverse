# !/usr/bin/env python3

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.doc_processor.voyage_reranker import (
    VoyageReranker,
    VoyageRerankerError,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class TestVoyageReranker(unittest.TestCase):
    def setUp(self):
        cfg = Configer()
        cfg.value = {
            "name": "voyage_reranker",
            "description": "reranker use voyage api",
            "api_key": "test_api_key",
            "model_name": "rerank-2.5",
            "top_n": 5,
            "truncation": True,
        }
        self.configer = ComponentConfiger()
        self.configer.load_by_configer(cfg)
        self.reranker = VoyageReranker()

        self.test_docs = [
            Document(text="Document 1", metadata={"id": 1}),
            Document(text="Document 2", metadata={"id": 2}),
            Document(text="Document 3", metadata={"id": 3}),
            Document(text="Document 4", metadata={"id": 4}),
            Document(text="Document 5", metadata={"id": 5}),
        ]

        self.test_query = Query(query_str="test query")

    def test_initialize_by_component_configer_with_env(self):
        with patch("agentuniverse.base.util.env_util.get_from_env") as mock_get_env:
            mock_get_env.return_value = "test_api_key"
            self.reranker = VoyageReranker()
            self.reranker._initialize_by_component_configer(self.configer)

            self.assertEqual(self.reranker.api_key, "test_api_key")
            self.assertEqual(self.reranker.model_name, "rerank-2.5")
            self.assertEqual(self.reranker.top_n, 5)
            self.assertEqual(self.reranker.truncation, True)

    @patch("requests.post")
    def test_process_docs(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"index": 2, "relevance_score": 0.9},
                {"index": 0, "relevance_score": 0.8},
                {"index": 4, "relevance_score": 0.7},
                {"index": 1, "relevance_score": 0.6},
                {"index": 3, "relevance_score": 0.5},
            ]
        }
        mock_post.return_value = mock_response

        self.reranker.api_key = "test_api_key"
        self.reranker.top_n = 5

        result_docs = self.reranker._process_docs(self.test_docs, self.test_query)

        mock_post.assert_called_once_with(
            "https://api.voyageai.com/v1/rerank",
            headers={"Content-Type": "application/json", "Authorization": "Bearer test_api_key"},
            json={
                "model": "rerank-2.5",
                "query": "test query",
                "documents": [doc.text for doc in self.test_docs],
                "top_k": 5,
                "truncation": True,
            },
            timeout=self.reranker.request_timeout,
        )

        self.assertEqual(len(result_docs), 5)
        self.assertEqual(result_docs[0].metadata["id"], 3)
        self.assertEqual(result_docs[0].metadata["relevance_score"], 0.9)
        self.assertEqual(result_docs[1].metadata["id"], 1)
        self.assertEqual(result_docs[1].metadata["relevance_score"], 0.8)

    @patch("requests.post")
    def test_process_docs_with_top_n(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"index": 2, "relevance_score": 0.9}, {"index": 0, "relevance_score": 0.8}]
        }
        mock_post.return_value = mock_response

        self.reranker.api_key = "test_api_key"
        self.reranker.top_n = 2

        result_docs = self.reranker._process_docs(self.test_docs, self.test_query)

        self.assertEqual(len(result_docs), 2)

    def test_process_docs_no_api_key(self):
        with self.assertRaises(VoyageRerankerError) as context:
            self.reranker._process_docs(self.test_docs, self.test_query)

        self.assertTrue("Voyage AI API key is not set" in str(context.exception))

    def test_process_docs_no_query(self):
        self.reranker.api_key = "test_api_key"
        with self.assertRaises(VoyageRerankerError) as context:
            self.reranker._process_docs(self.test_docs, None)

        self.assertTrue("Voyage AI reranker needs an origin string query" in str(context.exception))

    def test_process_docs_empty_docs(self):
        self.reranker.api_key = "test_api_key"
        result_docs = self.reranker._process_docs([], self.test_query)
        self.assertEqual(len(result_docs), 0)


if __name__ == "__main__":
    unittest.main()
