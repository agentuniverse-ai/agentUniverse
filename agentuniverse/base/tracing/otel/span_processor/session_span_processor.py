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
    """SpanProcessor that attaches the current session id to every span.

    On span start it stamps the span with the session id taken from the
    active trace context, falling back to '-1' when no session is bound.
    """

    def on_start(self, span, parent_context=None):
        """Stamp the started span with the current session id.

        Args:
            span: The span that has just started.
            parent_context: Optional parent context of the span.
        """
        session_id = get_session_id()
        if session_id:
            span.set_attribute(SPAN_SESSION_ID_KEY, session_id)
        else:
            span.set_attribute(SPAN_SESSION_ID_KEY, '-1')

    def on_end(self, span):
        """Callback for span end; kept as a no-op by this processor."""

    def shutdown(self):
        """Release processor resources; kept as a no-op by this processor."""

    def force_flush(self, timeout_millis=30000):
        """Flush pending spans; kept as a no-op by this processor.

        Args:
            timeout_millis(int): Maximum time to wait for the flush.
        """
