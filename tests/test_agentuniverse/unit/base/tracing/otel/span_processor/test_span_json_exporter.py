# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: test_span_json_exporter.py
"""Unit tests for SpanJsonExporter."""

import json
import pytest

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.trace import SpanContext, TraceFlags

from agentuniverse.base.tracing.otel.span_processor.span_json_exporter import SpanJsonExporter


@pytest.fixture
def exporter(tmp_path):
    """Create an exporter rooted in a temporary directory."""
    return SpanJsonExporter(base_dir=str(tmp_path))


def _make_span(kind=None):
    """Build a deterministic ReadableSpan for exporting."""
    ctx = SpanContext(0x11223344556677889900aabbccddeeff,
                      0x1111222233334444, is_remote=False,
                      trace_flags=TraceFlags(1))
    attrs = {SpanJsonExporter.span_kind_attr_name: kind} if kind else {}
    return ReadableSpan(name="test-op", context=ctx, attributes=attrs,
                        start_time=1700000000_000000000,
                        end_time=1700000001_000000000)


class TestSpanJsonExporter:
    """Test SpanJsonExporter folder/filename selection and export."""

    def test_constructor_creates_base_dir(self, tmp_path):
        """The exporter creates the base directory on construction."""
        base = tmp_path / "monitor"
        SpanJsonExporter(base_dir=str(base))
        assert base.is_dir()

    def test_folder_for_uses_span_kind(self, exporter):
        """_folder_for maps the au.span.kind attribute to a subfolder."""
        span = _make_span(kind="llm")
        assert exporter._folder_for(span) == exporter.base_dir / "llm"

    def test_folder_for_none_without_kind(self, exporter):
        """_folder_for returns None when the span has no kind attribute."""
        assert exporter._folder_for(_make_span()) is None

    def test_filename_is_deterministic(self, exporter):
        """_filename_for encodes timestamp, trace id and span id."""
        name = exporter._filename_for(_make_span(kind="llm"))
        assert name == "20231114T221320000000_11223344556677889900aabbccddeeff_1111222233334444.json"

    def test_span_to_dict_fields(self, exporter):
        """_span_to_dict renders the expected keys and formatted ids."""
        d = exporter._span_to_dict(_make_span(kind="llm"))
        assert d["trace_id"] == "11223344556677889900aabbccddeeff"
        assert d["span_id"] == "1111222233334444"
        assert d["parent_span_id"] is None
        assert d["name"] == "test-op"
        assert d["start_unix_nano"] == 1700000000_000000000
        assert d["end_unix_nano"] == 1700000001_000000000
        assert d["attributes"] == {SpanJsonExporter.span_kind_attr_name: "llm"}

    def test_export_writes_json_file(self, exporter):
        """export writes one JSON file per span under its kind folder."""
        result = exporter.export([_make_span(kind="llm")])
        assert result == SpanExportResult.SUCCESS
        files = list((exporter.base_dir / "llm").glob("*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text(encoding="utf-8"))
        assert data["name"] == "test-op"

    def test_export_skips_spans_without_kind(self, exporter):
        """export ignores spans that have no span kind attribute."""
        result = exporter.export([_make_span()])
        assert result == SpanExportResult.SUCCESS
        assert list(exporter.base_dir.glob("*.json")) == []

    def test_force_flush_returns_true(self, exporter):
        """force_flush always reports success."""
        assert exporter.force_flush() is True
