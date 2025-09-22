# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/6/5 17:58
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: agent_instrumentor.py

"""
OpenTelemetry instrumentor for Agent calls in AgentUniverse.

This instrumentor automatically creates spans and metrics for Agent invocations
decorated with @trace_agent.
"""
import asyncio
import base64
import datetime
import decimal
import json
import queue
import time
import traceback
from typing import Any, Dict, Optional

from opentelemetry import trace, metrics, context
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import Status, StatusCode, Span

from agentuniverse.agent.memory.conversation_memory.conversation_memory_module import \
    ConversationMemoryModule
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.annotation.trace import _get_agent_info, \
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


class QueueWrapper:
    """Minimal wrapper for synchronous queue to monitor first token time."""

    def __init__(self, original_queue: queue.Queue, callback_on_first_put):
        self._queue = original_queue
        self._first_put_time = None
        self._callback = callback_on_first_put

    def put(self, item, block=True, timeout=None):
        """Put an item into the queue, recording first put time."""

        if self._first_put_time is None:
            self._first_put_time = time.time()
            self._callback(self._first_put_time)
        return self._queue.put(item, block, timeout)

    def put_nowait(self, item):
        """Put an item into the queue without blocking."""
        if self._first_put_time is None:
            self._first_put_time = time.time()
            self._callback(self._first_put_time)
        return self._queue.put_nowait(item)

    # Delegate all other methods to the original queue
    def __getattr__(self, name):
        return getattr(self._queue, name)


class AsyncQueueWrapper:
    """Wrapper for asynchronous queue to monitor first token time."""

    def __init__(self, original_queue: asyncio.Queue, callback_on_first_put):
        self._queue = original_queue
        self._first_put_time = None
        self._callback = callback_on_first_put

    async def put(self, item):
        """Put an item into the queue, recording first put time."""
        if self._first_put_time is None:
            self._first_put_time = time.time()
            self._callback(self._first_put_time)
        return await self._queue.put(item)

    def put_nowait(self, item):
        """Put an item into the queue without blocking."""
        if self._first_put_time is None:
            self._first_put_time = time.time()
            self._callback(self._first_put_time)
        return self._queue.put_nowait(item)

    # Delegate all other methods to the original queue
    def __getattr__(self, name):
        return getattr(self._queue, name)


class AgentSpanManager:
    """Manager for Agent span lifecycle."""

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
        # init_token_count
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


class AgentMetricsRecorder:
    """Handles Agent metrics recording."""

    def __init__(self, metrics: Dict[str, Any]):
        self.metrics = metrics

    def record_call_start(self, labels: Dict[str, str]) -> None:
        """Record start of Agent call."""
        self.metrics[MetricNames.AGENT_CALLS_TOTAL].add(1, labels)

    def record_first_token(self, duration: float,
                           labels: Dict[str, str]) -> None:
        """Record start of Agent call."""
        self.metrics[MetricNames.AGENT_FIRST_TOKEN_DURATION].record(duration, labels)

    def record_duration(self, duration: float, labels: Dict[str, str]) -> None:
        """Record call duration."""
        self.metrics[MetricNames.AGENT_CALL_DURATION].record(duration, labels)

    def record_error(self, error: Exception, duration: float,
                     labels: Dict[str, str]) -> None:
        """Record error metrics."""
        error_labels = {**labels}
        error_labels[MetricLabels.STATUS] = type(error).__name__
        self.metrics[MetricNames.AGENT_ERRORS_TOTAL].add(1, error_labels)
        self.metrics[MetricNames.AGENT_CALL_DURATION].record(duration, error_labels)

    def record_total_token_usage(self, labels: Dict[str, str]) -> None:
        """Record start of Agent call."""
        self.metrics[MetricNames.AGENT_TOTAL_TOKENS].record(
            get_current_token_usage().total_tokens, labels)
        self.metrics[MetricNames.AGENT_COMPLETION_TOKENS].record(
            get_current_token_usage().completion_tokens, labels)
        self.metrics[MetricNames.AGENT_PROMPT_TOKENS].record(
            get_current_token_usage().prompt_tokens, labels)
        self.metrics[MetricNames.AGENT_CACHED_TOKENS].record(
            get_current_token_usage().cached_tokens, labels)
        self.metrics[MetricNames.AGENT_REASONING_TOKENS].record(
            get_current_token_usage().reasoning_tokens, labels)


class AgentSpanAttributesSetter:
    """Handles setting span attributes."""

    @staticmethod
    def set_input_attributes(span: Span, source_name: str,
                             input_params: Dict[str, Any],
                             caller_info: Dict[str, Any],
                             pair_id: str) -> None:
        """Set input-related span attributes."""
        span.set_attribute(SpanAttributes.SPAN_KIND, "agent")
        span.set_attribute(SpanAttributes.AGENT_NAME, source_name)
        span.set_attribute(SpanAttributes.AGENT_INPUT,
                           safe_json_dumps(input_params, ensure_ascii=False))
        span.set_attribute(SpanAttributes.TRACE_CALLER_NAME, caller_info.get('source', 'unknown'))
        span.set_attribute(SpanAttributes.TRACE_CALLER_TYPE, caller_info.get('type', 'user'))
        span.set_attribute(SpanAttributes.AGENT_PAIR_ID, pair_id)

    @staticmethod
    def set_success_attributes(span: Span, duration: float,
                               result: OutputObject) -> None:
        """Set success-related span attributes."""
        span.set_attribute(SpanAttributes.AGENT_DURATION, duration)
        span.set_attribute(SpanAttributes.AGENT_STATUS, "success")
        span.set_attribute(SpanAttributes.AGENT_OUTPUT,
                           safe_json_dumps(result.to_dict(), ensure_ascii=False))
        span.set_attribute(SpanAttributes.AGENT_USAGE_TOTAL_TOKENS,
                           get_current_token_usage().total_tokens)
        span.set_attribute(SpanAttributes.AGENT_USAGE_COMPLETION_TOKENS,
                           get_current_token_usage().completion_tokens)
        span.set_attribute(SpanAttributes.AGENT_USAGE_PROMPT_TOKENS,
                           get_current_token_usage().prompt_tokens)
        span.set_attribute(SpanAttributes.AGENT_USAGE_DETAIL_TOKENS,
                           safe_json_dumps(get_current_token_usage().to_dict()))

    @staticmethod
    def set_error_attributes(span: Span, error: Exception,
                             duration: float) -> None:
        """Set error-related span attributes."""
        error_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        span.set_attribute(SpanAttributes.AGENT_STATUS, "error")
        span.set_attribute(SpanAttributes.AGENT_ERROR_TYPE, type(error).__name__)
        span.set_attribute(SpanAttributes.AGENT_ERROR_MESSAGE, error_str)
        span.set_attribute(SpanAttributes.AGENT_DURATION, duration)
        span.set_attribute(SpanAttributes.AGENT_USAGE_TOTAL_TOKENS,
                           get_current_token_usage().total_tokens)
        span.set_attribute(SpanAttributes.AGENT_USAGE_COMPLETION_TOKENS,
                           get_current_token_usage().completion_tokens)
        span.set_attribute(SpanAttributes.AGENT_USAGE_PROMPT_TOKENS,
                           get_current_token_usage().prompt_tokens)
        span.set_attribute(SpanAttributes.AGENT_USAGE_DETAIL_TOKENS,
                           safe_json_dumps(get_current_token_usage().to_dict()))
        span.set_status(Status(StatusCode.ERROR, str(error)))

    @staticmethod
    def set_streaming(span: Span, streaming: bool) -> None:
        span.set_attribute(SpanAttributes.AGENT_STREAMING, streaming)

    @staticmethod
    def set_first_token_attributes(span: Span, duration: float) -> None:
        """Set first token timing attributes."""
        span.set_attribute(SpanAttributes.AGENT_FIRST_TOKEN_DURATION, duration)


class AgentInstrumentor(BaseInstrumentor):
    """OpenTelemetry instrumentor for Agent calls."""

    def __init__(self):
        super().__init__()
        self._tracer: Optional[trace.Tracer] = None
        self._meter: Optional[metrics.Meter] = None
        self._metrics: Dict[str, Any] = {}
        self._metrics_recorder: Optional[AgentMetricsRecorder] = None
        self._original_agent_wrapper_sync = None
        self._original_agent_wrapper_async = None

    def instrumentation_dependencies(self):
        return []

    def _instrument(self, **kwargs):
        """Instrument Agent tracing."""
        tracer_provider = kwargs.get("tracer_provider")
        meter_provider = kwargs.get("meter_provider")

        self._tracer = trace.get_tracer(INSTRUMENTOR_NAME,
                                        INSTRUMENTOR_VERSION, tracer_provider)
        self._meter = metrics.get_meter(INSTRUMENTOR_NAME,
                                        INSTRUMENTOR_VERSION, meter_provider)

        self._setup_metrics()
        self._patch_trace_agent()

    def _uninstrument(self, **kwargs):
        """Remove instrumentation."""
        try:
            from agentuniverse.base.annotation import trace as trace_module
            setattr(trace_module, '_agent_wrapper_async',
                    self._original_agent_wrapper_async)
            setattr(trace_module, '_agent_wrapper_sync',
                    self._original_agent_wrapper_sync)
        except ImportError:
            pass

    def _setup_metrics(self):
        """Setup Agent-specific metrics."""
        self._metrics = {
            MetricNames.AGENT_CALLS_TOTAL: self._meter.create_counter(
                name=MetricNames.AGENT_CALLS_TOTAL,
                description="Total number of Agent calls",
                unit="1"
            ),
            MetricNames.AGENT_ERRORS_TOTAL: self._meter.create_counter(
                name=MetricNames.AGENT_ERRORS_TOTAL,
                description="Total number of Agent errors",
                unit="1"
            ),
            MetricNames.AGENT_CALL_DURATION: self._meter.create_histogram(
                name=MetricNames.AGENT_CALL_DURATION,
                description="Duration of Agent calls in seconds",
                unit="s"
            ),
            MetricNames.AGENT_FIRST_TOKEN_DURATION: self._meter.create_histogram(
                name=MetricNames.AGENT_FIRST_TOKEN_DURATION,
                description="Duration of Agent first token in seconds",
                unit="s"
            ),
            MetricNames.AGENT_TOTAL_TOKENS: self._meter.create_histogram(
                name=MetricNames.AGENT_TOTAL_TOKENS,
                description="Total token nums used in agent",
                unit="1"
            ),
            MetricNames.AGENT_COMPLETION_TOKENS: self._meter.create_histogram(
                name=MetricNames.AGENT_COMPLETION_TOKENS,
                description="Completion token nums used in agent",
                unit="1"
            ),
            MetricNames.AGENT_PROMPT_TOKENS: self._meter.create_histogram(
                name=MetricNames.AGENT_PROMPT_TOKENS,
                description="Prompt token nums used in agent",
                unit="1"
            ),
            MetricNames.AGENT_CACHED_TOKENS: self._meter.create_histogram(
                name=MetricNames.AGENT_CACHED_TOKENS,
                description="Cached token nums used in agent",
                unit="1"
            ),
            MetricNames.AGENT_REASONING_TOKENS: self._meter.create_histogram(
                name=MetricNames.AGENT_REASONING_TOKENS,
                description="Reasoning token nums used in agent",
                unit="1"
            )
        }
        self._metrics_recorder = AgentMetricsRecorder(self._metrics)

    def _patch_trace_agent(self):
        """Patch the trace_agent decorator."""
        try:
            from agentuniverse.base.annotation import trace as trace_module
            self._original_agent_wrapper_async = getattr(trace_module,
                                                         '_agent_wrapper_async',
                                                         None)
            self._original_agent_wrapper_sync = getattr(trace_module,
                                                        '_agent_wrapper_sync',
                                                        None)
            setattr(trace_module, '_agent_wrapper_async',
                    self._wrap_async_agent_function)
            setattr(trace_module, '_agent_wrapper_sync',
                    self._wrap_sync_agent_function)
        except ImportError:
            pass

    def _wrap_output_stream(self, output_stream: Any, start_time: float,
                            span: Span, labels: Dict[str, str]) -> Any:
        """Wrap output stream queue to monitor first token time."""

        def on_first_put(first_put_time: float):
            duration = first_put_time - start_time
            self._metrics_recorder.record_first_token(duration, labels)
            AgentSpanAttributesSetter.set_first_token_attributes(span,
                                                                 duration)

        # Check if it's an async queue
        if hasattr(asyncio, 'Queue') and isinstance(output_stream,
                                                    asyncio.Queue):
            return AsyncQueueWrapper(output_stream, on_first_put)
        # Check if it's a sync queue
        elif isinstance(output_stream, (queue.Queue, queue.SimpleQueue)):
            return QueueWrapper(output_stream, on_first_put)
        else:
            # If it's not a recognized queue type, return as is
            return output_stream

    async def _wrap_async_agent_function(self, func, *args, **kwargs):
        """Wrap async Agent function with OTEL tracing and metrics."""
        agent_instance, source, agent_input, start_info, pair_id = _get_agent_info(
            func, *args, **kwargs)

        labels = {
            MetricLabels.AGENT_NAME: source,
            MetricLabels.CALLER_NAME: start_info.get('source', 'unknown'),
            MetricLabels.CALLER_TYPE: start_info.get('type', 'user'),
            MetricLabels.STATUS: "success"
        }

        span_manager = AgentSpanManager(self._tracer, f"au.agent.{source}")
        start_time = time.time()
        span = span_manager.start_span()

        with InvocationChainContext(source=source, node_type='agent'):
            try:
                AgentSpanAttributesSetter.set_input_attributes(
                    span, source, agent_input, start_info, pair_id)

                self._metrics_recorder.record_call_start(labels)

                # Add memory source info
                kwargs['memory_source_info'] = start_info

                # Record memory input operation
                ConversationMemoryModule().add_agent_input_info(
                    start_info, agent_instance, agent_input, pair_id)

                # wrap output_stream to record first token
                if 'output_stream' in kwargs and kwargs[
                    'output_stream'] is not None:
                    # Add streaming label
                    labels[MetricLabels.STREAMING] = True
                    AgentSpanAttributesSetter.set_streaming(span, True)
                    kwargs['output_stream'] = self._wrap_output_stream(
                        kwargs['output_stream'], start_time, span, labels)
                else:
                    labels[MetricLabels.STREAMING] = False
                    AgentSpanAttributesSetter.set_streaming(span, False)

                # Execute the agent function
                result = await func(*args, **kwargs)

                # Record memory output operation
                ConversationMemoryModule().add_agent_result_info(
                    agent_instance, result, start_info, pair_id)

                duration = time.time() - start_time
                self._metrics_recorder.record_duration(duration, labels)
                self._metrics_recorder.record_total_token_usage(labels)
                if not labels[MetricLabels.STREAMING]:
                    self._metrics_recorder.record_first_token(duration, labels)
                    AgentSpanAttributesSetter.set_first_token_attributes(span, duration)
                AgentSpanAttributesSetter.set_success_attributes(
                    span, duration, result)

                return result

            except Exception as e:
                duration = time.time() - start_time
                self._metrics_recorder.record_error(e, duration, labels)
                self._metrics_recorder.record_total_token_usage(labels)
                AgentSpanAttributesSetter.set_error_attributes(
                    span_manager.span, e, duration)
                raise

            finally:
                span_manager.cleanup()

    def _wrap_sync_agent_function(self, func, *args, **kwargs):
        """Wrap sync Agent function with OTEL tracing and metrics."""
        agent_instance, source, agent_input, start_info, pair_id = _get_agent_info(
            func, *args, **kwargs)

        labels = {
            MetricLabels.AGENT_NAME: source,
            MetricLabels.CALLER_NAME: start_info.get('source', 'unknown'),
            MetricLabels.CALLER_TYPE: start_info.get('type', 'user'),
            MetricLabels.STATUS: "success"
        }

        span_manager = AgentSpanManager(self._tracer, f"au.agent.{source}")
        start_time = time.time()
        span = span_manager.start_span()

        with InvocationChainContext(source=source, node_type='agent'):
            try:
                AgentSpanAttributesSetter.set_input_attributes(
                    span, source, agent_input, start_info, pair_id)

                self._metrics_recorder.record_call_start(labels)

                # Add memory source info
                kwargs['memory_source_info'] = start_info

                # Record memory input operation
                ConversationMemoryModule().add_agent_input_info(
                    start_info, agent_instance, agent_input, pair_id)

                # wrap output_stream to record first token
                if 'output_stream' in kwargs and kwargs[
                    'output_stream'] is not None:
                    # Add streaming label
                    labels[MetricLabels.STREAMING] = True
                    AgentSpanAttributesSetter.set_streaming(span, True)
                    kwargs['output_stream'] = self._wrap_output_stream(
                        kwargs['output_stream'], start_time, span, labels)
                else:
                    labels[MetricLabels.STREAMING] = False
                    AgentSpanAttributesSetter.set_streaming(span, False)

                # Execute the agent function
                result: OutputObject = func(*args, **kwargs)

                # Record memory output operation
                ConversationMemoryModule().add_agent_result_info(
                    agent_instance, result, start_info, pair_id)


                duration = time.time() - start_time
                self._metrics_recorder.record_duration(duration, labels)
                self._metrics_recorder.record_total_token_usage(labels)
                if not labels[MetricLabels.STREAMING]:
                    self._metrics_recorder.record_first_token(duration, labels)
                    AgentSpanAttributesSetter.set_first_token_attributes(span, duration)
                AgentSpanAttributesSetter.set_success_attributes(
                    span, duration, result)

                return result

            except Exception as e:
                duration = time.time() - start_time
                self._metrics_recorder.record_error(e, duration, labels)
                self._metrics_recorder.record_total_token_usage(labels)
                AgentSpanAttributesSetter.set_error_attributes(
                    span_manager.span, e, duration)
                raise

            finally:
                span_manager.cleanup()
