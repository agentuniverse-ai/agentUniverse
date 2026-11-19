# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01 10:00
# @Author  : Yue Wang
# @FileName: test_session_span_processor.py
"""Unit tests for SessionSpanProcessor."""

import pytest

from agentuniverse.base.tracing.au_trace_context import AuTraceContext
from agentuniverse.base.tracing.au_trace_manager import AuTraceManager
from agentuniverse.base.tracing.otel.consts import SPAN_SESSION_ID_KEY
from agentuniverse.base.tracing.otel.span_processor.session_span_processor import (
    SessionSpanProcessor,
)


class _FakeSpan:
    """Minimal span double that records set_attribute calls."""

    def __init__(self):
        self.attributes = {}

    def set_attribute(self, key, value):
        self.attributes[key] = value


class TestSessionSpanProcessor:
    """Test suite for SessionSpanProcessor."""

    @pytest.fixture
    def processor(self):
        return SessionSpanProcessor()

    @pytest.fixture(autouse=True)
    def fresh_trace(self):
        AuTraceManager().reset_trace()
        yield
        AuTraceManager().reset_trace()

    def test_on_start_records_current_session_id(self, processor):
        context = AuTraceContext.from_trace_context(
            trace_id='a' * 32, span_id='b' * 16, session_id='session-abc')
        AuTraceManager().recover_trace(context)

        span = _FakeSpan()
        processor.on_start(span)

        assert span.attributes.get(SPAN_SESSION_ID_KEY) == 'session-abc'

    def test_on_start_without_session_id_records_negative_one(self, processor):
        span = _FakeSpan()
        processor.on_start(span)

        assert span.attributes.get(SPAN_SESSION_ID_KEY) == '-1'

    def test_on_start_accepts_parent_context_argument(self, processor):
        context = AuTraceContext.from_trace_context(
            trace_id='c' * 32, span_id='d' * 16, session_id='session-xyz')
        AuTraceManager().recover_trace(context)

        span = _FakeSpan()
        processor.on_start(span, parent_context=None)

        assert span.attributes.get(SPAN_SESSION_ID_KEY) == 'session-xyz'

    def test_on_end_is_no_op(self, processor):
        assert processor.on_end(_FakeSpan()) is None

    def test_shutdown_is_no_op(self, processor):
        assert processor.shutdown() is None

    def test_force_flush_is_no_op(self, processor):
        assert processor.force_flush(timeout_millis=5000) is None
