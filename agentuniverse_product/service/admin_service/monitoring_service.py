# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

import datetime
from collections import defaultdict

from agentuniverse_product.dal.message_library import MessageLibrary, MessageORM
from agentuniverse_product.service.admin_service.dto import (
    AlertItemDTO,
    LlmMetricsResponseDTO,
    MetricPointDTO,
)


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
    def get_llm_metrics(start: str | None = None, end: str | None = None) -> LlmMetricsResponseDTO:
        now = datetime.datetime.now()
        default_start = now - datetime.timedelta(days=AdminMonitoringService.DEFAULT_RANGE_DAYS)
        start_dt = AdminMonitoringService._parse_bound(start, default_start)
        end_dt = AdminMonitoringService._parse_bound(end, now)
        if start_dt > end_dt:
            start_dt, end_dt = end_dt, start_dt

        messages = AdminMonitoringService._load_messages(start_dt, end_dt)
        grouped = AdminMonitoringService._build_series(messages)
        series = [
            grouped.get(bucket, MetricPointDTO(ts=bucket, calls=0, tokens=0))
            for bucket in AdminMonitoringService._date_buckets(start_dt, end_dt)
        ]

        return LlmMetricsResponseDTO(
            series=series,
            total_calls=sum(point.calls for point in series),
            total_tokens=sum(point.tokens for point in series),
            alerts=AdminMonitoringService._detect_alerts(series),
        )

    @staticmethod
    def get_today_usage() -> tuple[int, int]:
        today = datetime.datetime.now().date()
        start = datetime.datetime.combine(today, datetime.time.min)
        end = datetime.datetime.combine(today, datetime.time.max)
        messages = AdminMonitoringService._load_messages(start, end)
        calls = len(messages)
        tokens = sum(AdminMonitoringService._estimate_tokens(content) for _, content in messages)
        return calls, tokens
