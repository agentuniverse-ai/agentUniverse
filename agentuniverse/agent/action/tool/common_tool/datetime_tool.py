#!/usr/bin/env python3
"""Bounded datetime/timezone tool for agent workflows.

Provides ``now``, ``convert``, ``format``, ``parse``, and ``diff``
operations. All timezone conversions use the IANA timezone database via
``zoneinfo`` (Python 3.9+, zero third-party dependency). Bounded:
``parse`` rejects ambiguous formats, ``diff`` caps at a reasonable range.
"""

# ruff: noqa: TRY003, TRY004

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

# Common datetime formats, tried in order by parse().
_PARSE_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%d",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y",
    "%d-%m-%Y %H:%M:%S",
    "%d-%m-%Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%d %B %Y",
    "%d %b %Y",
]

_DEFAULT_FORMAT = "%Y-%m-%d %H:%M:%S %Z"


class DateTimeTool(Tool):
    """Datetime and timezone operations tool.

    Attributes:
        default_timezone: IANA timezone name for ``now`` when no timezone
            is specified (default ``"UTC"``).
        max_diff_days: Maximum absolute difference in days for ``diff``
            to prevent overflow (default 100000).
    """

    default_timezone: str = "UTC"
    max_diff_days: int = 100_000

    def execute(self, mode: str, datetime_str: str = "",
                timezone_str: str = "", target_timezone: str = "",
                fmt: str = "", unit: str = "days",
                **kwargs) -> dict:
        try:
            op = self._normalize_mode(mode)
            if op == "now":
                return self._now(timezone_str or self.default_timezone)
            if op == "convert":
                return self._convert(datetime_str, timezone_str, target_timezone, fmt)
            if op == "format":
                return self._format_dt(datetime_str, timezone_str, fmt)
            if op == "parse":
                return self._parse(datetime_str)
            if op == "diff":
                return self._diff(datetime_str, kwargs.get("end_datetime", ""),
                                  timezone_str, unit)
            return self._error("validation_error", f"Unknown mode: {mode}")
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc))
        except Exception as exc:
            return self._error("operation_error", str(exc))

    @staticmethod
    def _normalize_mode(mode: str) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")
        normalized = mode.strip().lower()
        allowed = {"now", "convert", "format", "parse", "diff"}
        if normalized not in allowed:
            raise ValueError(f"mode must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @staticmethod
    def _error(error_type: str, message: str) -> dict:
        return {"status": "error", "error_type": error_type, "error": message}

    @staticmethod
    def _ok(**kwargs) -> dict:
        return {"status": "success", **kwargs}

    def _get_tz(self, tz_name: str):
        if not tz_name or tz_name.upper() == "UTC":
            return timezone.utc
        try:
            return ZoneInfo(tz_name)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(
                f"Unknown timezone: {tz_name!r}. Use an IANA timezone name "
                f"like 'America/New_York', 'Asia/Shanghai', 'Europe/London'."
            ) from exc

    def _now(self, tz_name: str) -> dict:
        tz = self._get_tz(tz_name)
        now = datetime.now(tz)
        return self._ok(
            mode="now",
            datetime=now.strftime(_DEFAULT_FORMAT),
            iso=now.isoformat(),
            timestamp=now.timestamp(),
            timezone=str(tz),
        )

    def _convert(self, dt_str: str, from_tz: str, to_tz: str,
                 fmt: str) -> dict:
        dt = self._parse_datetime(dt_str, from_tz)
        target = self._get_tz(to_tz or "UTC")
        converted = dt.astimezone(target)
        output_format = fmt or _DEFAULT_FORMAT
        return self._ok(
            mode="convert",
            original=dt.strftime(output_format),
            converted=converted.strftime(output_format),
            original_iso=dt.isoformat(),
            converted_iso=converted.isoformat(),
            from_timezone=str(dt.tzinfo),
            to_timezone=str(target),
        )

    def _format_dt(self, dt_str: str, tz_name: str, fmt: str) -> dict:
        dt = self._parse_datetime(dt_str, tz_name)
        output_format = fmt or _DEFAULT_FORMAT
        return self._ok(
            mode="format",
            formatted=dt.strftime(output_format),
            iso=dt.isoformat(),
        )

    def _parse(self, dt_str: str) -> dict:
        if not dt_str:
            return self._error("validation_error", "datetime_str is required")
        parsed = self._try_parse_formats(dt_str)
        if parsed is None:
            return self._error(
                "validation_error",
                f"Could not parse {dt_str!r}. Supported formats include: "
                f"YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, ISO 8601, etc.")
        return self._ok(
            mode="parse",
            datetime=parsed.strftime(_DEFAULT_FORMAT),
            iso=parsed.isoformat(),
        )

    def _diff(self, start_str: str, end_str: str, tz_name: str,
              unit: str) -> dict:
        if not start_str:
            return self._error("validation_error", "datetime_str (start) is required")
        tz = self._get_tz(tz_name or "UTC")
        start = self._parse_datetime(start_str, tz_name)
        if end_str:
            end = self._parse_datetime(end_str, tz_name)
        else:
            end = datetime.now(tz)

        delta = end - start
        unit = (unit or "days").lower()

        if unit in ("days", "day", "d"):
            value = delta.total_seconds() / 86400
        elif unit in ("hours", "hour", "h"):
            value = delta.total_seconds() / 3600
        elif unit in ("minutes", "minute", "min", "m"):
            value = delta.total_seconds() / 60
        elif unit in ("seconds", "second", "sec", "s"):
            value = delta.total_seconds()
        else:
            raise ValueError(f"Unknown unit: {unit!r}. Use days, hours, minutes, or seconds.")

        if abs(value) > self.max_diff_days and unit in ("days", "d"):
            raise ValueError(
                f"Difference exceeds max_diff_days ({self.max_diff_days})")

        return self._ok(
            mode="diff",
            start=start.isoformat(),
            end=end.isoformat(),
            unit=unit,
            value=round(value, 6),
        )

    def _parse_datetime(self, dt_str: str, tz_name: str) -> datetime:
        parsed = self._try_parse_formats(dt_str)
        if parsed is None:
            raise ValueError(
                f"Could not parse {dt_str!r}. Supported formats: "
                f"YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, ISO 8601, etc.")
        tz = self._get_tz(tz_name or self.default_timezone)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=tz)
        return parsed

    @staticmethod
    def _try_parse_formats(dt_str: str) -> Optional[datetime]:
        dt_str = dt_str.strip()
        for fmt in _PARSE_FORMATS:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue
        # Try ISO 8601.
        try:
            return datetime.fromisoformat(
                dt_str.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _initialize_by_component_configer(self, configer: ComponentConfiger) -> "DateTimeTool":
        super()._initialize_by_component_configer(configer)
        if hasattr(configer, "default_timezone"):
            self.default_timezone = configer.default_timezone
        if hasattr(configer, "max_diff_days"):
            self.max_diff_days = configer.max_diff_days
        return self
