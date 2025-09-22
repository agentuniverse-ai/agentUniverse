# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/6/9 14:55
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: tool_instrumentor.py

"""
OpenTelemetry instrumentor for Tool calls in AgentUniverse.

This instrumentor automatically creates spans and metrics for Tool invocations
decorated with @trace_tool.
"""
import base64
import datetime
import decimal
import json
import time
import traceback
from typing import Any, Dict, Optional

from opentelemetry import trace, metrics, context
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import Status, StatusCode, Span

from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.memory.conversation_memory.conversation_memory_module import \
    ConversationMemoryModule
from agentuniverse.base.annotation.trace import _get_tool_info, \
    InvocationChainContext
from agentuniverse.base.tracing.au_trace_manager import init_new_token_usage, \
    get_current_token_usage, add_current_token_usage_to_parent
from .consts import (
    INSTRUMENTOR_NAME,
    INSTRUMENTOR_VERSION,
    MetricNames,
    MetricLabels,
    SpanAttributes
)


def _fallback(o):
    """JSON serialization fallback for complex types."""
    if isinstance(o, ToolInput):
        return o.to_json_str()
    if isinstance(o, (datetime.datetime, datetime.date)):
        return o.isoformat()
    if isinstance(o, bytes):
        return base64.b64encode(o).decode()
    if isinstance(o, (set, frozenset)):
        return list(o)
    if isinstance(o, decimal.Decimal):
        return float(o)
    return str(o)


def safe_json_dumps(obj, *, indent=None, ensure_ascii=False) -> str:
    """Safely serialize object to JSON string."""
    try:
        return json.dumps(
            obj,
            default=_fallback,
            indent=indent,
            ensure_ascii=ensure_ascii
        )
    except Exception:
        return str(obj)


class ToolSpanManager:
    """Manager for Tool span lifecycle."""

    def __init__(self, tracer: trace.Tracer, span_name: str):
        self.tracer = tracer
        self.span_name = span_name
        self.span: Optional[Span] = None
        self.token = None

    def start_span(self) -> Span:
        """Start a new span and return it."""
        self.span = self.tracer.start_span(
            name=self.span_name,
            kind=trace.SpanKind.INTERNAL,
            context=context.get_current()
        )
        self.token = context.attach(trace.set_span_in_context(self.span))
        init_new_token_usage()
        return self.span

    def cleanup(self):
        """Cleanup span and context."""
        add_current_token_usage_to_parent()
        if self.span:
            self.span.end()
            self.span = None
        if self.token:
            context.detach(self.token)
            self.token = None

    def __enter__(self) -> Span:
        return self.start_span()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class ToolMetricsRecorder:
    """Handles Tool metrics recording."""

    def __init__(self, metrics: Dict[str, Any]):
        self.metrics = metrics

    def record_call_start(self, labels: Dict[str, str]) -> None:
        """Record start of Tool call."""
        self.metrics[MetricNames.TOOL_CALLS_TOTAL].add(1, labels)

    def record_duration(self, duration: float, labels: Dict[str, str]) -> None:
        """Record call duration."""
        self.metrics[MetricNames.TOOL_CALL_DURATION].record(duration, labels)

    def record_error(self, error: Exception, duration: float,
                     labels: Dict[str, str]) -> None:
        """Record error metrics."""
        error_labels = {**labels}
        error_labels[MetricLabels.STATUS] = type(error).__name__
        self.metrics[MetricNames.TOOL_ERRORS_TOTAL].add(1, error_labels)
        self.metrics[MetricNames.TOOL_CALL_DURATION].record(duration, error_labels)

    def record_total_token_usage(self, labels: Dict[str, str]) -> None:
        """Record start of Agent call."""
        self.metrics[MetricNames.TOOL_TOTAL_TOKENS].record(get_current_token_usage().total_tokens, labels)
        self.metrics[MetricNames.TOOL_PROMPT_TOKENS].record(get_current_token_usage().prompt_tokens, labels)
        self.metrics[MetricNames.TOOL_COMPLETION_TOKENS].record(
            get_current_token_usage().completion_tokens, labels)
        self.metrics[MetricNames.TOOL_REASONING_TOKENS].record(
            get_current_token_usage().reasoning_tokens, labels)
        self.metrics[MetricNames.TOOL_CACHED_TOKENS].record(
            get_current_token_usage().cached_tokens, labels)


class ToolSpanAttributesSetter:
    """Handles setting span attributes."""

    @staticmethod
    def set_input_attributes(span: Span, source_name: str,
                             input_params: Dict[str, Any],
                             caller_info: Dict[str, Any],
                             pair_id: str) -> None:
        """Set input-related span attributes."""
        span.set_attribute(SpanAttributes.SPAN_KIND, "tool")
        span.set_attribute(SpanAttributes.TOOL_NAME, source_name)
        span.set_attribute(SpanAttributes.TOOL_INPUT,
                           safe_json_dumps(input_params, ensure_ascii=False))
        span.set_attribute(SpanAttributes.TRACE_CALLER_NAME,
                           caller_info.get('source', 'unknown'))
        span.set_attribute(SpanAttributes.TRACE_CALLER_TYPE,
                           caller_info.get('type', 'user'))
        span.set_attribute(SpanAttributes.TOOL_PAIR_ID, pair_id)

    @staticmethod
    def set_success_attributes(span: Span, duration: float,
                               result: Any) -> None:
        """Set success-related span attributes."""
        span.set_attribute(SpanAttributes.TOOL_DURATION, duration)
        span.set_attribute(SpanAttributes.TOOL_STATUS, "success")
        span.set_attribute(SpanAttributes.TOOL_OUTPUT,
                           safe_json_dumps(result, ensure_ascii=False))
        span.set_attribute(SpanAttributes.TOOL_USAGE_TOTAL_TOKENS, get_current_token_usage().total_tokens)
        span.set_attribute(SpanAttributes.TOOL_USAGE_COMPLETION_TOKENS,
                           get_current_token_usage().completion_tokens)
        span.set_attribute(SpanAttributes.TOOL_USAGE_PROMPT_TOKENS,
                           get_current_token_usage().prompt_tokens)
        span.set_attribute(SpanAttributes.TOOL_USAGE_DETAIL_TOKENS, safe_json_dumps(
            get_current_token_usage().to_dict()))

    @staticmethod
    def set_error_attributes(span: Span, error: Exception,
                             duration: float) -> None:
        """Set error-related span attributes."""
        error_str = ''.join(traceback.format_exception(type(error), error,
                                                       error.__traceback__))
        span.set_attribute(SpanAttributes.TOOL_STATUS, "error")
        span.set_attribute(SpanAttributes.TOOL_ERROR_TYPE, type(error).__name__)
        span.set_attribute(SpanAttributes.TOOL_ERROR_MESSAGE, error_str)
        span.set_attribute(SpanAttributes.TOOL_DURATION, duration)
        span.set_status(Status(StatusCode.ERROR, str(error)))
        span.set_attribute(SpanAttributes.TOOL_USAGE_TOTAL_TOKENS,
                           get_current_token_usage().total_tokens)
        span.set_attribute(SpanAttributes.TOOL_USAGE_COMPLETION_TOKENS,
                           get_current_token_usage().completion_tokens)
        span.set_attribute(SpanAttributes.TOOL_USAGE_PROMPT_TOKENS,
                           get_current_token_usage().prompt_tokens)
        span.set_attribute(SpanAttributes.TOOL_USAGE_DETAIL_TOKENS, safe_json_dumps(
            get_current_token_usage().to_dict()))


class ToolInstrumentor(BaseInstrumentor):
    """OpenTelemetry instrumentor for Tool calls."""

    def __init__(self):
        super().__init__()
        self._tracer: Optional[trace.Tracer] = None
        self._meter: Optional[metrics.Meter] = None
        self._metrics: Dict[str, Any] = {}
        self._metrics_recorder: Optional[ToolMetricsRecorder] = None
        self._original_tool_wrapper_sync = None
        self._original_tool_wrapper_async = None

    def instrumentation_dependencies(self):
        return []

    def _instrument(self, **kwargs):
        """Instrument Tool tracing."""
        tracer_provider = kwargs.get("tracer_provider")
        meter_provider = kwargs.get("meter_provider")

        self._tracer = trace.get_tracer(INSTRUMENTOR_NAME,
                                        INSTRUMENTOR_VERSION, tracer_provider)
        self._meter = metrics.get_meter(INSTRUMENTOR_NAME,
                                        INSTRUMENTOR_VERSION, meter_provider)

        self._setup_metrics()
        self._patch_trace_tool()

    def _uninstrument(self, **kwargs):
        """Remove instrumentation."""
        try:
            from agentuniverse.base.annotation import trace as trace_module
            setattr(trace_module, '_tool_wrapper_async',
                    self._original_tool_wrapper_async)
            setattr(trace_module, '_tool_wrapper_sync',
                    self._original_tool_wrapper_sync)
        except ImportError:
            pass

    def _setup_metrics(self):
        """Setup Tool-specific metrics."""
        self._metrics = {
            MetricNames.TOOL_CALLS_TOTAL: self._meter.create_counter(
                name=MetricNames.TOOL_CALLS_TOTAL,
                description="Total number of Tool calls",
                unit="1"
            ),
            MetricNames.TOOL_ERRORS_TOTAL: self._meter.create_counter(
                name=MetricNames.TOOL_ERRORS_TOTAL,
                description="Total number of Tool errors",
                unit="1"
            ),
            MetricNames.TOOL_CALL_DURATION: self._meter.create_histogram(
                name=MetricNames.TOOL_CALL_DURATION,
                description="Duration of Tool calls in seconds",
                unit="s"
            ),
            MetricNames.TOOL_TOTAL_TOKENS: self._meter.create_histogram(
                name=MetricNames.TOOL_TOTAL_TOKENS,
                description="Total token used in tool call",
                unit="1"
            ),
            MetricNames.TOOL_COMPLETION_TOKENS: self._meter.create_histogram(
                name=MetricNames.TOOL_COMPLETION_TOKENS,
                description="Completion token used in tool call",
                unit="1"
            ),
            MetricNames.TOOL_PROMPT_TOKENS: self._meter.create_histogram(
                name=MetricNames.TOOL_PROMPT_TOKENS,
                description="Prompt token used in tool call",
                unit="1"
            ),
            MetricNames.TOOL_CACHED_TOKENS: self._meter.create_histogram(
                name=MetricNames.TOOL_CACHED_TOKENS,
                description="Cached token used in tool call",
                unit="1"
            ),
            MetricNames.TOOL_REASONING_TOKENS: self._meter.create_histogram(
                name=MetricNames.TOOL_REASONING_TOKENS,
                description="Reasoning token used in tool call",
                unit="1"
            )
        }
        self._metrics_recorder = ToolMetricsRecorder(self._metrics)

    def _patch_trace_tool(self):
        """Patch the trace_tool decorator."""
        try:
            from agentuniverse.base.annotation import trace as trace_module
            self._original_tool_wrapper_async = getattr(trace_module,
                                                        '_tool_wrapper_async',
                                                        None)
            self._original_tool_wrapper_sync = getattr(trace_module,
                                                       '_tool_wrapper_sync',
                                                       None)
            setattr(trace_module, '_tool_wrapper_async',
                    self._wrap_async_tool_function)
            setattr(trace_module, '_tool_wrapper_sync',
                    self._wrap_sync_tool_function)
        except ImportError:
            pass

    async def _wrap_async_tool_function(self, func, *args, **kwargs):
        """Wrap async Tool function with OTEL tracing and metrics."""
        tool_instance, source, tool_input, start_info, pair_id = _get_tool_info(
            func, *args, **kwargs)

        labels = {
            MetricLabels.TOOL_NAME: source,
            MetricLabels.CALLER_NAME: start_info.get('source', 'unknown'),
            MetricLabels.CALLER_TYPE: start_info.get('type', 'user'),
            MetricLabels.STATUS: "success"
        }

        span_manager = ToolSpanManager(self._tracer, f"au.tool.{source}")
        start_time = time.time()
        span = span_manager.start_span()

        with InvocationChainContext(source=source, node_type='tool'):
            try:
                ToolSpanAttributesSetter.set_input_attributes(
                    span, source, tool_input, start_info, pair_id)

                self._metrics_recorder.record_call_start(labels)

                # Record memory input operation
                ConversationMemoryModule().add_tool_input_info(
                    start_info, source, tool_input, pair_id)

                # Execute the tool function
                result = await func(*args, **kwargs)

                # Record memory output operation
                ConversationMemoryModule().add_tool_output_info(
                    start_info, source, params=result, pair_id=pair_id)

                duration = time.time() - start_time
                self._metrics_recorder.record_duration(duration, labels)
                self._metrics_recorder.record_total_token_usage(labels)
                ToolSpanAttributesSetter.set_success_attributes(
                    span, duration, result)

                return result

            except Exception as e:
                duration = time.time() - start_time
                self._metrics_recorder.record_error(e, duration, labels)
                self._metrics_recorder.record_total_token_usage(labels)
                ToolSpanAttributesSetter.set_error_attributes(
                    span_manager.span, e, duration)
                raise

            finally:
                span_manager.cleanup()

    def _wrap_sync_tool_function(self, func, *args, **kwargs):
        """Wrap sync Tool function with OTEL tracing and metrics."""
        tool_instance, source, tool_input, start_info, pair_id = _get_tool_info(
            func, *args, **kwargs)

        labels = {
            MetricLabels.TOOL_NAME: source,
            MetricLabels.CALLER_NAME: start_info.get('source', 'unknown'),
            MetricLabels.CALLER_TYPE: start_info.get('type', 'user'),
            MetricLabels.STATUS: "success"
        }

        span_manager = ToolSpanManager(self._tracer, f"au.tool.{source}")
        start_time = time.time()
        span = span_manager.start_span()

        with InvocationChainContext(source=source, node_type='tool'):
            try:
                ToolSpanAttributesSetter.set_input_attributes(
                    span, source, tool_input, start_info, pair_id)

                self._metrics_recorder.record_call_start(labels)

                # Record memory input operation
                ConversationMemoryModule().add_tool_input_info(
                    start_info, source, tool_input, pair_id)

                # Execute the tool function
                result = func(*args, **kwargs)

                # Record memory output operation
                ConversationMemoryModule().add_tool_output_info(
                    start_info, source, params=result, pair_id=pair_id)

                duration = time.time() - start_time
                self._metrics_recorder.record_duration(duration, labels)
                self._metrics_recorder.record_total_token_usage(labels)
                ToolSpanAttributesSetter.set_success_attributes(
                    span, duration, result)

                return result

            except Exception as e:
                duration = time.time() - start_time
                self._metrics_recorder.record_error(e, duration, labels)
                self._metrics_recorder.record_total_token_usage(labels)
                ToolSpanAttributesSetter.set_error_attributes(
                    span_manager.span, e, duration)
                raise

            finally:
                span_manager.cleanup()
