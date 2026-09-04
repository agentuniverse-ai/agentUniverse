# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_langchain_instance.py
import asyncio
import unittest

from agentuniverse.llm.llm_output import LLMOutput

from examples.startup_app.demo_startup_app_with_multi_agents.intelligence.agentic.llm.langchian_instance.langchain_instance import (
    LangChainInstance,
)


class _SyncTokenCollector(object):
    """Fake run manager that records sync-streamed tokens."""

    def __init__(self):
        self.tokens = []

    def on_llm_new_token(self, token: str) -> None:
        self.tokens.append(token)


class _AsyncTokenCollector(object):
    """Fake run manager that records async-streamed tokens."""

    def __init__(self):
        self.tokens = []

    async def on_llm_new_token(self, token: str) -> None:
        self.tokens.append(token)


class _FakeLLM(object):
    """Minimal stand-in LLM for delegation tests."""

    def get_num_tokens(self, text: str) -> int:
        return len(text)

    def get_token_ids(self, text: str) -> list:
        return [ord(char) for char in text]


async def _async_stream(outputs):
    for output in outputs:
        yield output


class LangChainInstanceParseTest(unittest.TestCase):
    """Test cases for the pure stream parsing helpers."""

    def test_parse_stream_result_joins_texts(self):
        result = LangChainInstance.parse_stream_result(
            iter([LLMOutput(text='hello '), LLMOutput(text='world')]))
        self.assertEqual(result, 'hello world')

    def test_parse_stream_result_notifies_run_manager(self):
        collector = _SyncTokenCollector()
        LangChainInstance.parse_stream_result(
            iter([LLMOutput(text='a'), LLMOutput(text='b')]), collector)
        self.assertEqual(collector.tokens, ['a', 'b'])

    def test_aparse_stream_result_joins_texts(self):
        result = asyncio.run(LangChainInstance.aparse_stream_result(
            _async_stream([LLMOutput(text='foo'), LLMOutput(text='bar')])))
        self.assertEqual(result, 'foobar')

    def test_aparse_stream_result_notifies_run_manager(self):
        collector = _AsyncTokenCollector()
        asyncio.run(LangChainInstance.aparse_stream_result(
            _async_stream([LLMOutput(text='x')]), collector))
        self.assertEqual(collector.tokens, ['x'])


class LangChainInstanceTest(unittest.TestCase):
    """Test cases for deterministic LangChainInstance behaviors."""

    def setUp(self):
        self.instance = LangChainInstance(llm=_FakeLLM(), llm_type='Maya')

    def test_llm_type_property(self):
        self.assertEqual(self.instance._llm_type, 'Maya')

    def test_get_num_tokens_delegates_to_llm(self):
        self.assertEqual(self.instance.get_num_tokens('abcd'), 4)

    def test_get_token_ids_delegates_to_llm(self):
        self.assertEqual(self.instance.get_token_ids('ab'), [97, 98])
