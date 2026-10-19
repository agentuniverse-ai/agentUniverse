# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for tool instrumentation constants.

The module under test only declares instrumentor metadata, metric names,
span attribute names and metric label names; these tests lock the public
constant values so accidental renaming is caught early.
"""

from agentuniverse.base.tracing.otel.instrumentation.tool.consts import (
    INSTRUMENTOR_NAME,
    INSTRUMENTOR_VERSION,
    MetricLabels,
    MetricNames,
    SpanAttributes,
)


class TestInstrumentorMetadata:
    def test_instrumentor_name(self):
        assert INSTRUMENTOR_NAME == "opentelemetry-instrumentation-agentuniverse-tool"

    def test_instrumentor_version(self):
        assert INSTRUMENTOR_VERSION == "0.1.0"


class TestMetricNames:
    def test_call_counters_exist(self):
        assert MetricNames.TOOL_CALLS_TOTAL == "tool_calls_total"
        assert MetricNames.TOOL_ERRORS_TOTAL == "tool_errors_total"

    def test_duration_and_token_metrics(self):
        assert MetricNames.TOOL_CALL_DURATION == "tool_call_duration"
        assert MetricNames.TOOL_TOTAL_TOKENS == "tool_total_tokens"
        assert MetricNames.TOOL_PROMPT_TOKENS == "tool_prompt_tokens"
        assert MetricNames.TOOL_COMPLETION_TOKENS == "tool_completion_tokens"
        assert MetricNames.TOOL_REASONING_TOKENS == "tool_reasoning_tokens"
        assert MetricNames.TOOL_CACHED_TOKENS == "tool_cached_tokens"


class TestSpanAttributes:
    def test_span_kind_and_tool_attributes(self):
        assert SpanAttributes.SPAN_KIND == "au.span.kind"
        assert SpanAttributes.TOOL_NAME == "au.tool.name"
        assert SpanAttributes.TOOL_INPUT == "au.tool.input"
        assert SpanAttributes.TOOL_OUTPUT == "au.tool.output"
        assert SpanAttributes.TOOL_DURATION == "au.tool.duration"
        assert SpanAttributes.TOOL_STATUS == "au.tool.status"
        assert SpanAttributes.TOOL_PAIR_ID == "au.tool.pair_id"

    def test_error_attributes(self):
        assert SpanAttributes.TOOL_ERROR_TYPE == "au.tool.error.type"
        assert SpanAttributes.TOOL_ERROR_MESSAGE == "au.tool.error.message"

    def test_usage_attributes(self):
        assert SpanAttributes.TOOL_USAGE_TOTAL_TOKENS == "au.tool.usage.total_tokens"
        assert SpanAttributes.TOOL_USAGE_PROMPT_TOKENS == "au.tool.usage.prompt_tokens"
        assert SpanAttributes.TOOL_USAGE_COMPLETION_TOKENS == "au.tool.usage.completion_tokens"
        assert SpanAttributes.TOOL_USAGE_DETAIL_TOKENS == "au.tool.usage.detail_tokens"


class TestMetricLabels:
    def test_label_values(self):
        assert MetricLabels.TOOL_NAME == "au_tool_name"
        assert MetricLabels.CALLER_NAME == "au_trace_caller_name"
        assert MetricLabels.CALLER_TYPE == "au_trace_caller_type"
        assert MetricLabels.STATUS == "au_tool_status"
