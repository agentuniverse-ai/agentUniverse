# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/13 10:00
# @Author  : kaichuan
# @FileName: test_consts.py
"""Unit tests for the LLM instrumentation constants module."""

import pytest

from agentuniverse.base.tracing.otel.instrumentation.llm import consts


def _class_values(cls) -> list:
    """Collect the string constant values declared on a class."""
    return [v for k, v in vars(cls).items() if not k.startswith("__")
            and isinstance(v, str)]


class TestInstrumentorIdentity:
    """Test the top-level instrumentor identity constants."""

    def test_instrumentor_name(self):
        """INSTRUMENTOR_NAME matches the expected package identifier."""
        assert consts.INSTRUMENTOR_NAME == (
            "opentelemetry-instrumentation-agentuniverse-llm")

    def test_instrumentor_version(self):
        """INSTRUMENTOR_VERSION is a semantic version string."""
        assert consts.INSTRUMENTOR_VERSION == "0.1.0"


class TestMetricNames:
    """Test the metric name constants."""

    def test_metric_name_values(self):
        """Core metric names carry their documented values."""
        assert consts.MetricNames.LLM_CALLS_TOTAL == "llm_calls_total"
        assert consts.MetricNames.LLM_ERRORS_TOTAL == "llm_errors_total"
        assert consts.MetricNames.LLM_TOTAL_TOKENS == "llm_total_tokens"
        assert consts.MetricNames.LLM_FIRST_TOKEN_DURATION == (
            "llm_first_token_duration")

    def test_metric_names_are_unique(self):
        """No two metric names collide."""
        values = _class_values(consts.MetricNames)
        assert len(values) == len(set(values))


class TestSpanAttributes:
    """Test the span attribute name constants."""

    def test_span_attribute_values(self):
        """A representative set of span attributes carry exact values."""
        assert consts.SpanAttributes.SPAN_KIND == "au.span.kind"
        assert consts.SpanAttributes.AU_LLM_NAME == "au.llm.name"
        assert consts.SpanAttributes.AU_LLM_OUTPUT == "au.llm.output"
        assert consts.SpanAttributes.AU_LLM_STATUS == "au.llm.status"

    def test_span_attributes_follow_au_prefix(self):
        """Every span attribute uses the 'au.' namespace prefix."""
        for value in _class_values(consts.SpanAttributes):
            assert value.startswith("au.")

    def test_span_attributes_are_unique(self):
        """No two span attribute names collide."""
        values = _class_values(consts.SpanAttributes)
        assert len(values) == len(set(values))


class TestMetricLabels:
    """Test the metric label name constants."""

    def test_metric_label_values(self):
        """Metric labels carry their documented values."""
        assert consts.MetricLabels.STATUS == "au_llm_status"
        assert consts.MetricLabels.LLM_NAME == "au_llm_name"
        assert consts.MetricLabels.CALLER_TYPE == "au_trace_caller_type"

    def test_metric_labels_are_unique(self):
        """No two metric label names collide."""
        values = _class_values(consts.MetricLabels)
        assert len(values) == len(set(values))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
