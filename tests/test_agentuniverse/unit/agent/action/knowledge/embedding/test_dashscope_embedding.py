# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_dashscope_embedding.py

"""Unit tests for DashscopeEmbedding with the network fully mocked."""

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentuniverse.agent.action.knowledge.embedding.dashscope_embedding \
    import DASHSCOPE_EMBEDDING_URL, DASHSCOPE_MAX_BATCH_SIZE, \
    DashscopeEmbedding, batched

POST_PATH = ("agentuniverse.agent.action.knowledge.embedding."
             "dashscope_embedding.requests.post")


def payload_for(vectors):
    return {"output": {"embeddings": [{"embedding": v} for v in vectors]}}


def fake_post(calls, payload):
    def respond(url=None, headers=None, data=None, timeout=None):
        calls.append({"url": url, "headers": headers,
                      "data": json.loads(data.decode("utf-8"))})
        response = MagicMock()
        response.json.return_value = payload
        return response
    return respond


class TestDashscopeEmbedding:
    @pytest.fixture
    def embedding(self):
        return DashscopeEmbedding(embedding_model_name="text-embedding-v2",
                                  dashscope_api_key="test-key")

    def test_batched_splits_input(self):
        assert [list(b) for b in batched(list(range(7)), 3)] == \
            [[0, 1, 2], [3, 4, 5], [6]]
        assert list(batched([])) == []
        sizes = [len(b) for b in batched(list(range(60)))]
        assert sizes == [DASHSCOPE_MAX_BATCH_SIZE,
                         DASHSCOPE_MAX_BATCH_SIZE, 10]

    def test_get_embeddings_success(self, embedding):
        calls = []
        with patch(POST_PATH, side_effect=fake_post(
                calls, payload_for([[0.1, 0.2], [0.3, 0.4]]))):
            result = embedding.get_embeddings(["a", "b"])
        assert result == [[0.1, 0.2], [0.3, 0.4]]
        assert calls[0]["url"] == DASHSCOPE_EMBEDDING_URL
        assert calls[0]["headers"]["Authorization"] == "Bearer test-key"
        assert calls[0]["data"] == {"model": "text-embedding-v2",
                                    "input": {"texts": ["a", "b"]},
                                    "parameters": {"text_type": "document"}}

    def test_text_embedding_v3_parameters(self):
        emb = DashscopeEmbedding(embedding_model_name="text-embedding-v3",
                                 embedding_dims=512, dashscope_api_key="k")
        calls = []
        with patch(POST_PATH, side_effect=fake_post(
                calls, payload_for([[0.1]]))):
            emb.get_embeddings(["a"], output_type="binary", text_type="query")
        assert calls[0]["data"]["parameters"] == {
            "dimension": 512, "output_type": "binary", "text_type": "query"}

    def test_error_response_raises_exception(self, embedding):
        calls = []
        with patch(POST_PATH, side_effect=fake_post(
                calls, {"code": "Throttling", "message": "rate limited"})):
            with pytest.raises(Exception) as exc_info:
                embedding.get_embeddings(["a"])
        assert "Throttling" in str(exc_info.value)
        assert "rate limited" in str(exc_info.value)

    def test_missing_api_key_raises_exception(self):
        emb = DashscopeEmbedding(embedding_model_name="text-embedding-v2",
                                 dashscope_api_key=None)
        with pytest.raises(Exception, match="DASHSCOPE_API_KEY"):
            emb.get_embeddings(["a"])

    def test_async_get_embeddings(self, embedding):
        response = MagicMock()
        response.__aenter__ = AsyncMock(return_value=response)
        response.__aexit__ = AsyncMock(return_value=False)
        response.json = AsyncMock(return_value=payload_for([[0.1], [0.2]]))
        session = MagicMock()
        session.post = AsyncMock(return_value=response)
        client_session = MagicMock()
        client_session.__aenter__ = AsyncMock(return_value=session)
        client_session.__aexit__ = AsyncMock(return_value=False)
        with patch("agentuniverse.agent.action.knowledge.embedding."
                   "dashscope_embedding.aiohttp",
                   SimpleNamespace(ClientSession=lambda: client_session)):
            result = asyncio.run(embedding.async_get_embeddings(["a", "b"]))
        assert result == [[0.1], [0.2]]
