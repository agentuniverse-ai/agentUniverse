# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for agent instrumentation constants.

The module under test only declares instrumentor metadata, metric names,
span attribute names and metric label names; these tests lock the public
constant values and their namespacing so renaming does not go unnoticed.
"""

from agentuniverse.base.tracing.otel.instrumentation.agent.consts import (
    INSTRUMENTOR_NAME,
    INSTRUMENTOR_VERSION,
    MetricLabels,
    MetricNames,
    SpanAttributes,
)


class TestInstrumentorMetadata:
    def test_instrumentor_name(self):
        assert INSTRUMENTOR_NAME == "opentelemetry-instrumentation-agentuniverse-agent"

    def test_instrumentor_version(self):
        assert INSTRUMENTOR_VERSION == "0.1.0"


class TestMetricNames:
    def test_call_counters_exist(self):
        assert MetricNames.AGENT_CALLS_TOTAL == "agent_calls_total"
        assert MetricNames.AGENT_ERRORS_TOTAL == "agent_errors_total"

    def test_duration_and_token_metrics(self):
        assert MetricNames.AGENT_CALL_DURATION == "agent_call_duration"
        assert MetricNames.AGENT_FIRST_TOKEN_DURATION == "agent_first_token_duration"
        assert MetricNames.AGENT_TOTAL_TOKENS == "agent_total_tokens"
        assert MetricNames.AGENT_PROMPT_TOKENS == "agent_prompt_tokens"
        assert MetricNames.AGENT_COMPLETION_TOKENS == "agent_completion_tokens"
        assert MetricNames.AGENT_REASONING_TOKENS == "agent_reasoning_tokens"
        assert MetricNames.AGENT_CACHED_TOKENS == "agent_cached_tokens"


class TestSpanAttributes:
    def test_span_kind_and_agent_attributes(self):
        assert SpanAttributes.SPAN_KIND == "au.span.kind"
        assert SpanAttributes.AGENT_NAME == "au.agent.name"
        assert SpanAttributes.AGENT_INPUT == "au.agent.input"
        assert SpanAttributes.AGENT_OUTPUT == "au.agent.output"
        assert SpanAttributes.AGENT_STATUS == "au.agent.status"
        assert SpanAttributes.AGENT_STREAMING == "au.agent.streaming"

    def test_error_attributes(self):
        assert SpanAttributes.AGENT_ERROR_TYPE == "au.agent.error.type"
        assert SpanAttributes.AGENT_ERROR_MESSAGE == "au.agent.error.message"

    def test_usage_attributes(self):
        assert SpanAttributes.AGENT_USAGE_TOTAL_TOKENS == "au.agent.usage.total_tokens"
        assert SpanAttributes.AGENT_USAGE_PROMPT_TOKENS == "au.agent.usage.prompt_tokens"
        assert SpanAttributes.AGENT_USAGE_COMPLETION_TOKENS == "au.agent.usage.completion_tokens"
        assert SpanAttributes.AGENT_USAGE_DETAIL_TOKENS == "au.agent.usage.detail_tokens"


class TestMetricLabels:
    def test_label_values(self):
        assert MetricLabels.AGENT_NAME == "au_agent_name"
        assert MetricLabels.CALLER_NAME == "au_trace_caller_name"
        assert MetricLabels.CALLER_TYPE == "au_trace_caller_type"
        assert MetricLabels.STATUS == "au_agent_status"
        assert MetricLabels.STREAMING == "au_agent_streaming"
