# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/29 11:31
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: session_span_processor.py

from opentelemetry.sdk.trace import SpanProcessor

from agentuniverse.base.tracing.au_trace_manager import get_session_id
from agentuniverse.base.tracing.otel.consts import SPAN_SESSION_ID_KEY


class SessionSpanProcessor(SpanProcessor):
    def on_start(self, span, parent_context=None):
        session_id = get_session_id()
        if session_id:
            span.set_attribute(SPAN_SESSION_ID_KEY, session_id)
        else:
            span.set_attribute(SPAN_SESSION_ID_KEY, '-1')

    def on_end(self, span):
        pass

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis=30000):
        pass
