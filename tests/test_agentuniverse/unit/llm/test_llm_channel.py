# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_llm_channel.py
"""Unit tests for pure LLMChannel helpers (no network access)."""

import asyncio

import pytest

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
from agentuniverse.llm.llm_output import LLMOutput, TokenUsage


class FakeChunk:
    """Mimic an OpenAI streamed chunk with model_dump()."""

    def __init__(self, payload):
        self.payload = payload

    def model_dump(self):
        return self.payload


def delta_chunk(text, role="assistant"):
    return FakeChunk({
        "choices": [{"delta": {"role": role, "content": text}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 2},
    })


@pytest.fixture
def channel():
    """A bare LLMChannel with an empty channel config."""
    ch = LLMChannel(channel_model_name="gpt-4o")
    ch.channel_model_config = {}
    return ch


class TestLLMChannel:
    """Test deterministic LLMChannel behavior."""

    def test_parse_result_extracts_text_and_usage(self):
        out = LLMChannel.parse_result(delta_chunk("Hi"))
        assert out.text == "Hi"
        assert out.usage.prompt_tokens == 5
        assert out.usage.completion_tokens == 2
        assert isinstance(out, LLMOutput)

    def test_parse_result_empty_choices_returns_empty_text(self):
        out = LLMChannel.parse_result(FakeChunk({"choices": []}))
        assert out.text == ""
        assert isinstance(out.usage, TokenUsage)

    def test_generate_stream_result_yields_each_chunk(self):
        outputs = list(LLMChannel().generate_stream_result(
            iter([delta_chunk("a"), delta_chunk("b")])))
        assert [o.text for o in outputs] == ["a", "b"]

    def test_agenerate_stream_result(self):
        async def chunks():
            yield delta_chunk("async")

        async def collect():
            return [o.text async for o in
                    LLMChannel().agenerate_stream_result(chunks())]

        assert asyncio.run(collect()) == ["async"]

    def test_get_num_tokens_counts_tokens(self, channel):
        assert channel.get_num_tokens("hello world") == 2

    def test_channel_model_config_setter_merges_ext_params(self):
        ch = LLMChannel(channel_model_name="m")
        ch.channel_model_config = {"ext_params": {"custom": 1},
                                   "streaming": True}
        assert ch.ext_params["custom"] == 1
        assert ch.streaming is True

    def test_channel_model_config_drives_max_context_length(self):
        ch = LLMChannel(channel_model_name="m")
        ch._channel_model_config = {"max_context_length": 4096}
        assert ch.max_context_length() == 4096

    def test_create_copy_returns_self(self, channel):
        assert channel.create_copy() is channel
