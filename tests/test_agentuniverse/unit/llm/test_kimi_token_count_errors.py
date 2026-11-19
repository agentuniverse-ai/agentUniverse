# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""The Kimi token counter must survive an error payload and always send a timeout."""

import pytest

from agentuniverse.llm.default import kimi_openai_style_llm as kimi


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _make_llm():
    llm = kimi.KIMIOpenAIStyleLLM.__new__(kimi.KIMIOpenAIStyleLLM)
    object.__setattr__(llm, "api_base", "https://example.invalid")
    object.__setattr__(llm, "api_key", "test-key")
    object.__setattr__(llm, "model_name", "kimi-test")
    return llm


def test_error_payload_does_not_raise(monkeypatch):
    # No 'data' key: chaining .get('data').get(...) used to raise AttributeError.
    monkeypatch.setattr(kimi.requests, "post", lambda *a, **k: _FakeResponse({"error": "bad"}))
    assert _make_llm().get_num_tokens("hello") == 0


def test_missing_total_tokens_defaults_to_zero(monkeypatch):
    monkeypatch.setattr(kimi.requests, "post", lambda *a, **k: _FakeResponse({"data": {}}))
    assert _make_llm().get_num_tokens("hello") == 0


def test_happy_path_is_unchanged(monkeypatch):
    monkeypatch.setattr(kimi.requests, "post", lambda *a, **k: _FakeResponse({"data": {"total_tokens": 42}}))
    assert _make_llm().get_num_tokens("hello") == 42


def test_request_always_carries_a_timeout(monkeypatch):
    seen = {}

    def capture(*args, **kwargs):
        seen.update(kwargs)
        return _FakeResponse({"data": {"total_tokens": 7}})

    monkeypatch.setattr(kimi.requests, "post", capture)
    assert _make_llm().get_num_tokens("hello") == 7
    # requests waits forever without a timeout, which can hang an agent run.
    assert seen.get("timeout") is not None
