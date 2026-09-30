# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_dashscope_reranker.py
"""Unit tests for DashscopeReranker (Dashscope API calls always stubbed)."""

from types import SimpleNamespace

import dashscope
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.\
    dashscope_reranker import DashscopeReranker, MODEL_NAME_MAP
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


class TestDashscopeReranker:
    """Offline tests: the real Dashscope rerank HTTP API is never invoked."""

    @pytest.fixture
    def reranker(self):
        return DashscopeReranker()

    @pytest.fixture
    def docs(self):
        return [Document(text=f"doc {i}", metadata={"idx": i})
                for i in range(3)]

    def test_default_attributes(self):
        reranker = DashscopeReranker()
        assert reranker.model_name == "gte_rerank"
        assert reranker.top_n == 10
        assert MODEL_NAME_MAP["gte_rerank"] == \
            dashscope.TextReRank.Models.gte_rerank

    def test_missing_or_empty_query_raises(self, reranker, docs):
        with pytest.raises(Exception, match="need an origin string query"):
            reranker._process_docs(docs)
        with pytest.raises(Exception, match="need an origin string query"):
            reranker._process_docs(docs, Query(query_str=""))

    def test_empty_docs_short_circuit_without_api_call(self, reranker,
                                                       monkeypatch):
        def forbidden_call(**kwargs):
            raise AssertionError("API must not be called for empty input")

        monkeypatch.setattr(dashscope.TextReRank, "call", forbidden_call)
        assert reranker._process_docs([], Query(query_str="q")) == []

    def test_rerank_reorders_and_records_scores(self, reranker, docs,
                                                monkeypatch):
        resp = SimpleNamespace(status_code=200, output=SimpleNamespace(results=[
            SimpleNamespace(index=2, relevance_score=0.9),
            SimpleNamespace(index=0, relevance_score=0.8),
        ]))
        captured = {}

        def fake_call(**kwargs):
            captured.update(kwargs)
            return resp

        monkeypatch.setattr(dashscope.TextReRank, "call", fake_call)
        out = reranker._process_docs(docs, Query(query_str="search"))
        assert [d.metadata["idx"] for d in out] == [2, 0]
        assert [d.metadata["relevance_score"] for d in out] == [0.9, 0.8]
        assert captured["model"] == MODEL_NAME_MAP["gte_rerank"]
        assert captured["query"] == "search"
        assert captured["documents"] == ["doc 0", "doc 1", "doc 2"]
        assert captured["top_n"] == 10
        assert captured["return_documents"] is False

    def test_top_n_limits_returned_documents(self, reranker, docs, monkeypatch):
        resp = SimpleNamespace(status_code=200, output=SimpleNamespace(results=[
            SimpleNamespace(index=1, relevance_score=0.7)]))
        monkeypatch.setattr(dashscope.TextReRank, "call", lambda **kw: resp)
        reranker.top_n = 1
        out = reranker._process_docs(docs, Query(query_str="q"))
        assert [d.metadata["idx"] for d in out] == [1]

    def test_non_ok_status_raises_api_error(self, reranker, docs, monkeypatch):
        resp = SimpleNamespace(status_code=500, output=None)
        monkeypatch.setattr(dashscope.TextReRank, "call", lambda **kw: resp)
        with pytest.raises(Exception, match="Dashscope rerank api call error"):
            reranker._process_docs(docs, Query(query_str="q"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
