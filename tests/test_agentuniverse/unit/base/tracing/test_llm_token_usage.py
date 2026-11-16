# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Regression tests for LLM token accounting in the OTEL LLM instrumentor.

A streaming LLM call reports its token usage exactly once, so the framework must
record it exactly once as well. Agent-level token figures (the
``au.agent.usage.*`` span attributes and metrics) are read from the per-span
accumulator filled here, so recording a streaming call twice doubles every agent
token metric while non-streaming calls stay correct.
"""

import asyncio
import unittest

from opentelemetry import trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider

from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.tracing.au_trace_context import AuTraceContext
from agentuniverse.base.tracing.au_trace_manager import (
    get_current_token_usage,
    init_new_token_usage,
)
from agentuniverse.base.tracing.otel.instrumentation.llm.llm_instrumentor import (
    LLMInstrumentor,
)
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput, TokenUsage

PROMPT_TOKENS = 100
COMPLETION_TOKENS = 50
REPORTED_USAGE = TokenUsage(text_in=PROMPT_TOKENS, text_out=COMPLETION_TOKENS)


class _Chunk:
    """A single streaming chunk, shaped like the chunks providers yield."""

    def __init__(self, text: str, usage: TokenUsage = None):
        self.text = text
        self.usage = usage


def _chunks():
    yield _Chunk("Hello ")
    yield _Chunk("world", REPORTED_USAGE)


async def _async_chunks():
    for chunk in _chunks():
        yield chunk


class _StreamingLLM(LLM):
    """An LLM whose calls return a chunk stream instead of a single LLMOutput."""

    def _call(self, *args, **kwargs):
        return _chunks()

    async def _acall(self, *args, **kwargs):
        return _async_chunks()

    def get_num_tokens(self, text: str) -> int:
        return len(text)

    def max_context_length(self) -> int:
        return 4096


class _NonStreamingLLM(LLM):
    """An LLM whose calls return one LLMOutput, for comparison."""

    def _call(self, *args, **kwargs):
        return LLMOutput(text="Hello world", usage=REPORTED_USAGE)

    async def _acall(self, *args, **kwargs):
        return LLMOutput(text="Hello world", usage=REPORTED_USAGE)

    def get_num_tokens(self, text: str) -> int:
        return len(text)

    def max_context_length(self) -> int:
        return 4096


class LLMTokenUsageAccountingTest(unittest.TestCase):
    """Token usage recorded for one LLM call must match what the LLM reported."""

    @classmethod
    def setUpClass(cls):
        try:
            cls._previous_app_configer = ApplicationConfigManager().app_configer
        except ValueError:
            cls._previous_app_configer = None
        ApplicationConfigManager().app_configer = AppConfiger()

        cls._tracer_provider = TracerProvider()
        cls._instrumentor = LLMInstrumentor()
        cls._instrumentor.instrument(tracer_provider=cls._tracer_provider,
                                     meter_provider=MeterProvider())
        cls._tracer = cls._tracer_provider.get_tracer(__name__)

    @classmethod
    def tearDownClass(cls):
        cls._instrumentor.uninstrument()
        if cls._previous_app_configer is not None:
            ApplicationConfigManager().app_configer = cls._previous_app_configer

    def _run_traced_call(self, call):
        """Run one LLM call under a parent span and return that span's usage.

        The parent span stands in for the agent span the framework opens around
        an agent run; the usage accumulated on it is what the agent instrumentor
        reports as the agent's token usage.
        """
        AuTraceContext._token_count_dict.clear()
        with self._tracer.start_as_current_span("test.agent") as parent_span:
            parent_span_id = parent_span.get_span_context().span_id
            init_new_token_usage(parent_span_id)
            result = call()
            if hasattr(result, "__next__"):
                list(result)
        return get_current_token_usage(parent_span_id)

    def test_sync_streaming_usage_is_recorded_once(self):
        usage = self._run_traced_call(
            lambda: _StreamingLLM(name='streaming_llm', model_name='test-model').call("hi"))
        self.assertEqual(usage.prompt_tokens, PROMPT_TOKENS)
        self.assertEqual(usage.completion_tokens, COMPLETION_TOKENS)

    def test_async_streaming_usage_is_recorded_once(self):
        async def acall_and_drain():
            stream = await _StreamingLLM(name='async_streaming_llm',
                                         model_name='test-model').acall("hi")
            async for _ in stream:
                pass

        usage = self._run_traced_call(lambda: asyncio.run(acall_and_drain()))
        self.assertEqual(usage.prompt_tokens, PROMPT_TOKENS)
        self.assertEqual(usage.completion_tokens, COMPLETION_TOKENS)

    def test_sync_non_streaming_usage_matches_reported(self):
        usage = self._run_traced_call(
            lambda: _NonStreamingLLM(name='plain_llm', model_name='test-model').call("hi"))
        self.assertEqual(usage.prompt_tokens, PROMPT_TOKENS)
        self.assertEqual(usage.completion_tokens, COMPLETION_TOKENS)

    def test_streaming_usage_matches_non_streaming_usage(self):
        streaming = self._run_traced_call(
            lambda: _StreamingLLM(name='streaming_llm_2', model_name='test-model').call("hi"))
        non_streaming = self._run_traced_call(
            lambda: _NonStreamingLLM(name='plain_llm_2', model_name='test-model').call("hi"))
        self.assertEqual(streaming.prompt_tokens, non_streaming.prompt_tokens)
        self.assertEqual(streaming.completion_tokens, non_streaming.completion_tokens)
        self.assertEqual(streaming.total_tokens, non_streaming.total_tokens)


if __name__ == "__main__":
    unittest.main()
