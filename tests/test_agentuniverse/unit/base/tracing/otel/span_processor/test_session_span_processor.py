# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/13 10:00
# @Author  : kaichuan
# @FileName: test_session_span_processor.py
"""Unit tests for SessionSpanProcessor."""

from unittest.mock import MagicMock, patch

import pytest
from opentelemetry.sdk.trace import SpanProcessor

from agentuniverse.base.tracing.otel.consts import SPAN_SESSION_ID_KEY
from agentuniverse.base.tracing.otel.span_processor.session_span_processor import (
    SessionSpanProcessor,
)


class TestSessionSpanProcessor:
    """Test SessionSpanProcessor lifecycle hooks."""

    @pytest.fixture
    def processor(self):
        """Create a SessionSpanProcessor instance."""
        return SessionSpanProcessor()

    @pytest.fixture
    def span(self):
        """Create a mock span that records set_attribute calls."""
        return MagicMock()

    def test_is_span_processor(self, processor):
        """SessionSpanProcessor implements the SDK SpanProcessor interface."""
        assert isinstance(processor, SpanProcessor)

    def test_on_start_sets_session_id_attribute(self, processor, span):
        """on_start writes the resolved session id onto the span."""
        with patch(
                "agentuniverse.base.tracing.otel.span_processor."
                "session_span_processor.get_session_id",
                return_value="sess-123"):
            processor.on_start(span)
        span.set_attribute.assert_called_once_with(
            SPAN_SESSION_ID_KEY, "sess-123")

    def test_on_start_defaults_to_minus_one(self, processor, span):
        """on_start falls back to '-1' when no session is active."""
        with patch(
                "agentuniverse.base.tracing.otel.span_processor."
                "session_span_processor.get_session_id",
                return_value=None):
            processor.on_start(span)
        span.set_attribute.assert_called_once_with(
            SPAN_SESSION_ID_KEY, "-1")

    def test_on_start_accepts_parent_context(self, processor, span):
        """A parent context does not change the attribute that is written."""
        parent = object()
        with patch(
                "agentuniverse.base.tracing.otel.span_processor."
                "session_span_processor.get_session_id",
                return_value="sess-9"):
            processor.on_start(span, parent_context=parent)
        span.set_attribute.assert_called_once_with(
            SPAN_SESSION_ID_KEY, "sess-9")

    def test_session_id_key_constant(self):
        """SPAN_SESSION_ID_KEY carries the documented attribute name."""
        assert SPAN_SESSION_ID_KEY == "au.trace.session.id"

    def test_lifecycle_noops_return_none(self, processor, span):
        """on_end, shutdown and force_flush are safe no-ops."""
        assert processor.on_end(span) is None
        assert processor.shutdown() is None
        assert processor.force_flush(timeout_millis=100) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
