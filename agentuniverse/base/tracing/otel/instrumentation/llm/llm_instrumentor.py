#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/30 15:44
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: llm_instrumentor.py
# -*- coding: utf-8 -*-
"""
OpenTelemetry instrumentor for LLM calls in AgentUniverse.

This instrumentor automatically creates spans and metrics for LLM invocations
decorated with @trace_llm.
"""
import base64
import datetime
import decimal
import json
import time
import traceback
from typing import Any, Dict, Optional, AsyncGenerator, Generator

from opentelemetry import trace, metrics, context
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import Status, StatusCode, Span

from agentuniverse.base.annotation.trace import _get_llm_info, _llm_plugins
from agentuniverse.base.tracing.au_trace_manager import init_new_token_usage, \
    get_current_token_usage, add_current_token_usage_to_parent, \
    add_current_token_usage
from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.llm.llm_output import LLMOutput, TokenUsage
from .consts import (
    INSTRUMENTOR_NAME, INSTRUMENTOR_VERSION,
    MetricNames, SpanAttributes, MetricLabels
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


class LLMSpanManager:
    """Manager for LLM span lifecycle with support for deferred cleanup."""

    def __init__(self, tracer: trace.Tracer, span_name: str):
        self.tracer = tracer
        self.span_name = span_name
        self.span: Optional[Span] = None
        self.token = None
        self.auto_cleanup = True

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

    def defer_cleanup(self):
        """Defer automatic cleanup - caller must call cleanup() manually."""
        self.auto_cleanup = False

    def cleanup(self):
        """Manually cleanup span and context."""
        if self.span:
            try:
                add_current_token_usage_to_parent(
                    get_current_token_usage(self.span.context.span_id),
                    self.span.parent.span_id
                )
            except:
                pass
            self.span.end()
            self.span = None
        if self.token and self.auto_cleanup:
            context.detach(self.token)
            self.token = None
        Monitor.pop_invocation_chain()

    def __enter__(self) -> Span:
        return self.start_span()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.auto_cleanup:
            self.cleanup()


class LLMMetricsRecorder:
    """Handles LLM metrics recording."""

    def __init__(self, metrics: Dict[str, Any]):
        self.metrics = metrics

    def record_call_start(self, labels: Dict[str, str]) -> None:
        """Record start of LLM call."""
        self.metrics[MetricNames.LLM_CALLS_TOTAL].add(1, labels)

    def record_duration(self, duration: float, labels: Dict[str, str]) -> None:
        """Record call duration."""
        self.metrics[MetricNames.LLM_CALL_DURATION].record(duration, labels)

    def record_first_token(self, duration: float,
                           labels: Dict[str, str],
                           streaming: bool = True) -> None:
        """Record first token timing."""
        _labels = {**labels, MetricLabels.STREAMING: streaming}
        self.metrics[MetricNames.LLM_FIRST_TOKEN_DURATION].record(duration, _labels)

    def record_token_usage(self, usage: TokenUsage,
                           labels: Dict[str, str]) -> None:
        """Record token usage metrics."""
        if usage:
            self.metrics[MetricNames.LLM_PROMPT_TOKENS].record(usage.prompt_tokens,
                                                     labels)
            self.metrics[MetricNames.LLM_COMPLETION_TOKENS].record(
                usage.completion_tokens, labels)
            self.metrics[MetricNames.LLM_TOTAL_TOKENS].record(usage.total_tokens, labels)
            self.metrics[MetricNames.LLM_CACHED_TOKENS].record(
                usage.cached_tokens, labels)
            self.metrics[MetricNames.LLM_REASONING_TOKENS].record(
                usage.reasoning_tokens, labels)

    def record_error(self, error: Exception, duration: float,
                     labels: Dict[str, str]) -> None:
        """Record error metrics."""
        error_labels = {**labels}
        error_labels[MetricLabels.STATUS] = type(error).__name__
        self.metrics[MetricNames.LLM_ERRORS_TOTAL].add(1, error_labels)
        self.metrics[MetricNames.LLM_CALL_DURATION].record(duration, error_labels)


class LLMSpanAttributesSetter:
    """Handles setting span attributes."""

    @staticmethod
    def set_input_attributes(span: Span, source_name: str, channel_name: str,
                             input_params: Dict[str, Any],
                             llm_params: Dict[str, Any],
                             caller_info: Dict[str, Any]) -> None:
        """Set input-related span attributes."""
        span.set_attribute(SpanAttributes.SPAN_KIND, "llm")
        span.set_attribute(SpanAttributes.AU_LLM_NAME, source_name)
        span.set_attribute(SpanAttributes.AU_LLM_CHANNEL_NAME, channel_name)
        span.set_attribute(SpanAttributes.AU_LLM_INPUT,
                           safe_json_dumps(input_params, ensure_ascii=False))
        span.set_attribute(SpanAttributes.AU_LLM_LLM_PARAMS,
                           safe_json_dumps(llm_params, ensure_ascii=False))
        span.set_attribute(SpanAttributes.AU_TRACE_CALLER_NAME,
                           caller_info.get('source', 'unknown'))
        span.set_attribute(SpanAttributes.AU_TRACE_CALLER_TYPE,
                           caller_info.get('type', 'user'))

    @staticmethod
    def set_success_attributes(span: Span, duration: float,
                               result: LLMOutput) -> None:
        """Set success-related span attributes."""
        span.set_attribute(SpanAttributes.AU_LLM_DURATION, duration)
        span.set_attribute(SpanAttributes.AU_LLM_STATUS, "success")
        span.set_attribute(SpanAttributes.AU_LLM_OUTPUT, result.text)

        if result.usage:
            span.set_attribute(SpanAttributes.AU_LLM_USAGE_PROMPT_TOKENS,
                               result.usage.prompt_tokens)
            span.set_attribute(SpanAttributes.AU_LLM_USAGE_COMPLETION_TOKENS,
                               result.usage.completion_tokens)
            span.set_attribute(SpanAttributes.AU_LLM_USAGE_TOTAL_TOKENS,
                               result.usage.total_tokens)
            span.set_attribute(SpanAttributes.AU_LLM_USAGE_DETAIL_TOKENS,
                               safe_json_dumps(result.usage.to_dict()))

    @staticmethod
    def set_error_attributes(span: Span, error: Exception,
                             duration: float) -> None:
        """Set error-related span attributes."""
        error_str = ''.join(traceback.format_exception(type(error), error,
                                                       error.__traceback__))
        span.set_attribute(SpanAttributes.AU_LLM_STATUS, "error")
        span.set_attribute(SpanAttributes.AU_LLM_ERROR_TYPE, type(error).__name__)
        span.set_attribute(SpanAttributes.AU_LLM_ERROR_MESSAGE, error_str)
        span.set_attribute(SpanAttributes.AU_LLM_DURATION, duration)
        span.set_status(Status(StatusCode.ERROR, str(error)))

    @staticmethod
    def set_first_token_attributes(span: Span, duration: float) -> None:
        """Set first token timing attributes."""
        span.set_attribute(SpanAttributes.AU_LLM_FIRST_TOKEN_DURATION, duration)

    @staticmethod
    def set_streaming(span: Span, streaming: bool) -> None:
        span.set_attribute(SpanAttributes.AU_LLM_STREAMING, streaming)


class StreamingResultProcessor:
    """Handles streaming result processing."""

    def __init__(self, source: str, llm_input: Any, llm_instance: Any,
                 start_time: float, span_manager: LLMSpanManager,
                 labels: Dict[str, str],
                 metrics_recorder: LLMMetricsRecorder):
        self.source = source
        self.llm_input = llm_input
        self.llm_instance = llm_instance
        self.start_time = start_time
        self.span_manager = span_manager
        self.span = span_manager.span
        self.labels = labels
        self.metrics_recorder = metrics_recorder

    async def process_async_stream(self,
                                   result: AsyncGenerator) -> AsyncGenerator:
        """Process async streaming result."""
        llm_output = []
        usage = None
        first_token = True

        try:
            async for chunk in result:
                if first_token:
                    first_token = False
                    duration = time.time() - self.start_time
                    self.metrics_recorder.record_first_token(duration,
                                                             self.labels)
                    LLMSpanAttributesSetter.set_first_token_attributes(
                        self.span, duration)

                llm_output.append(chunk.text)
                if chunk.usage:
                    usage = chunk.usage
                yield chunk
            if usage:
                add_current_token_usage(usage, self.span_manager.span.context.span_id)
            self._finalize_streaming_result(llm_output, usage)

        except Exception as e:
            duration = time.time() - self.start_time
            self._handle_streaming_error(e, duration)
            raise
        finally:
            # Clean up span and context after streaming is complete
            self.span_manager.cleanup()

    def process_sync_stream(self, result) -> Generator:
        """Process sync streaming result."""
        llm_output = []
        usage = None
        first_token = True

        try:
            for chunk in result:
                if first_token:
                    first_token = False
                    duration = time.time() - self.start_time
                    self.metrics_recorder.record_first_token(duration,
                                                             self.labels)
                    LLMSpanAttributesSetter.set_first_token_attributes(
                        self.span, duration)

                llm_output.append(
                    chunk.text if hasattr(chunk, 'text') else str(chunk))
                if hasattr(chunk, 'usage') and chunk.usage:
                    usage = chunk.usage
                yield chunk
            if usage:
                add_current_token_usage(usage, self.span_manager.span.context.span_id)
            self._finalize_streaming_result(llm_output, usage)

        except Exception as e:
            duration = time.time() - self.start_time
            self._handle_streaming_error(e, duration)
            raise
        finally:
            # Clean up span and context after streaming is complete
            self.span_manager.cleanup()

    def _finalize_streaming_result(self, llm_output: list,
                                   usage: Optional[TokenUsage]) -> None:
        """Finalize streaming result processing."""
        output_str = "".join(llm_output)
        duration = time.time() - self.start_time

        Monitor().trace_llm_invocation(
            source=self.source,
            llm_input=self.llm_input,
            llm_output=output_str,
            cost_time=duration
        )

        pseudo_result = LLMOutput(text=output_str, usage=usage)
        Monitor().trace_llm_token_usage(self.llm_instance, self.llm_input,
                                        pseudo_result)

        # Record success metrics
        self.metrics_recorder.record_duration(duration, self.labels)
        if pseudo_result.usage:
            self.metrics_recorder.record_token_usage(pseudo_result.usage,
                                                     self.labels)
        LLMSpanAttributesSetter.set_success_attributes(self.span, duration,
                                                       pseudo_result)

    def _handle_streaming_error(self, error: Exception,
                                duration: float) -> None:
        """Handle streaming error."""
        self.metrics_recorder.record_error(error, duration, self.labels)
        LLMSpanAttributesSetter.set_error_attributes(self.span, error,
                                                     duration)


class LLMInstrumentor(BaseInstrumentor):
    """OpenTelemetry instrumentor for LLM calls."""

    def __init__(self):
        super().__init__()
        self._tracer: Optional[trace.Tracer] = None
        self._meter: Optional[metrics.Meter] = None
        self._metrics: Dict[str, Any] = {}
        self._metrics_recorder: Optional[LLMMetricsRecorder] = None
        self._original_llm_wrapper_sync = None
        self._original_llm_wrapper_async = None

    def instrumentation_dependencies(self):
        return []

    def _instrument(self, **kwargs):
        """Instrument LLM tracing."""
        tracer_provider = kwargs.get("tracer_provider")
        meter_provider = kwargs.get("meter_provider")

        self._tracer = trace.get_tracer(INSTRUMENTOR_NAME,
                                        INSTRUMENTOR_VERSION, tracer_provider)
        self._meter = metrics.get_meter(INSTRUMENTOR_NAME,
                                        INSTRUMENTOR_VERSION, meter_provider)

        self._setup_metrics()
        self._patch_trace_llm()

    def _uninstrument(self, **kwargs):
        """Remove instrumentation."""
        try:
            from agentuniverse.base.annotation import trace as trace_module
            setattr(trace_module, '_llm_wrapper_async',
                    self._original_llm_wrapper_async)
            setattr(trace_module, '_llm_wrapper_sync',
                    self._original_llm_wrapper_sync)
        except ImportError:
            pass

    def _setup_metrics(self):
        """Setup LLM-specific metrics."""
        self._metrics = {
            MetricNames.LLM_CALLS_TOTAL: self._meter.create_counter(
                name=MetricNames.LLM_CALLS_TOTAL,
                description="Total number of LLM calls",
                unit="1"
            ),
            MetricNames.LLM_ERRORS_TOTAL: self._meter.create_counter(
                name=MetricNames.LLM_ERRORS_TOTAL,
                description="Total number of LLM errors",
                unit="1"
            ),
            MetricNames.LLM_CALL_DURATION: self._meter.create_histogram(
                name=MetricNames.LLM_CALL_DURATION,
                description="Duration of LLM calls in seconds",
                unit="s"
            ),
            MetricNames.LLM_FIRST_TOKEN_DURATION: self._meter.create_histogram(
                name=MetricNames.LLM_FIRST_TOKEN_DURATION,
                description="Duration of LLM first token in seconds",
                unit="s"
            ),
            MetricNames.LLM_TOTAL_TOKENS: self._meter.create_histogram(
                name=MetricNames.LLM_TOTAL_TOKENS,
                description="Number of tokens used in LLM calls",
                unit="1"
            ),
            MetricNames.LLM_PROMPT_TOKENS: self._meter.create_histogram(
                name=MetricNames.LLM_PROMPT_TOKENS,
                description="Number of prompt tokens in LLM calls",
                unit="1"
            ),
            MetricNames.LLM_COMPLETION_TOKENS: self._meter.create_histogram(
                name=MetricNames.LLM_COMPLETION_TOKENS,
                description="Number of completion tokens in LLM calls",
                unit="1"
            ),
            MetricNames.LLM_REASONING_TOKENS: self._meter.create_histogram(
                name=MetricNames.LLM_REASONING_TOKENS,
                description="Number of reasoning tokens in LLM calls",
                unit="1"
            ),
            MetricNames.LLM_CACHED_TOKENS: self._meter.create_histogram(
                name=MetricNames.LLM_CACHED_TOKENS,
                description="Number of cached tokens in LLM calls",
                unit="1"
            )
        }
        self._metrics_recorder = LLMMetricsRecorder(self._metrics)

    def _patch_trace_llm(self):
        """Patch the trace_llm decorator."""
        try:
            from agentuniverse.base.annotation import trace as trace_module
            self._original_llm_wrapper_async = getattr(trace_module, '_llm_wrapper_async', None)
            self._original_llm_wrapper_sync = getattr(trace_module, '_llm_wrapper_sync', None)
            setattr(trace_module, '_llm_wrapper_async', self._wrap_async_llm_function)
            setattr(trace_module, '_llm_wrapper_sync', self._wrap_sync_llm_function)
        except ImportError:
            pass

    def _prepare_llm_context(self, func, *args, **kwargs) -> tuple:
        """Prepare LLM context information."""
        llm_instance, source, channel_name, llm_input, params, caller_info = _get_llm_info(
            func, *args, **kwargs)

        Monitor.add_invocation_chain({'source': source, 'type': 'llm'})
        Monitor.trace_llm_input(source, llm_input)

        labels = {
            MetricLabels.LLM_NAME: source,
            MetricLabels.CALLER_NAME: caller_info.get('source', 'unknown'),
            MetricLabels.CALLER_TYPE: caller_info.get('type', 'user'),
            MetricLabels.STATUS: "success"
        }

        return llm_instance, source, channel_name, llm_input, params, caller_info, labels

    def _handle_non_streaming_result(self, result: LLMOutput, llm_instance,
                                     source: str,
                                     llm_input, duration: float, span: Span,
                                     labels: Dict[str, str]) -> None:
        """Handle non-streaming LLM result."""
        Monitor.trace_llm_invocation(source, llm_input, result.text, duration)
        Monitor().trace_llm_token_usage(llm_instance, llm_input, result)

        self._metrics_recorder.record_duration(duration, labels)
        self._metrics_recorder.record_first_token(duration, labels, streaming=False)
        if result.usage:
            self._metrics_recorder.record_token_usage(result.usage, labels)
            add_current_token_usage(result.usage, span.context.span_id)
        LLMSpanAttributesSetter.set_first_token_attributes(span, duration)
        LLMSpanAttributesSetter.set_success_attributes(span, duration, result)

    async def _wrap_async_llm_function(self, func, *args, **kwargs):
        """Wrap async LLM function with OTEL tracing and metrics."""
        llm_instance, source, channel_name, llm_input, params, caller_info, labels = (
            self._prepare_llm_context(func, *args, **kwargs))

        span_manager = LLMSpanManager(self._tracer, f"au.llm.{source}")
        start_time = time.time()

        try:
            span = span_manager.start_span()
            LLMSpanAttributesSetter.set_input_attributes(
                span, source, channel_name, llm_input, params, caller_info)

            self._metrics_recorder.record_call_start(labels)

            result = await _llm_plugins(func)(*args, **kwargs)

            if isinstance(result, LLMOutput):
                # Non-streaming result - cleanup immediately
                LLMSpanAttributesSetter().set_streaming(span, False)
                duration = time.time() - start_time
                self._handle_non_streaming_result(
                    result, llm_instance, source, llm_input, duration,
                    span, labels)
                span_manager.cleanup()
                return result
            else:
                # Streaming result - defer cleanup to the processor
                LLMSpanAttributesSetter().set_streaming(span, True)
                span_manager.defer_cleanup()
                processor = StreamingResultProcessor(
                    source, llm_input, llm_instance, start_time,
                    span_manager, labels, self._metrics_recorder)
                context.detach(span_manager.token)
                return processor.process_async_stream(result)

        except Exception as e:
            duration = time.time() - start_time
            self._metrics_recorder.record_error(e, duration, labels)
            LLMSpanAttributesSetter.set_error_attributes(span_manager.span,
                                                         e, duration)
            span_manager.cleanup()
            raise


    def _wrap_sync_llm_function(self, func, *args, **kwargs):
        """Wrap sync LLM function with OTEL tracing and metrics."""
        llm_instance, source, channel_name, llm_input, params, caller_info, labels = (
            self._prepare_llm_context(func, *args, **kwargs))

        span_manager = LLMSpanManager(self._tracer, f"au.llm.{source}")
        start_time = time.time()

        try:
            span = span_manager.start_span()
            LLMSpanAttributesSetter.set_input_attributes(
                span, source, channel_name, llm_input, params, caller_info)

            self._metrics_recorder.record_call_start(labels)

            result = _llm_plugins(func)(*args, **kwargs)

            if isinstance(result, LLMOutput):
                # Non-streaming result - cleanup immediately
                LLMSpanAttributesSetter().set_streaming(span, False)
                duration = time.time() - start_time
                self._handle_non_streaming_result(
                    result, llm_instance, source, llm_input, duration,
                    span, labels)
                span_manager.cleanup()
                return result
            else:
                # Streaming result - defer cleanup to the processor
                LLMSpanAttributesSetter().set_streaming(span, True)
                span_manager.defer_cleanup()
                processor = StreamingResultProcessor(
                    source, llm_input, llm_instance, start_time,
                    span_manager, labels, self._metrics_recorder)
                context.detach(span_manager.token)
                return processor.process_sync_stream(result)

        except Exception as e:
            duration = time.time() - start_time
            self._metrics_recorder.record_error(e, duration, labels)
            LLMSpanAttributesSetter.set_error_attributes(span_manager.span,
                                                         e, duration)
            span_manager.cleanup()
            raise
