"""Real SDK export tests with synthetic payloads and two downstream exporters."""

import asyncio
import json

import pytest
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExportResult
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import Link, SpanContext, Status, StatusCode, TraceState

from agentuniverse.base.tracing.otel.span_processor.policy_span_exporter import (
    ExportField,
    PolicySpanExporter,
    SpanExportPolicy,
)
from agentuniverse.base.tracing.otel.span_processor.span_json_exporter import SpanJsonExporter


def fixture_spans():
    raw = InMemorySpanExporter()
    provider = TracerProvider(resource=Resource({"service.name": "approved", "secret": "SECRET"}))
    provider.add_span_processor(SimpleSpanProcessor(raw))
    tracer = provider.get_tracer("SECRET", "SECRET", schema_url="SECRET")
    linked = SpanContext(1, 2, False, trace_state=TraceState([("secret", "SECRET")]))
    with tracer.start_as_current_span("SECRET parent"):
        with tracer.start_as_current_span("SECRET prompt", links=[Link(linked, {"secret": "SECRET"})]) as span:
            span.set_attributes({"au.span.kind": "llm", "safe": 3, "prompt": "SECRET", "nested": '{"secret":"SECRET"}'})
            span.add_event("SECRET", {"safe": 1})
            span.add_event("usage", {"safe": 2, "secret": "SECRET"})
            span.record_exception(ValueError("SECRET"))
            span.set_status(Status(StatusCode.ERROR, "SECRET"))
    provider.shutdown()
    return raw.get_finished_spans()


def test_default_removes_all_payload_surfaces_and_keeps_topology():
    spans = fixture_spans()
    sink = InMemorySpanExporter()
    assert PolicySpanExporter(sink).export(spans) == SpanExportResult.SUCCESS
    clean = sink.get_finished_spans()
    for old, new in zip(spans, clean):
        assert "SECRET" not in new.to_json()
        assert new.name == "span"
        assert not new.attributes and not new.events and not new.links
        assert not new.resource.attributes
        assert new.context.trace_id == old.context.trace_id
        assert new.context.span_id == old.context.span_id
        assert new.start_time == old.start_time and new.end_time == old.end_time
        assert new.status.status_code == old.status.status_code
    assert clean[0].parent.span_id == clean[1].context.span_id
    assert "SECRET" in spans[0].to_json()


def test_explicit_policy_to_memory_and_actual_json_files(tmp_path):
    spans = fixture_spans()
    before = [s.to_json() for s in spans]
    policy = SpanExportPolicy(
        attributes={"au.span.kind": ExportField(str, values=frozenset({"llm"})), "safe": ExportField(int)},
        resources={"service.name": ExportField(str)},
        events={"usage": {"safe": ExportField(int)}},
    )
    memory = InMemorySpanExporter()
    assert PolicySpanExporter(memory, policy).export(spans) == SpanExportResult.SUCCESS
    assert memory.get_finished_spans()[0].events[0].attributes == {"safe": 2}
    assert PolicySpanExporter(SpanJsonExporter(str(tmp_path)), policy).export(spans) == SpanExportResult.SUCCESS
    files = list(tmp_path.rglob("*.json"))
    assert len(files) == 1
    payload = files[0].read_text(encoding="utf-8")
    assert "SECRET" not in payload
    assert json.loads(payload)["attributes"] == {"au.span.kind": "llm", "safe": 3}
    assert before == [s.to_json() for s in spans]


@pytest.mark.parametrize(
    "rule,value,expected",
    [
        (ExportField(int), True, False),
        (ExportField(int), 2, True),
        (ExportField(int), 2**63, False),
        (ExportField(float), float("nan"), False),
        (ExportField(float), float("inf"), False),
        (ExportField(str, 3), "abcd", False),
        (ExportField(str, 3), "中文", True),
        (ExportField(str), {"x": "y"}, False),
        (ExportField(str), ["a"], False),
        (ExportField(str, max_items=2), ["a", "b"], True),
        (ExportField(str, max_items=2), ["a", 1], False),
        (ExportField(str, max_items=2), ["a", "b", "c"], False),
        (ExportField(str, values=frozenset({"llm"})), "../secret", False),
    ],
)
def test_field_contract(rule, value, expected):
    assert rule.accepts(value) is expected


@pytest.mark.parametrize(
    "kwargs",
    [{"kind": dict}, {"kind": str, "max_length": -1}, {"kind": str, "max_items": True}, {"kind": int, "values": {"1"}}],
)
def test_invalid_rules(kwargs):
    with pytest.raises(ValueError):
        ExportField(**kwargs)


def test_policy_freezes_caller_mappings_and_bounds_events():
    fields = {"safe": ExportField(int)}
    policy = SpanExportPolicy(attributes=fields, events={"usage": fields}, max_events=0)
    fields["prompt"] = ExportField(str)
    result = policy.project(fixture_spans()[0])
    assert result.attributes == {"safe": 3} and not result.events


def test_exception_and_async_cancellation_spans_are_filtered():
    sink = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(PolicySpanExporter(sink)))
    tracer = provider.get_tracer("test")

    async def cancelled():
        with tracer.start_as_current_span("SECRET"):
            raise asyncio.CancelledError("SECRET")

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(cancelled())
    provider.shutdown()
    assert len(sink.get_finished_spans()) == 1
    assert "SECRET" not in sink.get_finished_spans()[0].to_json()


def test_fail_closed_no_retry_and_lifecycle():
    class Broken(InMemorySpanExporter):
        calls = 0
        timeout = None
        stopped = False

        def export(self, spans):
            self.calls += 1
            assert all("SECRET" not in span.to_json() for span in spans)
            raise RuntimeError("failed")

        def force_flush(self, timeout_millis=30000):
            self.timeout = timeout_millis
            return False

        def shutdown(self):
            self.stopped = True

    sink = Broken()
    wrapper = PolicySpanExporter(sink)
    assert wrapper.export(fixture_spans()) == SpanExportResult.FAILURE
    assert sink.calls == 1
    assert not wrapper.force_flush(42) and sink.timeout == 42
    wrapper.shutdown()
    assert sink.stopped


def test_projection_failure_never_sends_partial_batch():
    sink = InMemorySpanExporter()
    assert PolicySpanExporter(sink).export([fixture_spans()[0], None]) == SpanExportResult.FAILURE
    assert not sink.get_finished_spans()
