# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_langchain_instance.py
"""Unit tests for the LangChainInstance demo wrapper."""

import asyncio

import pytest

from agentuniverse.llm.llm_output import LLMOutput
from examples.startup_app.demo_startup_app_with_single_agent_and_actions.intelligence.agentic.llm.langchian_instance.langchain_instance import (
    LangChainInstance,
)


class _SyncRecorder:
    """Records tokens through the sync langchain run manager hook."""

    def __init__(self):
        self.tokens = []

    def on_llm_new_token(self, token: str):
        self.tokens.append(token)


class _AsyncRecorder:
    """Records tokens through the async langchain run manager hook."""

    def __init__(self):
        self.tokens = []

    async def on_llm_new_token(self, token: str):
        self.tokens.append(token)


class TestLangChainInstance:
    """Test LangChainInstance stream-result parsing helpers."""

    def test_parse_stream_result_concatenates(self):
        outputs = iter([LLMOutput(text='a', raw=None), LLMOutput(text='b', raw=None)])
        assert LangChainInstance.parse_stream_result(outputs) == 'ab'

    def test_parse_stream_result_reports_tokens(self):
        recorder = _SyncRecorder()
        outputs = iter([LLMOutput(text='x', raw=None), LLMOutput(text='y', raw=None)])
        result = LangChainInstance.parse_stream_result(outputs, recorder)
        assert result == 'xy'
        assert recorder.tokens == ['x', 'y']

    def test_parse_stream_result_empty(self):
        assert LangChainInstance.parse_stream_result(iter([])) == ''

    def test_aparse_stream_result_concatenates(self):
        async def run():
            async def stream():
                yield LLMOutput(text='p', raw=None)
                yield LLMOutput(text='q', raw=None)
            return await LangChainInstance.aparse_stream_result(stream())
        assert asyncio.run(run()) == 'pq'

    def test_aparse_stream_result_reports_tokens(self):
        async def run():
            recorder = _AsyncRecorder()

            async def stream():
                yield LLMOutput(text='1', raw=None)
                yield LLMOutput(text='2', raw=None)
            result = await LangChainInstance.aparse_stream_result(stream(), recorder)
            return result, recorder.tokens
        result, tokens = asyncio.run(run())
        assert result == '12'
        assert tokens == ['1', '2']

    def test_llm_type_property(self):
        from examples.startup_app.demo_startup_app_with_single_agent_and_actions.intelligence.agentic.llm.maya.insurance_maya_llm import (
            InsuranceMayaLLM,
        )
        instance = LangChainInstance(llm=InsuranceMayaLLM(), llm_type='Maya')
        assert instance._llm_type == 'Maya'
