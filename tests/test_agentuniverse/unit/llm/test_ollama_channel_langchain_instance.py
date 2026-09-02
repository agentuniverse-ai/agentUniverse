# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_ollama_channel_langchain_instance.py
"""Unit tests for OllamaChannelLangchainInstance (no real ollama server)."""

import asyncio
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage

from agentuniverse.llm.llm_channel.langchain_instance.ollama_channel_langchain_instance import (
    OllamaChannelLangchainInstance,
)


class FakeChannel:
    """Record calls made by the adapter and return canned stream outputs."""

    def __init__(self, model_name="llama3", outputs=None):
        self.channel_model_name = model_name
        self.outputs = outputs or []
        self.calls = []

    def call(self, **kwargs):
        self.calls.append(kwargs)
        return iter(self.outputs)

    async def acall(self, **kwargs):
        self.calls.append(kwargs)
        return self._async_outputs()

    async def _async_outputs(self):
        for output in self.outputs:
            yield output


@pytest.fixture
def outputs():
    """A stream of two llm outputs whose raw payloads are strings."""
    return [SimpleNamespace(raw="chunk-one"), SimpleNamespace(raw="chunk-two")]


class TestOllamaChannelLangchainInstance:
    """Test the ollama channel langchain adapter behavior."""

    def test_init_sets_channel_and_model(self, outputs):
        fake = FakeChannel(model_name="qwen3", outputs=outputs)
        instance = OllamaChannelLangchainInstance(fake)
        assert instance.llm_channel is fake
        assert instance.model == "qwen3"

    def test_create_chat_stream_yields_raw_payloads(self, outputs):
        fake = FakeChannel(outputs=outputs)
        instance = OllamaChannelLangchainInstance(fake)
        chunks = list(instance._create_chat_stream([AIMessage(content="hello")]))
        assert chunks == ["chunk-one", "chunk-two"]
        assert fake.calls[0]["stop"] is None

    def test_create_chat_stream_forwards_kwargs(self, outputs):
        fake = FakeChannel(outputs=outputs)
        instance = OllamaChannelLangchainInstance(fake)
        list(instance._create_chat_stream([AIMessage(content="hi")],
                                          stop=["\n"], temperature=0.2))
        call = fake.calls[0]
        assert call["stop"] == ["\n"]
        assert call["temperature"] == 0.2
        assert call["messages"][0]["content"] == "hi"

    def test_acreate_chat_stream_yields_raw_payloads(self, outputs):
        fake = FakeChannel(outputs=outputs)
        instance = OllamaChannelLangchainInstance(fake)

        async def collect():
            return [c async for c in
                    instance._acreate_chat_stream([AIMessage(content="hello")])]

        assert asyncio.run(collect()) == ["chunk-one", "chunk-two"]
