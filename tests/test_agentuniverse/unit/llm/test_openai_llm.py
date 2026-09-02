# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_openai_llm.py
"""Unit tests for pure OpenAILLM helpers (no network access)."""

import asyncio

import pytest

from agentuniverse.llm.openai_llm import OpenAILLM


class FakeChunk:
    """Mimic an OpenAI chat completion chunk with dict()/model_dump()."""

    def __init__(self, payload):
        self.payload = payload

    def dict(self):
        return self.payload

    def model_dump(self):
        return self.payload


@pytest.fixture
def llm():
    """Create an OpenAILLM instance with a dummy key for offline tests."""
    return OpenAILLM(model_name="gpt-4o", openai_api_key="test-key")


class TestOpenAILLM:
    """Test deterministic OpenAILLM behavior."""

    def test_max_context_length_of_known_model(self, llm):
        assert llm.max_context_length() == 128000

    def test_max_context_length_fallback_for_unknown_model(self):
        assert OpenAILLM(model_name="unknown-model").max_context_length() == 4096

    def test_get_num_tokens(self, llm):
        assert llm.get_num_tokens("hello world") == 2

    def test_parse_result_returns_llm_output(self):
        chunk = FakeChunk({"choices": [{"delta": {"role": "assistant", "content": "Hi"}}]})
        result = OpenAILLM.parse_result(chunk)
        assert result is not None
        assert result.text == "Hi"

    def test_parse_result_empty_choices_returns_none(self):
        chunk = FakeChunk({"choices": []})
        assert OpenAILLM.parse_result(chunk) is None

    def test_parse_result_missing_content_returns_none(self):
        chunk = FakeChunk({"choices": [{"delta": {"role": "assistant", "content": None}}]})
        assert OpenAILLM.parse_result(chunk) is None

    def test_generate_stream_result_yields_only_text_chunks(self):
        stream = iter([
            FakeChunk({"choices": [{"delta": {"content": "a"}}]}),
            FakeChunk({"choices": []}),
            FakeChunk({"choices": [{"delta": {"content": "b"}}]}),
        ])
        outputs = list(OpenAILLM.generate_stream_result(stream))
        assert [o.text for o in outputs] == ["a", "b"]

    def test_agenerate_stream_result(self):
        async def chunks():
            yield FakeChunk({"choices": [{"delta": {"content": "x"}}]})

        async def collect():
            return [o.text async for o in OpenAILLM.agenerate_stream_result(chunks())]

        assert asyncio.run(collect()) == ["x"]
