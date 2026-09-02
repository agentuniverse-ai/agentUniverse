# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/05 10:30
# @Author  : kaichuan
# @FileName: test_au_session_propagator.py
"""Unit tests for AUSessionPropagator in base.tracing.otel.propagator."""

import pytest

from opentelemetry.baggage import get_baggage

from agentuniverse.base.tracing.au_trace_manager import set_session_id
from agentuniverse.base.tracing.otel.consts import (
    HTTP_HEADER_SESSION_ID_KEY,
    SESSION_ID_KEY,
)
from agentuniverse.base.tracing.otel.propagator.au_session_propagator import (
    AUSessionPropagator,
)


class TestAUSessionPropagator:
    """Test session id propagation via carriers."""

    @pytest.fixture(autouse=True)
    def reset_session(self):
        """Clear the global session id around each test."""
        set_session_id(None)
        yield
        set_session_id(None)

    def test_fields_lists_both_keys(self):
        """fields returns exactly the two supported carrier keys."""
        propagator = AUSessionPropagator()
        assert propagator.fields == {
            HTTP_HEADER_SESSION_ID_KEY,
            SESSION_ID_KEY,
        }

    def test_inject_sets_both_keys(self):
        """inject writes the current session id under both keys."""
        set_session_id("sess-123")
        carrier = {}
        AUSessionPropagator().inject(carrier)
        assert carrier[HTTP_HEADER_SESSION_ID_KEY] == "sess-123"
        assert carrier[SESSION_ID_KEY] == "sess-123"

    def test_inject_without_session_id_leaves_carrier_empty(self):
        """With no active session id, nothing is written to the carrier."""
        set_session_id(None)
        carrier = {}
        AUSessionPropagator().inject(carrier)
        assert carrier == {}

    def test_extract_sets_baggage_and_session(self):
        """extract puts the value in baggage and updates the session id."""
        from agentuniverse.base.tracing.au_trace_manager import get_session_id

        carrier = {HTTP_HEADER_SESSION_ID_KEY: ["abc-1"]}
        context = AUSessionPropagator().extract(carrier)
        assert get_baggage(HTTP_HEADER_SESSION_ID_KEY, context) == ["abc-1"]
        assert get_session_id() == "abc-1"

    def test_extract_prefers_http_header_key(self):
        """When both keys are present the HTTP header key wins."""
        carrier = {
            HTTP_HEADER_SESSION_ID_KEY: ["from-header"],
            SESSION_ID_KEY: ["from-plain"],
        }
        context = AUSessionPropagator().extract(carrier)
        assert get_baggage(HTTP_HEADER_SESSION_ID_KEY, context) == ["from-header"]
        assert get_baggage(SESSION_ID_KEY, context) is None

    def test_extract_empty_carrier_returns_context(self):
        """An empty carrier yields a context without session baggage."""
        from opentelemetry.context.context import Context

        context = AUSessionPropagator().extract({})
        assert isinstance(context, Context)
        assert get_baggage(HTTP_HEADER_SESSION_ID_KEY, context) is None
        assert get_baggage(SESSION_ID_KEY, context) is None
