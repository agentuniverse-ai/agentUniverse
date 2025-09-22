# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/6/10 15:01
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: consts.py


INSTRUMENTOR_NAME = "opentelemetry-instrumentation-agentuniverse-llm"
INSTRUMENTOR_VERSION = "0.1.0"


# Metric names
class MetricNames:
    """Metric name constants."""
    LLM_CALLS_TOTAL = "llm_calls_total"
    LLM_ERRORS_TOTAL = "llm_errors_total"
    LLM_CALL_DURATION = "llm_call_duration"
    LLM_FIRST_TOKEN_DURATION = "llm_first_token_duration"
    LLM_TOTAL_TOKENS = "llm_total_tokens"
    LLM_PROMPT_TOKENS = "llm_prompt_tokens"
    LLM_COMPLETION_TOKENS = "llm_completion_tokens"
    LLM_REASONING_TOKENS = "llm_reasoning_tokens"
    LLM_CACHED_TOKENS = "llm_cached_tokens"


# Span attribute names
class SpanAttributes:
    """Span attribute name constants."""
    # Basic span attributes
    SPAN_KIND = "au.span.kind"
    AU_LLM_NAME = "au.llm.name"
    AU_LLM_CHANNEL_NAME = "au.llm.channel_name"
    AU_LLM_INPUT = "au.llm.input"
    AU_LLM_OUTPUT = "au.llm.output"
    AU_LLM_LLM_PARAMS = "au.llm.llm_params"
    AU_LLM_STREAMING = "au.llm.streaming"
    # Trace attributes
    AU_TRACE_CALLER_NAME = "au.trace.caller_name"
    AU_TRACE_CALLER_TYPE = "au.trace.caller_type"

    # Status and timing attributes
    AU_LLM_DURATION = "au.llm.duration"
    AU_LLM_STATUS = "au.llm.status"
    AU_LLM_FIRST_TOKEN_DURATION = "au.llm.first_token.duration"

    # Token usage attributes
    AU_LLM_USAGE_PROMPT_TOKENS = "au.llm.usage.prompt_tokens"
    AU_LLM_USAGE_COMPLETION_TOKENS = "au.llm.usage.completion_tokens"
    AU_LLM_USAGE_TOTAL_TOKENS = "au.llm.usage.total_tokens"
    AU_LLM_USAGE_DETAIL_TOKENS = "au.llm.usage.detail_tokens"

    # Error attributes
    AU_LLM_ERROR_TYPE = "au.llm.error.type"
    AU_LLM_ERROR_MESSAGE = "au.llm.error.message"


# Metric label names
class MetricLabels:
    """Metric label name constants."""
    STATUS = "au_llm_status"
    STREAMING = "au_llm_streaming"
    LLM_NAME = "au_llm_name"
    CHANNEL_NAME = "au_llm_channel_name"
    CALLER_NAME = "au_trace_caller_name"
    CALLER_TYPE = "au_trace_caller_type"
