import json
from datetime import datetime
from pathlib import Path

from agentuniverse_product.service.admin_service.otel_span_reader import AdminOtelSpanReader


def _write_span(base_dir: Path, kind: str, filename: str, payload: dict) -> None:
    folder = base_dir / kind
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / filename).open("w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def test_load_llm_metrics_from_otel_spans(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_OTEL_SPAN_DIR", str(tmp_path))
    _write_span(
        tmp_path,
        "llm",
        "20260401T100000000000_abc_span.json",
        {
            "trace_id": "abc",
            "span_id": "span001",
            "parent_span_id": None,
            "name": "au.llm.demo",
            "start_unix_nano": int(datetime(2026, 4, 1, 10, 0, 0).timestamp() * 1e9),
            "end_unix_nano": int(datetime(2026, 4, 1, 10, 0, 1).timestamp() * 1e9),
            "status": "OK",
            "attributes": {
                "au.span.kind": "llm",
                "au.trace.session.id": "session-1",
                "au.llm.usage.total_tokens": 128,
            },
        },
    )

    records = AdminOtelSpanReader.load_llm_metrics(
        datetime(2026, 4, 1, 0, 0, 0),
        datetime(2026, 4, 1, 23, 59, 59),
    )

    assert len(records) == 1
    assert records[0][1] == 128


def test_load_session_spans_filters_by_session_id(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_OTEL_SPAN_DIR", str(tmp_path))
    common = {
        "trace_id": "abc",
        "start_unix_nano": int(datetime(2026, 4, 1, 10, 0, 0).timestamp() * 1e9),
        "end_unix_nano": int(datetime(2026, 4, 1, 10, 0, 2).timestamp() * 1e9),
        "status": "OK",
    }
    _write_span(
        tmp_path,
        "agent",
        "agent.json",
        {
            **common,
            "span_id": "agent001",
            "parent_span_id": None,
            "name": "au.agent.demo",
            "attributes": {
                "au.span.kind": "agent",
                "au.trace.session.id": "session-2",
                "au.agent.name": "demo_agent",
            },
        },
    )
    _write_span(
        tmp_path,
        "llm",
        "llm.json",
        {
            **common,
            "span_id": "llm001",
            "parent_span_id": "agent001",
            "name": "au.llm.demo",
            "attributes": {
                "au.span.kind": "llm",
                "au.trace.session.id": "session-1",
                "au.llm.name": "demo_llm",
                "au.llm.usage.total_tokens": 64,
            },
        },
    )

    spans = AdminOtelSpanReader.load_session_spans("session-1")

    assert len(spans) == 1
    assert spans[0]["span_id"] == "llm001"


def test_is_enabled_respects_flag(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_OTEL_SPAN_DIR", str(tmp_path))
    (tmp_path / "llm").mkdir()
    monkeypatch.setenv("ADMIN_OTEL_SPAN_ENABLED", "0")
    assert AdminOtelSpanReader.is_enabled() is False
