# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_consts.py
"""Unit tests for the OpenTelemetry tracing constants."""

import pytest

from agentuniverse.base.tracing.otel import consts


class TestOtelConsts:
    """Test the wire-level identifiers exported by the otel consts module."""

    def test_trace_id_keys(self):
        """Trace id context and HTTP header keys keep their documented values."""
        assert consts.TRACE_ID_KEY == "auTraceId"
        assert consts.HTTP_HEADER_TRACE_ID_KEY == "AU-TraceId"

    def test_chain_id_keys(self):
        """Chain id context and HTTP header keys keep their documented values."""
        assert consts.CHAIN_ID_KEY == "auChainId"
        assert consts.HTTP_HEADER_CHAIN_ID_KEY == "AU-ChainId"

    def test_session_id_keys(self):
        """Session id context, HTTP header and span keys are stable."""
        assert consts.SESSION_ID_KEY == "auSessionId"
        assert consts.HTTP_HEADER_SESSION_ID_KEY == "AU-SessionId"
        assert consts.SPAN_SESSION_ID_KEY == "au.trace.session.id"

    @pytest.mark.parametrize(
        ("context_key", "header_key"),
        [
            (consts.TRACE_ID_KEY, consts.HTTP_HEADER_TRACE_ID_KEY),
            (consts.CHAIN_ID_KEY, consts.HTTP_HEADER_CHAIN_ID_KEY),
            (consts.SESSION_ID_KEY, consts.HTTP_HEADER_SESSION_ID_KEY),
        ],
    )
    def test_header_keys_follow_au_prefix_scheme(self, context_key, header_key):
        """HTTP headers mirror the context key with an AU- prefix."""
        assert header_key.startswith("AU-")
        assert header_key.removeprefix("AU-") == context_key.removeprefix("au")

    def test_all_keys_are_distinct_strings(self):
        """No two exported identifiers collide."""
        keys = [
            consts.TRACE_ID_KEY,
            consts.HTTP_HEADER_TRACE_ID_KEY,
            consts.CHAIN_ID_KEY,
            consts.HTTP_HEADER_CHAIN_ID_KEY,
            consts.SESSION_ID_KEY,
            consts.HTTP_HEADER_SESSION_ID_KEY,
            consts.SPAN_SESSION_ID_KEY,
        ]
        assert all(isinstance(key, str) for key in keys)
        assert len(keys) == len(set(keys))
