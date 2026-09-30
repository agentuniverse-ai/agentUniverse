#!/usr/bin/env python3

import asyncio

import pytest
from opentelemetry import context as otel_context
from opentelemetry import trace as otel_trace

from agentuniverse.base.annotation.trace import (
    InvocationChainContext,
    _default_agent_wrapper_async,
    _default_agent_wrapper_sync,
    _default_llm_wrapper_sync,
)
from agentuniverse.base.tracing.au_trace_context import AuTraceContext
from agentuniverse.base.util.monitor.monitor import Monitor

TRACE_A = "a" * 32
SPAN_A = "b" * 16


def _inject_foreign_trace_context():
    """Simulate Agent.run attaching a caller supplied trace context."""
    AuTraceContext.from_trace_context(TRACE_A, SPAN_A, session_id="request-A")


def _current_trace_id():
    ctx = otel_trace.get_current_span().get_span_context()
    return f"{ctx.trace_id:032x}" if ctx.is_valid else None


@pytest.fixture(autouse=True)
def _clean_otel_context():
    """Start and end every test from a pristine OTel context."""
    otel_context.attach(otel_context.Context())
    yield
    otel_context.attach(otel_context.Context())


def _patch_memory_module(monkeypatch):
    class _StubMemoryModule:
        def __call__(self):
            return self

        def add_agent_input_info(self, *args, **kwargs):
            return None

        def add_agent_result_info(self, *args, **kwargs):
            return None

    import agentuniverse.base.annotation.trace as trace_module

    monkeypatch.setattr(trace_module, "ConversationMemoryModule", _StubMemoryModule)


class TestTraceContextIsolation:

    def test_sync_agent_run_restores_otel_context(self, monkeypatch):
        _patch_memory_module(monkeypatch)
        trace_before = _current_trace_id()

        def fake_agent_run(**kwargs):
            _inject_foreign_trace_context()
            assert _current_trace_id() == TRACE_A
            return "ok"

        result = _default_agent_wrapper_sync(fake_agent_run)
        assert result == "ok"
        assert _current_trace_id() == trace_before, (
            "the trace context injected during the agent run leaked into "
            "the caller scope; a reused server thread would attach the next "
            "request's spans to the previous request's trace"
        )

    def test_async_agent_run_restores_otel_context(self, monkeypatch):
        _patch_memory_module(monkeypatch)
        trace_before = _current_trace_id()

        async def fake_agent_run(**kwargs):
            _inject_foreign_trace_context()
            assert _current_trace_id() == TRACE_A
            return "ok"

        result = asyncio.run(_default_agent_wrapper_async(fake_agent_run))
        assert result == "ok"
        assert _current_trace_id() == trace_before

    def test_agent_run_restores_context_on_failure(self, monkeypatch):
        _patch_memory_module(monkeypatch)
        trace_before = _current_trace_id()

        def failing_agent_run(**kwargs):
            _inject_foreign_trace_context()
            raise ValueError

        with pytest.raises(ValueError):
            _default_agent_wrapper_sync(failing_agent_run)
        assert _current_trace_id() == trace_before

    def test_token_usage_lookups_are_safe_for_unknown_span(self):
        from agentuniverse.llm.llm_output import TokenUsage

        context = AuTraceContext()
        unknown_span_id = 12345678

        usage = context.get_current_token_usage(unknown_span_id)
        assert isinstance(usage, TokenUsage)

        context.add_current_token_usage(TokenUsage(), unknown_span_id)
        assert isinstance(context.get_current_token_usage(unknown_span_id), TokenUsage)

    def test_streaming_llm_wrapper_pops_chain_when_consumer_aborts(self, monkeypatch):
        import agentuniverse.base.annotation.trace as trace_module

        monkeypatch.setattr(trace_module, "_llm_plugins", lambda func: func)

        def chunks():
            yield "chunk-1"
            yield "chunk-2"

        def fake_llm(**kwargs):
            return chunks()

        with InvocationChainContext(source="agent", node_type="agent"):
            baseline = len(Monitor.get_invocation_chain())
            stream = _default_llm_wrapper_sync(fake_llm)
            assert len(Monitor.get_invocation_chain()) == baseline + 1

            # consume one chunk, then abort like a disconnecting client
            iterator = iter(stream)
            assert next(iterator) == "chunk-1"
            stream.close()

            assert (
                len(Monitor.get_invocation_chain()) == baseline
            ), "aborting the stream left the llm node on the invocation chain"
