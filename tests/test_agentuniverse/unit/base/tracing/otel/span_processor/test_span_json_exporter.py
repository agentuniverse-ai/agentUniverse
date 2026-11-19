# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the span JSON exporter.

Finished spans are produced entirely in-memory through the OpenTelemetry
SDK so the tests stay deterministic (no network, GPU, DB or sleeps).
"""

import json

from opentelemetry.sdk.trace import Status, StatusCode, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExportResult
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from agentuniverse.base.tracing.otel.span_processor.span_json_exporter import SpanJsonExporter


def _make_finished_spans(with_kind: str | None = "agent"):
    """Create finished spans through an in-memory pipeline."""
    memory_exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(memory_exporter)
    tracer = TracerProvider(active_span_processor=processor).get_tracer("test")
    with tracer.start_as_current_span("operation") as span:
        if with_kind is not None:
            span.set_attribute("au.span.kind", with_kind)
        span.set_status(Status(StatusCode.OK))
    processor.shutdown()
    return memory_exporter.get_finished_spans()


class TestSpanJsonExporter:
    def test_init_creates_base_dir(self, tmp_path):
        exporter = SpanJsonExporter(str(tmp_path / "monitor"))
        assert (tmp_path / "monitor").is_dir()

    def test_folder_for_uses_span_kind_attribute(self, tmp_path):
        exporter = SpanJsonExporter(str(tmp_path))
        span = _make_finished_spans("agent")[0]
        assert exporter._folder_for(span) == tmp_path / "agent"

    def test_folder_for_missing_kind_returns_none(self, tmp_path):
        exporter = SpanJsonExporter(str(tmp_path))
        span = _make_finished_spans(None)[0]
        assert exporter._folder_for(span) is None

    def test_span_to_dict_fields(self, tmp_path):
        exporter = SpanJsonExporter(str(tmp_path))
        span = _make_finished_spans("agent")[0]
        result = exporter._span_to_dict(span)
        assert result["name"] == "operation"
        assert result["kind"] == "INTERNAL"
        assert result["parent_span_id"] is None
        assert result["trace_id"] == f"{span.context.trace_id:032x}"
        assert result["span_id"] == f"{span.context.span_id:016x}"
        assert result["attributes"]["au.span.kind"] == "agent"

    def test_filename_ends_with_json(self, tmp_path):
        exporter = SpanJsonExporter(str(tmp_path))
        span = _make_finished_spans("agent")[0]
        name = exporter._filename_for(span)
        assert name.endswith(".json")
        assert f"{span.context.trace_id:032x}" in name
        assert f"{span.context.span_id:016x}" in name

    def test_export_writes_json_file(self, tmp_path):
        exporter = SpanJsonExporter(str(tmp_path))
        spans = _make_finished_spans("agent")
        assert exporter.export(spans) == SpanExportResult.SUCCESS
        output_dir = tmp_path / "agent"
        files = list(output_dir.glob("*.json"))
        assert len(files) == 1
        payload = json.loads(files[0].read_text(encoding="utf-8"))
        assert payload["name"] == "operation"
        assert payload["attributes"]["au.span.kind"] == "agent"

    def test_export_skips_span_without_kind(self, tmp_path):
        exporter = SpanJsonExporter(str(tmp_path))
        spans = _make_finished_spans(None)
        assert exporter.export(spans) == SpanExportResult.SUCCESS
        assert not list(tmp_path.glob("*.json"))

    def test_force_flush_and_shutdown(self, tmp_path):
        exporter = SpanJsonExporter(str(tmp_path))
        assert exporter.force_flush() is True
        assert exporter.shutdown() is None
