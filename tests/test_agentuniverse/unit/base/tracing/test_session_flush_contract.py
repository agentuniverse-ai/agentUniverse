"""Exercise session processor flushing through real SDK providers and queues."""

import pytest
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from agentuniverse.base.tracing.otel.span_processor.session_span_processor import (
    SessionSpanProcessor,
)
from agentuniverse.base.tracing.otel.telemetry_manager import TelemetryManager


@pytest.mark.parametrize("timeout", [0, 1, 30000])
def test_no_buffer_flush_reports_success(timeout):
    assert SessionSpanProcessor().force_flush(timeout) is True


def test_default_telemetry_provider_reports_success():
    provider = TelemetryManager()._build_tracer_provider({}, Resource.create())
    try:
        assert provider.force_flush() is True
    finally:
        provider.shutdown()


@pytest.mark.parametrize("session_first", [False, True])
def test_batch_export_is_flushed_in_either_processor_order(session_first):
    exporter = InMemorySpanExporter()
    batch = BatchSpanProcessor(exporter, schedule_delay_millis=60000)
    session = SessionSpanProcessor()
    provider = TracerProvider(shutdown_on_exit=False)
    for processor in ([session, batch] if session_first else [batch, session]):
        provider.add_span_processor(processor)
    try:
        with provider.get_tracer(__name__).start_as_current_span("example"):
            pass
        assert exporter.get_finished_spans() == ()
        assert provider.force_flush() is True
        assert [span.name for span in exporter.get_finished_spans()] == ["example"]
        assert provider.force_flush() is True
        assert len(exporter.get_finished_spans()) == 1
    finally:
        provider.shutdown()


def test_following_processor_failure_is_not_masked():
    calls = []

    class FailingProcessor(SpanProcessor):
        def force_flush(self, timeout_millis=30000):
            calls.append(timeout_millis)
            return False

    provider = TracerProvider(shutdown_on_exit=False)
    provider.add_span_processor(SessionSpanProcessor())
    provider.add_span_processor(FailingProcessor())
    try:
        assert provider.force_flush() is False
        assert len(calls) == 1
    finally:
        provider.shutdown()


def test_session_attribute_and_other_lifecycle_hooks_are_unchanged():
    from agentuniverse.base.tracing.au_trace_manager import AuTraceManager, set_session_id
    from agentuniverse.base.tracing.otel.consts import SPAN_SESSION_ID_KEY

    manager = AuTraceManager()
    token = manager.context_instance.set(None)
    provider = TracerProvider(shutdown_on_exit=False)
    processor = SessionSpanProcessor()
    provider.add_span_processor(processor)
    try:
        set_session_id("example-session")
        with provider.get_tracer(__name__).start_span("example") as span:
            assert span.attributes[SPAN_SESSION_ID_KEY] == "example-session"
        assert processor.on_end(span) is None
        assert processor.shutdown() is None
        assert processor.force_flush() is True
    finally:
        provider.shutdown()
        manager.context_instance.reset(token)
