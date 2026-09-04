# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/02/10 10:10
# @Author  : Yue Wang
# @FileName: test_consts.py
"""Unit tests for the OTEL tracing constant definitions."""

from agentuniverse.base.tracing.otel.consts import (
    CHAIN_ID_KEY,
    HTTP_HEADER_CHAIN_ID_KEY,
    HTTP_HEADER_SESSION_ID_KEY,
    HTTP_HEADER_TRACE_ID_KEY,
    SESSION_ID_KEY,
    SPAN_SESSION_ID_KEY,
    TRACE_ID_KEY,
)


class TestTracingConsts:
    """Validate the key/header constant values used by the tracing stack."""

    def test_trace_id_keys(self):
        """The trace id keys must use the canonical AU names."""
        assert TRACE_ID_KEY == "auTraceId"
        assert HTTP_HEADER_TRACE_ID_KEY == "AU-TraceId"

    def test_chain_id_keys(self):
        """The chain id keys must use the canonical AU names."""
        assert CHAIN_ID_KEY == "auChainId"
        assert HTTP_HEADER_CHAIN_ID_KEY == "AU-ChainId"

    def test_session_id_keys(self):
        """The session id keys must use the canonical AU names."""
        assert SESSION_ID_KEY == "auSessionId"
        assert HTTP_HEADER_SESSION_ID_KEY == "AU-SessionId"
        assert SPAN_SESSION_ID_KEY == "au.trace.session.id"

    def test_keys_are_distinct(self):
        """The internal keys must all be distinct strings."""
        internal = {TRACE_ID_KEY, CHAIN_ID_KEY, SESSION_ID_KEY}
        assert len(internal) == 3

    def test_header_keys_are_distinct(self):
        """The HTTP header keys must all be distinct strings."""
        headers = {
            HTTP_HEADER_TRACE_ID_KEY,
            HTTP_HEADER_CHAIN_ID_KEY,
            HTTP_HEADER_SESSION_ID_KEY,
        }
        assert len(headers) == 3

    def test_values_are_strings(self):
        """Every exported constant must be a non-empty string."""
        for value in (
            TRACE_ID_KEY,
            HTTP_HEADER_TRACE_ID_KEY,
            CHAIN_ID_KEY,
            HTTP_HEADER_CHAIN_ID_KEY,
            SESSION_ID_KEY,
            HTTP_HEADER_SESSION_ID_KEY,
            SPAN_SESSION_ID_KEY,
        ):
            assert isinstance(value, str)
            assert len(value) > 0
