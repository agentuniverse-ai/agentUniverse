# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/02/10 10:20
# @Author  : Yue Wang
# @FileName: test_au_session_propagator.py
"""Unit tests for AUSessionPropagator inject/extract behavior."""

import pytest
from opentelemetry.baggage import get_all
from opentelemetry.propagators import textmap

from agentuniverse.base.tracing.au_trace_manager import (
    AuTraceManager,
    get_session_id,
    set_session_id,
)
from agentuniverse.base.tracing.otel.consts import (
    HTTP_HEADER_SESSION_ID_KEY,
    SESSION_ID_KEY,
)
from agentuniverse.base.tracing.otel.propagator.au_session_propagator import (
    AUSessionPropagator,
)


class TestAUSessionPropagator:
    """Test AUSessionPropagator header propagation logic."""

    @pytest.fixture(autouse=True)
    def reset_trace(self):
        """Reset the session-id trace state before and after each test."""
        AuTraceManager().reset_trace()
        yield
        AuTraceManager().reset_trace()

    @pytest.fixture
    def propagator(self):
        """Create an AUSessionPropagator instance."""
        return AUSessionPropagator()

    def test_fields_returns_session_keys(self, propagator):
        """fields must list the propagated header keys."""
        assert propagator.fields == {
            HTTP_HEADER_SESSION_ID_KEY,
            SESSION_ID_KEY,
        }

    def test_inject_writes_session_id_header(self, propagator):
        """inject must set both session keys when a session id exists."""
        set_session_id("sess-12345")
        carrier: dict = {}
        propagator.inject(carrier)
        assert carrier[HTTP_HEADER_SESSION_ID_KEY] == "sess-12345"
        assert carrier[SESSION_ID_KEY] == "sess-12345"

    def test_inject_without_session_id_is_noop(self, propagator):
        """inject must not touch the carrier when no session id exists."""
        carrier: dict = {}
        propagator.inject(carrier)
        assert carrier == {}

    def test_extract_reads_header_session_id(self, propagator):
        """extract must read the session id from the AU header."""
        carrier = {HTTP_HEADER_SESSION_ID_KEY: ["sess-abc"]}
        ctx = propagator.extract(carrier)
        assert get_session_id() == "sess-abc"
        baggage = get_all(ctx)
        assert baggage is not None

    def test_extract_empty_carrier_returns_context(self, propagator):
        """extract must tolerate an empty carrier and set no session id."""
        ctx = propagator.extract({})
        assert ctx is not None
        assert get_session_id() is None

    def test_extract_uses_custom_setter(self, propagator):
        """extract must honor a caller-supplied getter."""
        seen = {}

        class DictGetter(textmap.Getter):
            def get(self, carrier, key):
                return [carrier.get(key)]

            def keys(self, carrier):
                return list(carrier.keys())

        ctx = propagator.extract({"AU-SessionId": "sess-x"}, getter=DictGetter())
        assert get_session_id() == "sess-x"
        assert ctx is not None
