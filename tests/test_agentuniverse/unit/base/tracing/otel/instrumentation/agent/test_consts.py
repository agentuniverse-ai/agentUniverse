# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/05 10:25
# @Author  : kaichuan
# @FileName: test_consts.py
"""Unit tests for the OTel agent instrumentation constants."""

import pytest

from agentuniverse.base.tracing.otel.instrumentation.agent import consts


def _public_attrs(cls):
    """Return (name, value) pairs of public string attributes of a class."""
    return [
        (name, value)
        for name, value in vars(cls).items()
        if not name.startswith("_") and isinstance(value, str)
    ]


class TestInstrumentorConstants:
    """Test the instrumentation identity constants."""

    def test_instrumentor_name(self):
        """INSTRUMENTOR_NAME identifies the agentuniverse agent instrumentation."""
        assert consts.INSTRUMENTOR_NAME == "opentelemetry-instrumentation-agentuniverse-agent"

    def test_instrumentor_version(self):
        """INSTRUMENTOR_VERSION follows semantic versioning."""
        parts = consts.INSTRUMENTOR_VERSION.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)


class TestMetricNames:
    """Test the metric name constants."""

    def test_known_metric_names(self):
        """Core metric names match the documented values."""
        assert consts.MetricNames.AGENT_CALLS_TOTAL == "agent_calls_total"
        assert consts.MetricNames.AGENT_ERRORS_TOTAL == "agent_errors_total"
        assert consts.MetricNames.AGENT_CALL_DURATION == "agent_call_duration"
        assert consts.MetricNames.AGENT_TOTAL_TOKENS == "agent_total_tokens"

    def test_metric_names_are_unique_and_prefixed(self):
        """Every metric name is unique and starts with 'agent_'."""
        attrs = _public_attrs(consts.MetricNames)
        values = [value for _, value in attrs]
        assert len(values) == len(set(values))
        assert all(value.startswith("agent_") for value in values)


class TestSpanAttributes:
    """Test the span attribute name constants."""

    def test_known_span_attributes(self):
        """Core span attributes match the documented values."""
        assert consts.SpanAttributes.SPAN_KIND == "au.span.kind"
        assert consts.SpanAttributes.AGENT_NAME == "au.agent.name"
        assert consts.SpanAttributes.AGENT_ERROR_TYPE == "au.agent.error.type"
        assert consts.SpanAttributes.TRACE_CALLER_NAME == "au.trace.caller_name"

    def test_span_attributes_are_unique_and_prefixed(self):
        """Every span attribute is unique and starts with 'au.'."""
        attrs = _public_attrs(consts.SpanAttributes)
        values = [value for _, value in attrs]
        assert len(values) >= 15
        assert len(values) == len(set(values))
        assert all(value.startswith("au.") for value in values)


class TestMetricLabels:
    """Test the metric label constants."""

    def test_metric_labels_are_unique_and_prefixed(self):
        """Every label name is unique and starts with 'au_'."""
        attrs = _public_attrs(consts.MetricLabels)
        values = [value for _, value in attrs]
        assert len(values) == len(set(values))
        assert all(value.startswith("au_") for value in values)
        assert "au_agent_name" in values
        assert "au_agent_status" in values
