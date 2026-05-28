# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

import json
import os
import pathlib
from datetime import datetime

from agentuniverse.base.tracing.otel.consts import SPAN_SESSION_ID_KEY
from agentuniverse.base.tracing.otel.instrumentation.llm.consts import SpanAttributes as LLMSpanAttributes

SPAN_KIND_FOLDERS = ("llm", "agent", "tool")


class AdminOtelSpanReader:
    """Read exported OpenTelemetry span JSON files for admin monitoring and trace."""

    @staticmethod
    def get_base_dir() -> pathlib.Path:
        return pathlib.Path(os.environ.get("ADMIN_OTEL_SPAN_DIR", "./monitor"))

    @staticmethod
    def is_enabled() -> bool:
        flag = os.environ.get("ADMIN_OTEL_SPAN_ENABLED", "1").strip().lower()
        if flag in {"0", "false", "no", "off"}:
            return False
        base = AdminOtelSpanReader.get_base_dir()
        return base.exists() and any((base / folder).is_dir() for folder in SPAN_KIND_FOLDERS)

    @staticmethod
    def _load_span_file(path: pathlib.Path) -> dict | None:
        try:
            with path.open(encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, json.JSONDecodeError):
            return None

    @staticmethod
    def span_timestamp(span: dict) -> datetime | None:
        start_nano = span.get("start_unix_nano")
        if start_nano is None:
            return None
        try:
            return datetime.fromtimestamp(int(start_nano) / 1e9)
        except (TypeError, ValueError, OSError):
            return None

    @staticmethod
    def span_session_id(span: dict) -> str | None:
        attributes = span.get("attributes") or {}
        session_id = attributes.get(SPAN_SESSION_ID_KEY)
        if session_id is None or str(session_id) in {"", "-1"}:
            return None
        return str(session_id)

    @staticmethod
    def span_kind(span: dict, folder_kind: str) -> str:
        attributes = span.get("attributes") or {}
        kind = attributes.get("au.span.kind")
        if kind:
            return str(kind)
        return folder_kind

    @staticmethod
    def llm_tokens(span: dict) -> int:
        attributes = span.get("attributes") or {}
        if attributes.get("au.span.kind") != "llm":
            return 0
        total = attributes.get(LLMSpanAttributes.AU_LLM_USAGE_TOTAL_TOKENS)
        if total is not None:
            try:
                return max(int(total), 0)
            except (TypeError, ValueError):
                pass
        try:
            prompt = int(attributes.get(LLMSpanAttributes.AU_LLM_USAGE_PROMPT_TOKENS, 0) or 0)
            completion = int(attributes.get(LLMSpanAttributes.AU_LLM_USAGE_COMPLETION_TOKENS, 0) or 0)
            return max(prompt + completion, 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def load_spans(
        start: datetime,
        end: datetime,
        session_id: str | None = None,
        kinds: tuple[str, ...] | None = None,
    ) -> list[dict]:
        if not AdminOtelSpanReader.is_enabled():
            return []

        selected_kinds = kinds or SPAN_KIND_FOLDERS
        base_dir = AdminOtelSpanReader.get_base_dir()
        spans: list[dict] = []

        for kind in selected_kinds:
            folder = base_dir / kind
            if not folder.is_dir():
                continue
            for path in folder.glob("*.json"):
                span = AdminOtelSpanReader._load_span_file(path)
                if not span:
                    continue
                timestamp = AdminOtelSpanReader.span_timestamp(span)
                if timestamp is None or timestamp < start or timestamp > end:
                    continue
                if session_id and AdminOtelSpanReader.span_session_id(span) != session_id:
                    continue
                span.setdefault("attributes", {})
                if "au.span.kind" not in span["attributes"]:
                    span["attributes"]["au.span.kind"] = kind
                spans.append(span)

        spans.sort(key=lambda item: int(item.get("start_unix_nano") or 0))
        return spans

    @staticmethod
    def load_llm_metrics(start: datetime, end: datetime) -> list[tuple[datetime, int]]:
        records: list[tuple[datetime, int]] = []
        for span in AdminOtelSpanReader.load_spans(start, end, kinds=("llm",)):
            timestamp = AdminOtelSpanReader.span_timestamp(span)
            if timestamp is None:
                continue
            records.append((timestamp, AdminOtelSpanReader.llm_tokens(span)))
        return records

    @staticmethod
    def load_session_spans(session_id: str) -> list[dict]:
        if not session_id:
            return []
        start = datetime.min
        end = datetime.max
        return AdminOtelSpanReader.load_spans(start, end, session_id=session_id)
