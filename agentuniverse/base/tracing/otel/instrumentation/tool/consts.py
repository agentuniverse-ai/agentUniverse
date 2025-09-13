# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/6/10 15:01
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: consts.py


# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/6/9 14:55
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: tool_constants.py

"""
Constants for Tool instrumentor metrics and attributes.
"""

# Instrumentor metadata
INSTRUMENTOR_NAME = "opentelemetry-instrumentation-agentuniverse-tool"
INSTRUMENTOR_VERSION = "0.1.0"


# Metric names
class MetricNames:
    TOOL_CALLS_TOTAL = "tool_calls_total"
    TOOL_ERRORS_TOTAL = "tool_errors_total"
    TOOL_CALL_DURATION = "tool_call_duration"
    TOOL_TOTAL_TOKENS = "tool_total_tokens"
    TOOL_PROMPT_TOKENS = "tool_prompt_tokens"
    TOOL_COMPLETION_TOKENS = "tool_completion_tokens"
    TOOL_REASONING_TOKENS = "tool_reasoning_tokens"
    TOOL_CACHED_TOKENS = "tool_cached_tokens"


# Span attribute names
class SpanAttributes:
    # Tool-specific attributes
    SPAN_KIND = "au.span.kind"
    TOOL_NAME = "au.tool.name"
    TOOL_INPUT = "au.tool.input"
    TOOL_OUTPUT = "au.tool.output"
    TOOL_DURATION = "au.tool.duration"
    TOOL_STATUS = "au.tool.status"
    TOOL_PAIR_ID = "au.tool.pair_id"

    # Error attributes
    TOOL_ERROR_TYPE = "au.tool.error.type"
    TOOL_ERROR_MESSAGE = "au.tool.error.message"

    # Trace attributes
    TRACE_CALLER_NAME = "au.trace.caller_name"
    TRACE_CALLER_TYPE = "au.trace.caller_type"

    # Total token usage
    TOOL_USAGE_TOTAL_TOKENS = "au.tool.usage.total_tokens"
    TOOL_USAGE_PROMPT_TOKENS = "au.tool.usage.prompt_tokens"
    TOOL_USAGE_COMPLETION_TOKENS = "au.tool.usage.completion_tokens"
    TOOL_USAGE_DETAIL_TOKENS = "au.tool.usage.detail_tokens"


# Label names for metrics
class MetricLabels:
    TOOL_NAME = "au_tool_name"
    STATUS = "au_tool_status"
    CALLER_NAME = "au_trace_caller_name"
    CALLER_TYPE = "au_trace_caller_type"
