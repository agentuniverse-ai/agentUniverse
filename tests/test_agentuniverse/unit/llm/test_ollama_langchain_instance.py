# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_ollama_langchain_instance.py
"""Unit tests for OllamaLangchainInstance (no real ollama server)."""

import asyncio
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage

from agentuniverse.llm.ollama_langchain_instance import OllamaLangchainInstance


class FakeLLM:
    """Record calls made by the instance and return canned stream outputs."""

    def __init__(self, model_name="llama3", outputs=None):
        self.model_name = model_name
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


class TestOllamaLangchainInstance:
    """Test the ollama LangChain adapter behavior."""

    def test_init_sets_llm_and_model(self, outputs):
        llm = FakeLLM(model_name="qwen3", outputs=outputs)
        instance = OllamaLangchainInstance(llm)
        assert instance.llm is llm
        assert instance.model == "qwen3"

    def test_create_chat_stream_yields_raw_payloads(self, outputs):
        llm = FakeLLM(outputs=outputs)
        instance = OllamaLangchainInstance(llm)
        chunks = list(instance._create_chat_stream([AIMessage(content="hello")]))
        assert chunks == ["chunk-one", "chunk-two"]
        assert llm.calls[0]["stop"] is None

    def test_create_chat_stream_forwards_stop_and_kwargs(self, outputs):
        llm = FakeLLM(outputs=outputs)
        instance = OllamaLangchainInstance(llm)
        list(instance._create_chat_stream([AIMessage(content="hi")],
                                          stop=["\n"], temperature=0.5))
        call = llm.calls[0]
        assert call["stop"] == ["\n"]
        assert call["temperature"] == 0.5
        assert call["messages"][0]["content"] == "hi"

    def test_acreate_chat_stream_yields_raw_payloads(self, outputs):
        llm = FakeLLM(outputs=outputs)
        instance = OllamaLangchainInstance(llm)

        async def collect():
            return [chunk async for chunk in
                    instance._acreate_chat_stream([AIMessage(content="hello")])]

        assert asyncio.run(collect()) == ["chunk-one", "chunk-two"]
