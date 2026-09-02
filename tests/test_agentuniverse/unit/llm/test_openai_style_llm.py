# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_openai_style_llm.py
"""Unit tests for pure OpenAIStyleLLM helpers (no network access)."""

import asyncio

import pytest

from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM


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
    """Create an OpenAIStyleLLM instance with a dummy key for offline tests."""
    return OpenAIStyleLLM(model_name="gpt-4o", api_key="test-key")


class TestOpenAIStyleLLM:
    """Test deterministic OpenAIStyleLLM behavior."""

    def test_get_num_tokens(self, llm):
        assert llm.get_num_tokens("hello world") == 2

    def test_parse_result_returns_text(self, llm):
        chunk = FakeChunk({"choices": [{"delta": {"role": "assistant", "content": "Hi"}}]})
        result = llm.parse_result(chunk)
        assert result.text == "Hi"

    def test_parse_result_empty_choices_returns_empty_text(self, llm):
        chunk = FakeChunk({"choices": []})
        result = llm.parse_result(chunk)
        assert result is not None
        assert result.text == ""

    def test_parse_result_missing_content_returns_empty_text(self, llm):
        chunk = FakeChunk({"choices": [{"delta": {"role": "assistant", "content": None}}]})
        assert llm.parse_result(chunk).text == ""

    def test_generate_stream_result_yields_every_chunk(self, llm):
        stream = iter([
            FakeChunk({"choices": [{"delta": {"content": "a"}}]}),
            FakeChunk({"choices": []}),
            FakeChunk({"choices": [{"delta": {"content": None}}]}),
        ])
        outputs = list(llm.generate_stream_result(stream))
        assert [o.text for o in outputs] == ["a", "", ""]

    def test_agenerate_stream_result(self, llm):
        async def chunks():
            yield FakeChunk({"choices": [{"delta": {"content": "x"}}]})

        async def collect():
            return [o.text async for o in llm.agenerate_stream_result(chunks())]

        assert asyncio.run(collect()) == ["x"]
