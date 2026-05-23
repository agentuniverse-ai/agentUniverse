# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

import datetime
from collections import defaultdict

from agentuniverse_product.dal.message_library import MessageLibrary, MessageORM
from agentuniverse_product.service.admin_service.dto import (
    AlertItemDTO,
    CallerRankDTO,
    LlmMetricsResponseDTO,
    MetricPointDTO,
    RecentCallDTO,
    ResourceSnapshotDTO,
)
from agentuniverse_product.service.admin_service.otel_span_reader import AdminOtelSpanReader


class AdminMonitoringService:
    """Aggregate lightweight LLM metrics from persisted session messages."""

    DEFAULT_RANGE_DAYS = 7
    TOKEN_CHARS_RATIO = 4

    @staticmethod
    def _parse_bound(value: str | None, fallback: datetime.datetime) -> datetime.datetime:
        if not value:
            return fallback
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.datetime.strptime(value, fmt)
            except ValueError:
                continue
        return fallback

    @staticmethod
    def _normalize_content(content: object | None) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        return str(content)

    @staticmethod
    def _estimate_tokens(content: object | None) -> int:
        text = AdminMonitoringService._normalize_content(content).strip()
        if not text:
            return 0
        return max(len(text) // AdminMonitoringService.TOKEN_CHARS_RATIO, 1)

    @staticmethod
    def _load_messages(start: datetime.datetime, end: datetime.datetime) -> list[tuple[datetime.datetime, str]]:
        try:
            with MessageLibrary().get_db_session() as db_session:
                rows = (
                    db_session.query(MessageORM)
                    .filter(MessageORM.gmt_created >= start, MessageORM.gmt_created <= end)
                    .all()
                )
                return [(row.gmt_created, AdminMonitoringService._normalize_content(row.content)) for row in rows]
        except Exception:
            return []

    @staticmethod
    def _date_buckets(start: datetime.datetime, end: datetime.datetime) -> list[str]:
        current = start.date()
        end_date = end.date()
        buckets: list[str] = []
        while current <= end_date:
            buckets.append(current.strftime("%Y-%m-%d"))
            current += datetime.timedelta(days=1)
        return buckets

    @staticmethod
    def _build_series_from_otel(records: list[tuple[datetime.datetime, int]]) -> dict[str, MetricPointDTO]:
        grouped: dict[str, dict[str, int]] = defaultdict(lambda: {"calls": 0, "tokens": 0})
        for created_at, tokens in records:
            bucket = created_at.strftime("%Y-%m-%d")
            grouped[bucket]["calls"] += 1
            grouped[bucket]["tokens"] += tokens

        return {
            bucket: MetricPointDTO(ts=bucket, calls=values["calls"], tokens=values["tokens"])
            for bucket, values in grouped.items()
        }

    @staticmethod
    def _resolve_series(
        start_dt: datetime.datetime,
        end_dt: datetime.datetime,
    ) -> tuple[dict[str, MetricPointDTO], str]:
        if AdminOtelSpanReader.is_enabled():
            otel_records = AdminOtelSpanReader.load_llm_metrics(start_dt, end_dt)
            return AdminMonitoringService._build_series_from_otel(otel_records), "otel"

        messages = AdminMonitoringService._load_messages(start_dt, end_dt)
        return AdminMonitoringService._build_series(messages), "message_estimate"

    @staticmethod
    def _build_series(messages: list[tuple[datetime.datetime, str]]) -> dict[str, MetricPointDTO]:
        grouped: dict[str, dict[str, int]] = defaultdict(lambda: {"calls": 0, "tokens": 0})
        for created_at, content in messages:
            bucket = created_at.strftime("%Y-%m-%d")
            grouped[bucket]["calls"] += 1
            grouped[bucket]["tokens"] += AdminMonitoringService._estimate_tokens(content)

        return {
            bucket: MetricPointDTO(ts=bucket, calls=values["calls"], tokens=values["tokens"])
            for bucket, values in grouped.items()
        }

    @staticmethod
    def _detect_alerts(series: list[MetricPointDTO]) -> list[AlertItemDTO]:
        if not series or sum(point.calls for point in series) == 0:
            return [
                AlertItemDTO(
                    level="info",
                    message="No LLM activity recorded in the selected time window.",
                )
            ]

        if len(series) < 2:
            return []

        *previous, latest = series
        previous_calls = sum(point.calls for point in previous) / max(len(previous), 1)
        previous_tokens = sum(point.tokens for point in previous) / max(len(previous), 1)

        alerts: list[AlertItemDTO] = []
        if previous_calls > 0 and latest.calls >= previous_calls * 2:
            alerts.append(
                AlertItemDTO(
                    level="warning",
                    message="Today's LLM call volume is more than 2x the recent daily average.",
                )
            )
        if previous_tokens > 0 and latest.tokens >= previous_tokens * 2:
            alerts.append(
                AlertItemDTO(
                    level="warning",
                    message="Today's token usage is more than 2x the recent daily average.",
                )
            )
        return alerts

    @staticmethod
    def _percentile(values: list[float], ratio: float) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        index = min(len(ordered) - 1, int(round((len(ordered) - 1) * ratio)))
        return ordered[index]

    @staticmethod
    def _build_otel_insights(
        start_dt: datetime.datetime,
        end_dt: datetime.datetime,
    ) -> tuple[float, list[CallerRankDTO], list[RecentCallDTO]]:
        spans = AdminOtelSpanReader.load_spans(start_dt, end_dt, kinds=("llm",))
        durations: list[float] = []
        caller_counts: dict[str, int] = defaultdict(int)
        recent: list[tuple[datetime.datetime, str, int]] = []

        for span in spans:
            start_nano = span.get("start_unix_nano")
            end_nano = span.get("end_unix_nano")
            if start_nano is not None and end_nano is not None:
                durations.append(max((int(end_nano) - int(start_nano)) / 1e6, 0.0))

            attributes = span.get("attributes") or {}
            caller = str(attributes.get("au.llm.name") or span.get("name") or "unknown")
            caller_counts[caller] += 1

            timestamp = AdminOtelSpanReader.span_timestamp(span)
            if timestamp is not None:
                recent.append(
                    (
                        timestamp,
                        caller,
                        AdminOtelSpanReader.llm_tokens(span),
                    )
                )

        p95 = AdminMonitoringService._percentile(durations, 0.95)
        top_callers = [
            CallerRankDTO(name=name, calls=calls)
            for name, calls in sorted(caller_counts.items(), key=lambda item: item[1], reverse=True)[:5]
        ]
        recent_calls = [
            RecentCallDTO(
                ts=item[0].strftime("%Y-%m-%d %H:%M:%S"),
                label=item[1],
                tokens=item[2],
            )
            for item in sorted(recent, key=lambda row: row[0], reverse=True)[:8]
        ]
        return p95, top_callers, recent_calls

    @staticmethod
    def _build_message_insights(
        messages: list[tuple[datetime.datetime, str]],
    ) -> tuple[float, list[CallerRankDTO], list[RecentCallDTO]]:
        recent = sorted(messages, key=lambda item: item[0], reverse=True)[:8]
        recent_calls = [
            RecentCallDTO(
                ts=created_at.strftime("%Y-%m-%d %H:%M:%S"),
                label="session-message",
                tokens=AdminMonitoringService._estimate_tokens(content),
            )
            for created_at, content in recent
        ]
        return 0.0, [], recent_calls

    @staticmethod
    def _resource_snapshot() -> ResourceSnapshotDTO:
        from agentuniverse_product.service.admin_service.resource_service import AdminResourceService

        summary = AdminResourceService.get_dashboard_summary()
        return ResourceSnapshotDTO(
            agents=summary.total_agents,
            tools=summary.total_tools,
            knowledge=summary.total_knowledge,
            workflows=summary.total_workflows,
            llms=summary.total_llms,
            memories=summary.total_memories,
        )

    @staticmethod
    def get_llm_metrics(start: str | None = None, end: str | None = None) -> LlmMetricsResponseDTO:
        now = datetime.datetime.now()
        default_start = now - datetime.timedelta(days=AdminMonitoringService.DEFAULT_RANGE_DAYS)
        start_dt = AdminMonitoringService._parse_bound(start, default_start)
        end_dt = AdminMonitoringService._parse_bound(end, now)
        if start_dt > end_dt:
            start_dt, end_dt = end_dt, start_dt

        grouped, data_source = AdminMonitoringService._resolve_series(start_dt, end_dt)
        series = [
            grouped.get(bucket, MetricPointDTO(ts=bucket, calls=0, tokens=0))
            for bucket in AdminMonitoringService._date_buckets(start_dt, end_dt)
        ]

        if data_source == "otel":
            p95_latency_ms, top_callers, recent_calls = AdminMonitoringService._build_otel_insights(
                start_dt, end_dt
            )
        else:
            messages = AdminMonitoringService._load_messages(start_dt, end_dt)
            p95_latency_ms, top_callers, recent_calls = AdminMonitoringService._build_message_insights(messages)

        return LlmMetricsResponseDTO(
            series=series,
            total_calls=sum(point.calls for point in series),
            total_tokens=sum(point.tokens for point in series),
            alerts=AdminMonitoringService._detect_alerts(series),
            data_source=data_source,
            p95_latency_ms=p95_latency_ms,
            top_callers=top_callers,
            recent_calls=recent_calls,
            resource_snapshot=AdminMonitoringService._resource_snapshot(),
        )

    @staticmethod
    def get_today_usage() -> tuple[int, int]:
        today = datetime.datetime.now().date()
        start = datetime.datetime.combine(today, datetime.time.min)
        end = datetime.datetime.combine(today, datetime.time.max)
        if AdminOtelSpanReader.is_enabled():
            records = AdminOtelSpanReader.load_llm_metrics(start, end)
            return len(records), sum(tokens for _, tokens in records)

        messages = AdminMonitoringService._load_messages(start, end)
        calls = len(messages)
        tokens = sum(AdminMonitoringService._estimate_tokens(content) for _, content in messages)
        return calls, tokens
