# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio
import threading
from typing import Optional

from opentelemetry import trace, context
from opentelemetry.sdk.trace.id_generator import RandomIdGenerator
from opentelemetry.trace import format_trace_id, format_span_id, SpanContext, \
    TraceFlags, NonRecordingSpan

from agentuniverse.llm.llm_output import TokenUsage

# @Time    : 2025/1/6 17:21
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: au_trace_context.py

id_generator = RandomIdGenerator()


class AuTraceContext:
    _token_count_dict = {}
    _token_count_lock = threading.Lock()

    def __init__(self):
        self._session_id = None
        current_span = trace.get_current_span()

        if current_span and current_span.get_span_context().is_valid:
            span_context = current_span.get_span_context()
            self._trace_id = format_trace_id(span_context.trace_id)
            self._span_id = format_span_id(span_context.span_id)
        else:
            self._trace_id = self._generate_trace_id()
            self._span_id = self._generate_span_id()

    @classmethod
    def new_context(cls):
        return cls()

    @classmethod
    def from_trace_context(cls, trace_id: str, span_id: str,
                           session_id: Optional[str] = None):
        instance = cls.__new__(cls)
        instance._session_id = session_id
        instance._trace_id = trace_id
        instance._span_id = span_id
        instance._set_otel_context(trace_id, span_id)

        return instance

    @staticmethod
    def _generate_trace_id() -> str:
        trace_id_int = id_generator.generate_trace_id()
        return format_trace_id(trace_id_int)

    @staticmethod
    def _generate_span_id() -> str:
        span_id_int = id_generator.generate_span_id()
        return format_span_id(span_id_int)

    def _set_otel_context(self, trace_id: str, span_id: str):
        try:
            trace_id_int = int(trace_id, 16)
            span_id_int = int(span_id, 16)

            span_context = SpanContext(
                trace_id=trace_id_int,
                span_id=span_id_int,
                is_remote=True,
                trace_flags=TraceFlags(0x01)
            )

            span = NonRecordingSpan(span_context)
            ctx = trace.set_span_in_context(span)
            token = context.attach(ctx)
            return token

        except Exception as e:
            return None

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def trace_id(self) -> str:
        current_span = trace.get_current_span()

        if current_span and current_span.get_span_context().is_valid:
            span_context = current_span.get_span_context()
            return format_trace_id(span_context.trace_id)
        return self._trace_id

    @property
    def span_id(self) -> str:
        current_span = trace.get_current_span()

        if current_span and current_span.get_span_context().is_valid:
            span_context = current_span.get_span_context()
            return format_span_id(span_context.span_id)
        return self._span_id

    def set_session_id(self, session_id: str):
        self._session_id = session_id

    def set_trace_id(self, trace_id: str):
        self._trace_id = trace_id
        self._set_otel_context(trace_id, self._span_id)

    def set_span_id(self, span_id: str):
        self._span_id = span_id
        self._set_otel_context(self._trace_id, span_id)

    def set_trace_context(self, trace_id: str, span_id: str):
        self._trace_id = trace_id
        self._span_id = span_id
        self._set_otel_context(trace_id, span_id)

    def _get_current_span_id(self):
        span = trace.get_current_span()
        if not span.is_recording():
            return None
        return span.context.span_id

    def init_new_token_usage(self, span_id=None):
        span_id = span_id or trace.get_current_span().get_span_context().span_id
        if not span_id:
            return
        self._token_count_dict[span_id] = TokenUsage()

    def add_current_token_usage(self, token_usage, span_id=None):
        span_id = span_id or trace.get_current_span().get_span_context().span_id
        if not span_id:
            return
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            with self._token_count_lock:
                self._token_count_dict[span_id] += token_usage
        else:
            self._token_count_dict[span_id] += token_usage

    def add_current_token_usage_to_parent(self, token_usage=None, parent_span_id=None):
        if not token_usage:
            token_usage = self.get_current_token_usage()
        if parent_span_id and parent_span_id in self._token_count_dict:
            self._token_count_dict[parent_span_id] += token_usage
            return

        span = trace.get_current_span()
        parent_ctx = span.parent  # 只有 SpanContext，可能为 None
        if parent_ctx is not None and parent_ctx.span_id and parent_ctx.span_id in self._token_count_dict:
            self._token_count_dict[parent_ctx.span_id] += token_usage

    def get_current_token_usage(self, span_id=None):
        span_id = span_id or trace.get_current_span().get_span_context().span_id
        if not span_id:
            return TokenUsage()
        return self._token_count_dict.get(span_id, TokenUsage())


    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id
        }

    def __str__(self):
        return f"Context(session_id={self.session_id}, trace_id={self.trace_id}, span_id={self.span_id})"

    def __repr__(self):
        return self.__str__()
