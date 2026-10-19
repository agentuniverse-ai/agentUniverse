# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_langchain_instance.py

"""Unit tests for the LangChainInstance example adapter."""

import asyncio
import unittest

from agentuniverse.llm.llm_output import LLMOutput
from examples.startup_app.demo_startup_app_with_single_agent.intelligence.agentic.llm.langchian_instance.langchain_instance import (
    LangChainInstance)


class StubLLM(object):
    """Minimal llm double with a deterministic call result."""

    def call(self, prompt, stop=None, **kwargs):
        return LLMOutput(text="stub reply", raw={"prompt": prompt})

    async def acall(self, prompt, stop=None, **kwargs):
        return LLMOutput(text="stub async reply", raw={"prompt": prompt})


class TestLangChainInstance(unittest.TestCase):
    """Deterministic adapter behaviors without any real model."""

    def setUp(self):
        self.instance = LangChainInstance(llm=StubLLM(), llm_type="Maya")

    def test_init_sets_attributes(self):
        self.assertEqual(self.instance._llm_type, "Maya")
        self.assertIsNotNone(self.instance.llm)

    def test_call_non_streaming_returns_text(self):
        self.assertEqual(self.instance._call(prompt="hi"), "stub reply")

    def test_call_streaming_concatenates_chunks(self):
        def fake_call(prompt, stop=None, **kwargs):
            return iter([LLMOutput(text="a"), LLMOutput(text="b"), LLMOutput(text="c")])
        streaming = LangChainInstance(llm=StubLLM(), llm_type="Maya")
        streaming.llm.call = fake_call
        self.assertEqual(streaming._call(prompt="hi", streaming=True), "abc")

    def test_acall_returns_text(self):
        result = asyncio.run(self.instance._acall(prompt="hi"))
        self.assertEqual(result, "stub async reply")

    def test_parse_stream_result_concatenates(self):
        stream = iter([LLMOutput(text="x"), LLMOutput(text="y"), LLMOutput(text="z")])
        self.assertEqual(LangChainInstance.parse_stream_result(stream), "xyz")

    def test_parse_stream_result_notifies_run_manager(self):
        class FakeManager(object):
            def __init__(self):
                self.tokens = []
            def on_llm_new_token(self, token):
                self.tokens.append(token)
        manager = FakeManager()
        stream = iter([LLMOutput(text="a"), LLMOutput(text="b")])
        self.assertEqual(LangChainInstance.parse_stream_result(stream, manager), "ab")
        self.assertEqual(manager.tokens, ["a", "b"])

    def test_aparse_stream_result_concatenates(self):
        async def agen():
            yield LLMOutput(text="p")
            yield LLMOutput(text="q")
        result = asyncio.run(LangChainInstance.aparse_stream_result(agen()))
        self.assertEqual(result, "pq")


if __name__ == '__main__':
    unittest.main()
