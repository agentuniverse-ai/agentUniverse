# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/13 10:00
# @Author  : kaichuan
# @FileName: test_au_trace_context.py
"""Unit tests for AuTraceContext."""

import string

import pytest
from opentelemetry import context as otel_context

from agentuniverse.base.tracing.au_trace_context import AuTraceContext

_HEX = set(string.hexdigits)


@pytest.fixture(autouse=True)
def isolated_otel_context():
    """Give each test a clean OpenTelemetry context and restore it after."""
    token = otel_context.attach({})
    yield
    otel_context.detach(token)


class TestAuTraceContext:
    """Test AuTraceContext id handling and serialization."""

    def test_from_trace_context_preserves_ids(self):
        """from_trace_context keeps the supplied ids and session."""
        ctx = AuTraceContext.from_trace_context("a" * 32, "b" * 16, "sess-1")
        assert ctx.trace_id == "a" * 32
        assert ctx.span_id == "b" * 16
        assert ctx.session_id == "sess-1"

    def test_new_context_generates_hex_ids(self):
        """new_context yields 32-char trace and 16-char span hex ids."""
        ctx = AuTraceContext.new_context()
        assert len(ctx.trace_id) == 32
        assert len(ctx.span_id) == 16
        assert set(ctx.trace_id) <= _HEX
        assert set(ctx.span_id) <= _HEX

    def test_generated_ids_have_expected_lengths(self):
        """The static generators emit correctly-sized hex strings."""
        trace_id = AuTraceContext._generate_trace_id()
        span_id = AuTraceContext._generate_span_id()
        assert len(trace_id) == 32
        assert len(span_id) == 16
        assert set(trace_id) <= _HEX
        assert set(span_id) <= _HEX

    def test_set_trace_context_updates_ids(self):
        """set_trace_context replaces the stored trace and span ids."""
        ctx = AuTraceContext.new_context()
        ctx.set_trace_context("c" * 32, "d" * 16)
        assert ctx.trace_id == "c" * 32
        assert ctx.span_id == "d" * 16

    def test_set_session_id(self):
        """set_session_id updates the session id property."""
        ctx = AuTraceContext.new_context()
        ctx.set_session_id("s42")
        assert ctx.session_id == "s42"

    def test_to_dict_shape(self):
        """to_dict returns exactly the three public identifiers."""
        ctx = AuTraceContext.from_trace_context("a" * 32, "b" * 16, "sess")
        assert ctx.to_dict() == {
            "session_id": "sess",
            "trace_id": "a" * 32,
            "span_id": "b" * 16,
        }

    def test_str_format(self):
        """__str__/__repr__ render a stable, readable representation."""
        ctx = AuTraceContext.from_trace_context("a" * 32, "b" * 16, "sess")
        expected = (
            f"Context(session_id=sess, trace_id={'a' * 32}, "
            f"span_id={'b' * 16})"
        )
        assert str(ctx) == expected
        assert repr(ctx) == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
