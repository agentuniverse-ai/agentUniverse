# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/02/10 10:30
# @Author  : Yue Wang
# @FileName: test_consts.py
"""Unit tests for the LLM instrumentation constants."""

from agentuniverse.base.tracing.otel.instrumentation.llm.consts import (
    INSTRUMENTOR_NAME,
    INSTRUMENTOR_VERSION,
    MetricLabels,
    MetricNames,
    SpanAttributes,
)


class TestInstrumentorMetadata:
    """Validate the instrumentor name/version metadata."""

    def test_instrumentor_name(self):
        """The instrumentor name must identify the AU LLM package."""
        assert INSTRUMENTOR_NAME == "opentelemetry-instrumentation-agentuniverse-llm"

    def test_instrumentor_version(self):
        """The instrumentor version must be a non-empty string."""
        assert INSTRUMENTOR_VERSION == "0.1.0"


class TestMetricNames:
    """Validate the metric name constants."""

    def test_metric_names_values(self):
        """Metric names must use the expected dot-separated labels."""
        assert MetricNames.LLM_CALLS_TOTAL == "llm_calls_total"
        assert MetricNames.LLM_ERRORS_TOTAL == "llm_errors_total"
        assert MetricNames.LLM_CALL_DURATION == "llm_call_duration"
        assert MetricNames.LLM_FIRST_TOKEN_DURATION == "llm_first_token_duration"
        assert MetricNames.LLM_TOTAL_TOKENS == "llm_total_tokens"
        assert MetricNames.LLM_PROMPT_TOKENS == "llm_prompt_tokens"
        assert MetricNames.LLM_COMPLETION_TOKENS == "llm_completion_tokens"
        assert MetricNames.LLM_REASONING_TOKENS == "llm_reasoning_tokens"
        assert MetricNames.LLM_CACHED_TOKENS == "llm_cached_tokens"

    def test_metric_names_unique(self):
        """All metric names must be distinct."""
        names = [v for k, v in vars(MetricNames).items() if isinstance(v, str) and not k.startswith('__')]
        assert len(names) == len(set(names)) == 9


class TestSpanAttributes:
    """Validate the span attribute name constants."""

    def test_span_kind_and_llm_attributes(self):
        """Core span kind and llm attributes must keep their prefixes."""
        assert SpanAttributes.SPAN_KIND == "au.span.kind"
        assert SpanAttributes.AU_LLM_NAME == "au.llm.name"
        assert SpanAttributes.AU_LLM_CHANNEL_NAME == "au.llm.channel_name"
        assert SpanAttributes.AU_LLM_INPUT == "au.llm.input"
        assert SpanAttributes.AU_LLM_OUTPUT == "au.llm.output"
        assert SpanAttributes.AU_LLM_STREAMING == "au.llm.streaming"

    def test_span_attributes_unique(self):
        """All span attribute names must be distinct."""
        attrs = [v for k, v in vars(SpanAttributes).items() if isinstance(v, str) and not k.startswith('__')]
        assert len(attrs) == len(set(attrs))


class TestMetricLabels:
    """Validate the metric label constants."""

    def test_metric_label_values(self):
        """Metric labels must keep the au_llm_ prefix convention."""
        assert MetricLabels.STATUS == "au_llm_status"
        assert MetricLabels.STREAMING == "au_llm_streaming"
        assert MetricLabels.LLM_NAME == "au_llm_name"
        assert MetricLabels.CHANNEL_NAME == "au_llm_channel_name"
        assert MetricLabels.CALLER_NAME == "au_trace_caller_name"
        assert MetricLabels.CALLER_TYPE == "au_trace_caller_type"

    def test_metric_labels_unique(self):
        """All metric label names must be distinct."""
        labels = [v for k, v in vars(MetricLabels).items() if isinstance(v, str) and not k.startswith('__')]
        assert len(labels) == len(set(labels)) == 6
