import importlib
import sys
import types
import unittest
from unittest.mock import MagicMock

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


class TestDashscopeReranker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        fake_dashscope = types.SimpleNamespace(
            TextReRank=types.SimpleNamespace(
                Models=types.SimpleNamespace(gte_rerank="gte_rerank"),
                call=MagicMock()
            )
        )
        sys.modules["dashscope"] = fake_dashscope
        module_name = (
            "agentuniverse.agent.action.knowledge.doc_processor."
            "dashscope_reranker"
        )
        cls.module = importlib.reload(importlib.import_module(module_name))

    def test_process_docs_skips_out_of_range_results(self):
        docs = [
            Document(text="first", metadata={}),
            Document(text="second", metadata={})
        ]
        self.module.dashscope.TextReRank.call.return_value = MagicMock(
            status_code=self.module.HTTPStatus.OK,
            output=MagicMock(results=[
                MagicMock(index=5, relevance_score=0.9),
                MagicMock(index=0, relevance_score=0.85),
                MagicMock(index=1, relevance_score=0.8),
                MagicMock(index=-1, relevance_score=0.7),
                MagicMock(index=None, relevance_score=0.6),
                MagicMock(index=True, relevance_score=0.5),
                MagicMock(index=False, relevance_score=0.4),
            ])
        )

        reranker = self.module.DashscopeReranker()
        reranked = reranker._process_docs(docs, Query(query_str="query"))

        self.assertEqual(len(reranked), 2)
        self.assertEqual(reranked[0].text, "first")
        self.assertEqual(reranked[0].metadata["relevance_score"], 0.85)
        self.assertEqual(reranked[1].text, "second")
        self.assertEqual(reranked[1].metadata["relevance_score"], 0.8)
