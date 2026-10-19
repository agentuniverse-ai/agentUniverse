# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 13:50
# @Author  : yuewang
# @FileName: test_openai_embedding.py
"""Unit tests for OpenAIEmbedding."""

import pytest
from types import SimpleNamespace

import agentuniverse.agent.action.knowledge.embedding.openai_embedding as oe
from agentuniverse.agent.action.knowledge.embedding.openai_embedding import OpenAIEmbedding


def _fake_openai_cls(create_kwargs_holder):
    """Build a fake OpenAI client factory capturing create kwargs."""

    def create(input=None, model=None, dimensions=None, **kw):
        create_kwargs_holder['kwargs'] = {'input': input, 'model': model,
                                          'dimensions': dimensions}
        return SimpleNamespace(data=[
            SimpleNamespace(embedding=[0.1]), SimpleNamespace(embedding=[0.2])])

    class _Client:
        def __init__(self, api_key=None, **kw):
            self.api_key = api_key
            self.embeddings = SimpleNamespace(create=create)

    return _Client


class TestOpenAIEmbedding:
    """Test OpenAIEmbedding with a mocked client."""

    def test_missing_model_name_raises(self, monkeypatch):
        holder = {}
        monkeypatch.setattr(oe, 'OpenAI', _fake_openai_cls(holder))
        emb = OpenAIEmbedding(openai_api_key='sk-x', embedding_model_name=None)
        with pytest.raises(ValueError, match='embedding_model_name'):
            emb.get_embeddings(['a'])

    def test_get_embeddings(self, monkeypatch):
        holder = {}
        monkeypatch.setattr(oe, 'OpenAI', _fake_openai_cls(holder))
        emb = OpenAIEmbedding(openai_api_key='sk-x',
                              embedding_model_name='text-embedding-3-small')
        result = emb.get_embeddings(['a', 'b'])
        assert result == [[0.1], [0.2]]
        assert holder['kwargs']['model'] == 'text-embedding-3-small'
        assert holder['kwargs']['input'] == ['a', 'b']
        assert holder['kwargs']['dimensions'] is None

    def test_get_embeddings_with_dimensions(self, monkeypatch):
        holder = {}
        monkeypatch.setattr(oe, 'OpenAI', _fake_openai_cls(holder))
        emb = OpenAIEmbedding(openai_api_key='sk-x',
                              embedding_model_name='text-embedding-3-small',
                              dimensions=64)
        emb.get_embeddings(['a'])
        assert holder['kwargs']['dimensions'] == 64

    def test_as_langchain(self):
        emb = OpenAIEmbedding(openai_api_key='sk-x',
                              embedding_model_name='text-embedding-3-small')
        lc = emb.as_langchain()
        assert lc is not None
