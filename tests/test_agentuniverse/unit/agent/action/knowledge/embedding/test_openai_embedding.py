# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_openai_embedding.py

"""Unit tests for OpenAIEmbedding with mocked clients."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentuniverse.agent.action.knowledge.embedding.openai_embedding import \
    OpenAIEmbedding
from agentuniverse.base.component.component_enum import ComponentEnum

MODULE = "agentuniverse.agent.action.knowledge.embedding.openai_embedding."


class FakeData:
    def __init__(self, vectors):
        self.data = [SimpleNamespace(embedding=v) for v in vectors]


class FakeBadRequestError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class TestOpenAIEmbedding:
    @pytest.fixture
    def embedding(self):
        return OpenAIEmbedding(embedding_model_name="text-embedding-3-small",
                               openai_api_key="test-key")

    def test_get_embeddings_returns_vectors(self, embedding):
        assert embedding.component_type == ComponentEnum.EMBEDDING
        client = MagicMock()
        client.embeddings.create.return_value = FakeData([[0.1, 0.2], [0.3, 0.4]])
        with patch(MODULE + "OpenAI", return_value=client):
            result = embedding.get_embeddings(["hello", "world"])
        assert result == [[0.1, 0.2], [0.3, 0.4]]
        kwargs = client.embeddings.create.call_args.kwargs
        assert kwargs == {"input": ["hello", "world"],
                          "model": "text-embedding-3-small"}

    def test_get_embeddings_passes_dimensions(self):
        emb = OpenAIEmbedding(embedding_model_name="text-embedding-3-small",
                              dimensions=1536, openai_api_key="test-key")
        client = MagicMock()
        client.embeddings.create.return_value = FakeData([[0.1]])
        with patch(MODULE + "OpenAI", return_value=client):
            emb.get_embeddings(["hello"])
        assert client.embeddings.create.call_args.kwargs["dimensions"] == 1536

    def test_missing_model_name_raises_value_error(self):
        emb = OpenAIEmbedding(openai_api_key="test-key")
        assert emb.embedding_model_name is None
        with patch(MODULE + "OpenAI", return_value=MagicMock()), \
                pytest.raises(ValueError, match="embedding_model_name"):
            emb.get_embeddings(["hello"])

    def test_bad_request_error_is_wrapped(self, embedding):
        client = MagicMock()
        client.embeddings.create.side_effect = \
            FakeBadRequestError("token limit exceeded")
        with patch(MODULE + "OpenAI", return_value=client), \
                patch(MODULE + "BadRequestError", FakeBadRequestError), \
                pytest.raises(ValueError) as exc_info:
            embedding.get_embeddings(["hello"])
        assert str(exc_info.value) == "token limit exceeded"

    def test_async_get_embeddings(self, embedding):
        client = MagicMock()
        client.embeddings.create = AsyncMock(return_value=FakeData([[0.5], [0.6]]))
        with patch(MODULE + "AsyncOpenAI", return_value=client):
            result = asyncio.run(embedding.async_get_embeddings(["a", "b"]))
        assert result == [[0.5], [0.6]]

    def test_as_langchain_uses_existing_clients(self, embedding):
        embedding.client = SimpleNamespace(embeddings="sync_emb")
        embedding.async_client = SimpleNamespace(embeddings="async_emb")
        langchain_embedding = embedding.as_langchain()
        assert langchain_embedding.openai_api_key == "test-key"
        assert langchain_embedding.client == "sync_emb"
        assert langchain_embedding.async_client == "async_emb"
