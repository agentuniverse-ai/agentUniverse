# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/6/10 14:40
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: consts.py


INSTRUMENTOR_NAME = "opentelemetry-instrumentation-agentuniverse-agent"
INSTRUMENTOR_VERSION = "0.1.0"


# Metric Names
class MetricNames:
    AGENT_CALLS_TOTAL = "agent_calls_total"
    AGENT_ERRORS_TOTAL = "agent_errors_total"
    AGENT_CALL_DURATION = "agent_call_duration"
    AGENT_FIRST_TOKEN_DURATION = "agent_first_token_duration"
    AGENT_TOTAL_TOKENS = "agent_total_tokens"
    AGENT_PROMPT_TOKENS = "agent_prompt_tokens"
    AGENT_COMPLETION_TOKENS = "agent_completion_tokens"
    AGENT_REASONING_TOKENS = "agent_reasoning_tokens"
    AGENT_CACHED_TOKENS = "agent_cached_tokens"


# Span Attribute Names
class SpanAttributes:
    # Agent attributes
    SPAN_KIND = "au.span.kind"
    AGENT_NAME = "au.agent.name"
    AGENT_INPUT = "au.agent.input"
    AGENT_OUTPUT = "au.agent.output"
    AGENT_DURATION = "au.agent.duration"
    AGENT_STATUS = "au.agent.status"
    AGENT_PAIR_ID = "au.agent.pair_id"
    AGENT_STREAMING = "au.agent.streaming"

    # First token attributes
    AGENT_FIRST_TOKEN_DURATION = "au.agent.first_token.duration"

    # Error attributes
    AGENT_ERROR_TYPE = "au.agent.error.type"
    AGENT_ERROR_MESSAGE = "au.agent.error.message"

    # Trace attributes
    TRACE_CALLER_NAME = "au.trace.caller_name"
    TRACE_CALLER_TYPE = "au.trace.caller_type"

    # Total token usage
    AGENT_USAGE_TOTAL_TOKENS = "au.agent.usage.total_tokens"
    AGENT_USAGE_PROMPT_TOKENS = "au.agent.usage.prompt_tokens"
    AGENT_USAGE_COMPLETION_TOKENS = "au.agent.usage.completion_tokens"
    AGENT_USAGE_DETAIL_TOKENS = "au.agent.usage.detail_tokens"


class MetricLabels:
    AGENT_NAME = "au_agent_name"
    CALLER_NAME = "au_trace_caller_name"
    CALLER_TYPE = "au_trace_caller_type"
    STATUS = "au_agent_status"
    STREAMING = "au_agent_streaming"
