# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for the AuTraceContext trace helper.

AuTraceContext keeps the trace/span/session identifiers of the current
execution and accumulates LLM token usage per span.  The tests below exercise
its deterministic behaviors: identifier generation, context reconstruction,
property access and token usage accounting, using explicit span ids and an
isolated OTel context so no live tracing state is required.
"""

import pytest
from opentelemetry import context as otel_context
from opentelemetry import trace

from agentuniverse.base.tracing.au_trace_context import AuTraceContext
from agentuniverse.llm.llm_output import TokenUsage


@pytest.fixture
def clean_context():
    """Make sure no valid OTel span leaks into identifier generation."""
    token = otel_context.attach(trace.set_span_in_context(trace.INVALID_SPAN))
    yield
    otel_context.detach(token)


class TestNewContext:
    """Tests for creating a brand new trace context."""

    def test_session_id_defaults_to_none(self, clean_context):
        ctx = AuTraceContext.new_context()
        assert ctx.session_id is None

    def test_trace_id_is_32_hex_chars(self, clean_context):
        ctx = AuTraceContext.new_context()
        assert len(ctx.trace_id) == 32
        assert all(c in "0123456789abcdef" for c in ctx.trace_id)

    def test_span_id_is_16_hex_chars(self, clean_context):
        ctx = AuTraceContext.new_context()
        assert len(ctx.span_id) == 16
        assert all(c in "0123456789abcdef" for c in ctx.span_id)

    def test_generated_ids_differ_between_contexts(self, clean_context):
        first = AuTraceContext.new_context()
        second = AuTraceContext.new_context()
        assert first.trace_id != second.trace_id
        assert first.span_id != second.span_id


class TestFromTraceContext:
    """Tests for reconstructing a context from known identifiers."""

    def test_fields_are_restored(self):
        ctx = AuTraceContext.from_trace_context("a" * 32, "b" * 16, "session-1")
        assert ctx.session_id == "session-1"
        assert ctx.trace_id == "a" * 32
        assert ctx.span_id == "b" * 16

    def test_session_id_is_optional(self):
        ctx = AuTraceContext.from_trace_context("a" * 32, "b" * 16)
        assert ctx.session_id is None

    def test_to_dict_matches_constructed_fields(self):
        ctx = AuTraceContext.from_trace_context("a" * 32, "b" * 16, "session-2")
        assert ctx.to_dict() == {
            "session_id": "session-2",
            "trace_id": "a" * 32,
            "span_id": "b" * 16,
        }


class TestSetters:
    """Tests for the session/trace/span setter methods."""

    def test_set_session_id(self, clean_context):
        ctx = AuTraceContext.new_context()
        ctx.set_session_id("new-session")
        assert ctx.session_id == "new-session"

    def test_set_trace_id_updates_value(self, clean_context):
        ctx = AuTraceContext.new_context()
        ctx.set_trace_id("f" * 32)
        assert ctx.trace_id == "f" * 32

    def test_set_span_id_updates_value(self, clean_context):
        ctx = AuTraceContext.new_context()
        ctx.set_span_id("e" * 16)
        assert ctx.span_id == "e" * 16


class TestTokenUsage:
    """Tests for per-span token usage accumulation."""

    def test_init_creates_empty_usage(self, clean_context):
        ctx = AuTraceContext.new_context()
        ctx.init_new_token_usage(span_id="span-a")
        usage = ctx.get_current_token_usage(span_id="span-a")
        assert usage.text_in == 0
        assert usage.text_out == 0

    def test_add_accumulates_token_usage(self, clean_context):
        ctx = AuTraceContext.new_context()
        ctx.init_new_token_usage(span_id="span-b")
        ctx.add_current_token_usage(TokenUsage(text_in=5, text_out=3), span_id="span-b")
        ctx.add_current_token_usage(TokenUsage(text_in=2, text_out=1), span_id="span-b")
        usage = ctx.get_current_token_usage(span_id="span-b")
        assert usage.text_in == 7
        assert usage.text_out == 4

    def test_unknown_span_raises_key_error(self, clean_context):
        ctx = AuTraceContext.new_context()
        with pytest.raises(KeyError):
            ctx.get_current_token_usage(span_id="missing-span")


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
