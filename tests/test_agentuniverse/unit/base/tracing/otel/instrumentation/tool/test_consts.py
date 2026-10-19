# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_consts.py
"""Unit tests for the tool instrumentor constants."""

import pytest

from agentuniverse.base.tracing.otel.instrumentation.tool import consts


class TestToolInstrumentationConsts:
    """Test the metric, span attribute and label identifiers."""

    def test_instrumentor_metadata(self):
        """Instrumentor name and version keep their documented values."""
        assert consts.INSTRUMENTOR_NAME == (
            "opentelemetry-instrumentation-agentuniverse-tool"
        )
        assert consts.INSTRUMENTOR_VERSION == "0.1.0"

    def test_metric_names(self):
        """All exported metric names keep their wire values."""
        assert consts.MetricNames.TOOL_CALLS_TOTAL == "tool_calls_total"
        assert consts.MetricNames.TOOL_ERRORS_TOTAL == "tool_errors_total"
        assert consts.MetricNames.TOOL_CALL_DURATION == "tool_call_duration"
        assert consts.MetricNames.TOOL_TOTAL_TOKENS == "tool_total_tokens"
        assert consts.MetricNames.TOOL_PROMPT_TOKENS == "tool_prompt_tokens"
        assert consts.MetricNames.TOOL_COMPLETION_TOKENS == "tool_completion_tokens"
        assert consts.MetricNames.TOOL_REASONING_TOKENS == "tool_reasoning_tokens"
        assert consts.MetricNames.TOOL_CACHED_TOKENS == "tool_cached_tokens"

    def test_span_attributes(self):
        """All exported span attribute names keep their dotted values."""
        assert consts.SpanAttributes.SPAN_KIND == "au.span.kind"
        assert consts.SpanAttributes.TOOL_NAME == "au.tool.name"
        assert consts.SpanAttributes.TOOL_INPUT == "au.tool.input"
        assert consts.SpanAttributes.TOOL_OUTPUT == "au.tool.output"
        assert consts.SpanAttributes.TOOL_ERROR_TYPE == "au.tool.error.type"
        assert consts.SpanAttributes.TRACE_CALLER_NAME == "au.trace.caller_name"
        assert consts.SpanAttributes.TOOL_USAGE_TOTAL_TOKENS == (
            "au.tool.usage.total_tokens"
        )

    def test_metric_labels(self):
        """Metric label names keep their underscore-prefixed values."""
        assert consts.MetricLabels.TOOL_NAME == "au_tool_name"
        assert consts.MetricLabels.STATUS == "au_tool_status"
        assert consts.MetricLabels.CALLER_NAME == "au_trace_caller_name"
        assert consts.MetricLabels.CALLER_TYPE == "au_trace_caller_type"

    @pytest.mark.parametrize(
        "attribute",
        [
            consts.SpanAttributes.TOOL_NAME,
            consts.SpanAttributes.TOOL_INPUT,
            consts.SpanAttributes.TOOL_OUTPUT,
            consts.SpanAttributes.TOOL_USAGE_PROMPT_TOKENS,
        ],
    )
    def test_span_attributes_use_au_prefix(self, attribute):
        """Every tool span attribute is namespaced under au."""
        assert attribute.startswith("au.")
