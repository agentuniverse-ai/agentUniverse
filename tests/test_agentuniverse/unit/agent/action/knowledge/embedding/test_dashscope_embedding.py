# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 13:45
# @Author  : yuewang
# @FileName: test_dashscope_embedding.py
"""Unit tests for DashscopeEmbedding."""

import json
import pytest
import requests
from types import SimpleNamespace

from agentuniverse.agent.action.knowledge.embedding.dashscope_embedding import (
    DASHSCOPE_EMBEDDING_URL,
    DashscopeEmbedding,
    batched,
)


def _fake_response(payload):
    return SimpleNamespace(json=lambda: payload)


class TestBatched:
    """Test the batched helper."""

    def test_batches_of_25(self):
        inputs = list(range(55))
        chunks = list(batched(inputs))
        assert [len(c) for c in chunks] == [25, 25, 5]
        assert chunks[0] == list(range(25))

    def test_empty_input(self):
        assert list(batched([])) == []


class TestDashscopeEmbedding:
    """Test get_embeddings with a mocked HTTP layer."""

    def test_missing_api_key_raises(self):
        emb = DashscopeEmbedding(dashscope_api_key=None)
        with pytest.raises(Exception, match='No DASHSCOPE_API_KEY'):
            emb.get_embeddings(['a'])

    def test_get_embeddings_success(self, monkeypatch):
        captured = {}

        def fake_post(url=None, headers=None, data=None, timeout=None):
            captured['url'] = url
            captured['params'] = json.loads(data)
            return _fake_response({'output': {'embeddings': [
                {'text_index': 0, 'embedding': [0.1, 0.2]},
                {'text_index': 1, 'embedding': [0.3, 0.4]}]}})

        monkeypatch.setattr(requests, 'post', fake_post)
        emb = DashscopeEmbedding(dashscope_api_key='sk-x',
                                 embedding_model_name='text-embedding-v3')
        result = emb.get_embeddings(['a', 'b'])
        assert result == [[0.1, 0.2], [0.3, 0.4]]
        assert captured['url'] == DASHSCOPE_EMBEDDING_URL
        assert captured['params']['input']['texts'] == ['a', 'b']
        assert captured['params']['parameters']['dimension'] == 1024
        assert captured['params']['parameters']['text_type'] == 'document'

    def test_error_response_raises(self, monkeypatch):
        monkeypatch.setattr(requests, 'post',
                            lambda **kw: _fake_response({'code': 'Err', 'message': 'bad'}))
        emb = DashscopeEmbedding(dashscope_api_key='sk-x',
                                 embedding_model_name='text-embedding-v2')
        with pytest.raises(Exception, match='error code:Err'):
            emb.get_embeddings(['a'])
