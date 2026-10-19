#!/usr/bin/env python3
"""Bounded iCalendar creation, reading, inspection, and merging."""

# Public execute() converts validation failures into structured tool errors.
# ruff: noqa: C901, TRY003, TRY004

import json
import os
import tempfile
import uuid
from datetime import date, datetime, timedelta
from typing import Any, ClassVar, cast
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool


class ICalendarTool(Tool):
    """Create, read, inspect, and merge RFC 5545 ``.ics`` calendars."""

    base_dir: str = "."
    max_read_bytes: int = 10 * 1024 * 1024
    max_write_bytes: int = 10 * 1024 * 1024
    max_events: int = 1_000
    max_text_chars: int = 200_000
    max_output_chars: int = 500_000
    max_field_chars: int = 20_000
    max_attendees_per_event: int = 100
    max_categories_per_event: int = 100
    max_alarms_per_event: int = 10
    max_properties_per_event: int = 50
    max_input_files: int = 100
    max_merge_bytes: int = 50 * 1024 * 1024

    _EVENT_FIELDS: ClassVar[set[str]] = {
        "uid",
        "summary",
        "start",
        "end",
        "description",
        "location",
        "status",
        "organizer",
        "attendees",
        "categories",
        "url",
        "rrule",
        "alarms",
    }
    _STATUSES: ClassVar[set[str]] = {"TENTATIVE", "CONFIRMED", "CANCELLED"}

    def execute(
        self,
        mode: str,
        file_path: str,
        events: list[dict[str, Any]] | None = None,
        input_paths: list[str] | None = None,
        overwrite: bool = False,
        calendar_name: str | None = None,
        calendar_description: str | None = None,
        default_timezone: str | None = None,
    ) -> dict[str, Any]:
        """Execute ``create``, ``read``, ``info``, or ``merge``."""
        try:
            self._validate_config()
            operation = self._mode(mode)
            path = self._ics_path(file_path, "file_path")
            if operation == "create":
                return self._create(
                    path,
                    events,
                    overwrite,
                    calendar_name,
                    calendar_description,
                    default_timezone,
                )
            if operation == "merge":
                return self._merge(
                    path,
                    input_paths,
                    overwrite,
                    calendar_name,
                    calendar_description,
                )
            calendar = self._load(path)
            return self._read(path, calendar) if operation == "read" else self._info(path, calendar)
        except ImportError as exc:
            return self._error(
                file_path,
                "dependency_error",
                "icalendar is required. Install it with: pip install icalendar",
                str(exc),
            )
        except (TypeError, ValueError) as exc:
            return self._error(file_path, "validation_error", str(exc))
        except Exception as exc:
            return self._error(file_path, "operation_error", f"iCalendar operation failed: {exc}")

    @staticmethod
    def _error(path: Any, kind: str, message: str, detail: str | None = None) -> dict[str, Any]:
        result = {"status": "error", "error_type": kind, "error": message, "file_path": path}
        if detail:
            result["detail"] = detail
        return result

    def _validate_config(self) -> None:
        for name in (
            "max_read_bytes",
            "max_write_bytes",
            "max_events",
            "max_text_chars",
            "max_output_chars",
            "max_field_chars",
            "max_attendees_per_event",
            "max_categories_per_event",
            "max_alarms_per_event",
            "max_properties_per_event",
            "max_input_files",
            "max_merge_bytes",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.base_dir, str) or not self.base_dir:
            raise ValueError("base_dir must be a non-empty string")

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("mode must be a non-empty string")
        operation = value.strip().lower()
        if operation not in {"create", "read", "info", "merge"}:
            raise ValueError("mode must be create, read, info, or merge")
        return operation

    def _ics_path(self, value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        if os.path.splitext(value)[1].lower() != ".ics":
            raise ValueError(f"{field} must have a .ics extension")
        return cast(str, resolve_safe_path(value, self.base_dir))

    @staticmethod
    def _dependency() -> tuple[Any, Any, Any]:
        try:
            from icalendar import Alarm, Calendar, Event
        except ImportError as exc:
            raise ImportError("No module named 'icalendar'") from exc
        return Calendar, Event, Alarm

    def _load(self, path: str) -> Any:
        if not os.path.isfile(path):
            raise ValueError(f"file_path does not exist: {path}")
        size = os.path.getsize(path)
        if size > self.max_read_bytes:
            raise ValueError(f"file_path exceeds max_read_bytes ({self.max_read_bytes})")
        Calendar, _, _ = self._dependency()
        with open(path, "rb") as stream:
            calendar = Calendar.from_ical(stream.read())
        self._validate_loaded_calendar(calendar)
        return calendar

    def _validate_loaded_calendar(self, calendar: Any) -> None:
        events = list(calendar.walk("VEVENT"))
        if len(events) > self.max_events:
            raise ValueError(f"calendar exceeds max_events ({self.max_events})")
        for event_index, event in enumerate(events):
            properties = event.property_items()
            if len(properties) > self.max_properties_per_event:
                raise ValueError(
                    f"event {event_index} exceeds max_properties_per_event ({self.max_properties_per_event})"
                )
            for name, value in properties:
                if len(str(value)) > self.max_field_chars:
                    raise ValueError(f"event {event_index}.{name} exceeds max_field_chars ({self.max_field_chars})")
            if len(self._multi_property(event, "attendee")) > self.max_attendees_per_event:
                raise ValueError(
                    f"event {event_index} exceeds max_attendees_per_event ({self.max_attendees_per_event})"
                )
            if len(self._categories(event)) > self.max_categories_per_event:
                raise ValueError(
                    f"event {event_index} exceeds max_categories_per_event ({self.max_categories_per_event})"
                )
            alarms = [component for component in event.subcomponents if component.name == "VALARM"]
            if len(alarms) != len(event.subcomponents):
                raise ValueError(f"event {event_index} contains an unsupported nested component")
            if len(alarms) > self.max_alarms_per_event:
                raise ValueError(f"event {event_index} exceeds max_alarms_per_event ({self.max_alarms_per_event})")
            for alarm_index, alarm in enumerate(alarms):
                for name, value in alarm.property_items():
                    if len(str(value)) > self.max_field_chars:
                        raise ValueError(
                            f"event {event_index}.alarm {alarm_index}.{name} exceeds max_field_chars "
                            f"({self.max_field_chars})"
                        )

    def _create(
        self,
        path: str,
        events: Any,
        overwrite: Any,
        name: Any,
        description: Any,
        default_timezone: Any,
    ) -> dict[str, Any]:
        self._check_overwrite(path, overwrite)
        validated = self._validate_events(events, default_timezone)
        calendar = self._new_calendar(name, description)
        for spec in validated:
            calendar.add_component(self._event_component(spec))
        self._atomic_write(calendar.to_ical(), path)
        return {
            "status": "success",
            "mode": "create",
            "file_path": path,
            "event_count": len(validated),
            "file_size": os.path.getsize(path),
            "overwritten": overwrite,
        }

    def _merge(
        self,
        path: str,
        input_paths: Any,
        overwrite: Any,
        name: Any,
        description: Any,
    ) -> dict[str, Any]:
        self._check_overwrite(path, overwrite)
        if not isinstance(input_paths, list) or not input_paths:
            raise ValueError("input_paths must be a non-empty list")
        if len(input_paths) > self.max_input_files:
            raise ValueError(f"input_paths exceeds max_input_files ({self.max_input_files})")
        safe_inputs = []
        calendar = self._new_calendar(name, description)
        seen = set()
        event_count = 0
        total_bytes = 0
        for index, raw_path in enumerate(input_paths):
            safe_path = self._ics_path(raw_path, f"input_paths[{index}]")
            if safe_path == path:
                raise ValueError("file_path must not also appear in input_paths")
            if not os.path.isfile(safe_path):
                raise ValueError(f"input_paths[{index}] does not exist: {safe_path}")
            total_bytes += os.path.getsize(safe_path)
            if total_bytes > self.max_merge_bytes:
                raise ValueError(f"input_paths exceed max_merge_bytes ({self.max_merge_bytes})")
            source = self._load(safe_path)
            for event in source.walk("VEVENT"):
                event_count += 1
                if event_count > self.max_events:
                    raise ValueError(f"merged calendar exceeds max_events ({self.max_events})")
                uid = str(event.get("uid", "")).strip()
                if not uid:
                    raise ValueError("every merged event must have a UID")
                if uid in seen:
                    raise ValueError(f"duplicate event UID during merge: {uid}")
                seen.add(uid)
                calendar.add_component(event)
            safe_inputs.append(safe_path)
        self._validate_loaded_calendar(calendar)
        self._atomic_write(calendar.to_ical(), path)
        return {
            "status": "success",
            "mode": "merge",
            "file_path": path,
            "input_paths": safe_inputs,
            "event_count": event_count,
            "file_size": os.path.getsize(path),
            "overwritten": overwrite,
        }

    @staticmethod
    def _new_calendar(name: Any, description: Any) -> Any:
        Calendar, _, _ = ICalendarTool._dependency()
        calendar = Calendar()
        calendar.add("prodid", "-//agentUniverse//ICalendarTool//EN")
        calendar.add("version", "2.0")
        calendar.add("calscale", "GREGORIAN")
        for field, value, target in (
            ("calendar_name", name, "X-WR-CALNAME"),
            ("calendar_description", description, "X-WR-CALDESC"),
        ):
            if value is not None:
                if not isinstance(value, str) or not value.strip() or len(value) > 2_000:
                    raise ValueError(f"{field} must be a non-empty string of at most 2000 characters")
                calendar.add(target, value.strip())
        return calendar

    @staticmethod
    def _check_overwrite(path: str, overwrite: Any) -> None:
        if not isinstance(overwrite, bool):
            raise ValueError("overwrite must be a boolean")
        if os.path.exists(path) and not overwrite:
            raise ValueError(f"file already exists: {path}; set overwrite=true to replace it")

    def _validate_events(self, value: Any, default_timezone: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list) or not value:
            raise ValueError("events must be a non-empty list")
        if len(value) > self.max_events:
            raise ValueError(f"events exceeds max_events ({self.max_events})")
        timezone = self._timezone(default_timezone)
        total_chars = 0
        output = []
        seen_uids = set()
        for index, raw in enumerate(value):
            if not isinstance(raw, dict):
                raise ValueError(f"events[{index}] must be an object")
            unknown = set(raw) - self._EVENT_FIELDS
            if unknown:
                raise ValueError(f"events[{index}] has unknown fields: {', '.join(sorted(unknown))}")
            summary = self._text(raw.get("summary"), f"events[{index}].summary", required=True)
            start = self._temporal(raw.get("start"), f"events[{index}].start", timezone)
            end = self._temporal(raw.get("end"), f"events[{index}].end", timezone)
            if isinstance(start, datetime) != isinstance(end, datetime):
                raise ValueError(f"events[{index}] start and end must both be dates or both be date-times")
            if end <= start:
                raise ValueError(f"events[{index}].end must be after start")
            uid = self._text(raw.get("uid", f"{uuid.uuid4()}@agentuniverse"), f"events[{index}].uid", True)
            if uid in seen_uids:
                raise ValueError(f"duplicate event UID: {uid}")
            seen_uids.add(uid)
            spec = {"uid": uid, "summary": summary, "start": start, "end": end}
            for field in ("description", "location", "organizer", "url", "rrule"):
                spec[field] = self._text(raw.get(field), f"events[{index}].{field}")
            status = raw.get("status")
            if status is not None:
                if not isinstance(status, str) or status.strip().upper() not in self._STATUSES:
                    raise ValueError(f"events[{index}].status must be tentative, confirmed, or cancelled")
                status = status.strip().upper()
            spec["status"] = status
            spec["attendees"] = self._string_list(
                raw.get("attendees", []), f"events[{index}].attendees", self.max_attendees_per_event
            )
            spec["categories"] = self._string_list(
                raw.get("categories", []),
                f"events[{index}].categories",
                self.max_categories_per_event,
            )
            alarms = raw.get("alarms", [])
            if not isinstance(alarms, list) or len(alarms) > self.max_alarms_per_event:
                raise ValueError(f"events[{index}].alarms must be a list limited to {self.max_alarms_per_event}")
            normalized_alarms = []
            for alarm_index, alarm in enumerate(alarms):
                if not isinstance(alarm, dict) or set(alarm) - {"minutes_before", "description"}:
                    raise ValueError(f"events[{index}].alarms[{alarm_index}] has invalid fields")
                minutes = alarm.get("minutes_before")
                if isinstance(minutes, bool) or not isinstance(minutes, int) or not 0 <= minutes <= 525_600:
                    raise ValueError(f"events[{index}].alarms[{alarm_index}].minutes_before is invalid")
                alarm_description = self._text(
                    alarm.get("description", "Reminder"),
                    f"events[{index}].alarms[{alarm_index}].description",
                    True,
                )
                normalized_alarms.append({"minutes_before": minutes, "description": alarm_description})
            spec["alarms"] = normalized_alarms
            total_chars += sum(len(str(item or "")) for item in spec.values() if not isinstance(item, (list, date)))
            total_chars += sum(len(item) for item in spec["attendees"] + spec["categories"])
            total_chars += sum(len(item["description"]) for item in normalized_alarms)
            output.append(spec)
        if total_chars > self.max_text_chars:
            raise ValueError(f"event text exceeds max_text_chars ({self.max_text_chars})")
        return output

    @staticmethod
    def _timezone(value: Any) -> ZoneInfo | None:
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise ValueError("default_timezone must be a non-empty IANA timezone string")
        try:
            return ZoneInfo(value.strip())
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"unknown default_timezone: {value}") from exc

    @staticmethod
    def _temporal(value: Any, field: str, timezone: ZoneInfo | None) -> date | datetime:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be an ISO date or date-time string")
        text = value.strip()
        if "T" not in text and " " not in text:
            try:
                return date.fromisoformat(text)
            except ValueError as exc:
                raise ValueError(f"{field} must be an ISO date or date-time string") from exc
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"{field} must be an ISO date or date-time string") from exc
        if parsed.tzinfo is None and timezone is not None:
            parsed = parsed.replace(tzinfo=timezone)
        return parsed

    def _text(self, value: Any, field: str, required: bool = False) -> str | None:
        if value is None and not required:
            return None
        if not isinstance(value, str) or (required and not value.strip()):
            raise ValueError(f"{field} must be a non-empty string")
        value = value.strip()
        if len(value) > self.max_field_chars or "\x00" in value:
            raise ValueError(f"{field} is invalid or too long")
        return value

    def _string_list(self, value: Any, field: str, limit: int) -> list[str]:
        if not isinstance(value, list) or len(value) > limit:
            raise ValueError(f"{field} must be a list limited to {limit} items")
        output = []
        for index, item in enumerate(value):
            normalized = self._text(item, f"{field}[{index}]", True)
            output.append(cast(str, normalized))
        return output

    @staticmethod
    def _event_component(spec: dict[str, Any]) -> Any:
        _, Event, Alarm = ICalendarTool._dependency()
        event = Event()
        for target, field in (("uid", "uid"), ("summary", "summary"), ("dtstart", "start"), ("dtend", "end")):
            event.add(target, spec[field])
        for field in ("description", "location", "status", "organizer", "url", "rrule"):
            if spec[field]:
                event.add(field, spec[field])
        for attendee in spec["attendees"]:
            event.add("attendee", attendee)
        if spec["categories"]:
            event.add("categories", spec["categories"])
        event.add("dtstamp", datetime.now().astimezone())
        for alarm_spec in spec["alarms"]:
            alarm = Alarm()
            alarm.add("action", "DISPLAY")
            alarm.add("description", alarm_spec["description"])
            alarm.add("trigger", timedelta(minutes=-alarm_spec["minutes_before"]))
            event.add_component(alarm)
        return event

    def _read(self, path: str, calendar: Any) -> dict[str, Any]:
        remaining = self.max_text_chars
        results = []
        truncated = False

        def consume(value: Any) -> str:
            nonlocal remaining, truncated
            output, remaining, cut = self._bounded(value, remaining)
            truncated = truncated or cut
            return output

        for component in calendar.walk("VEVENT"):
            event = {
                "uid": consume(self._property(component, "uid")),
                "summary": consume(self._property(component, "summary")),
                "start": consume(self._decoded_temporal(component, "dtstart")),
                "end": consume(self._decoded_temporal(component, "dtend")),
                "description": consume(self._property(component, "description")),
                "location": consume(self._property(component, "location")),
                "status": consume(self._property(component, "status")),
                "organizer": consume(self._property(component, "organizer")),
                "url": consume(self._property(component, "url")),
                "rrule": consume(self._property(component, "rrule")),
                "attendees": [consume(value) for value in self._multi_property(component, "attendee")],
                "categories": [consume(value) for value in self._categories(component)],
                "alarms": [
                    {
                        "action": consume(self._property(alarm, "action")),
                        "description": consume(self._property(alarm, "description")),
                        "trigger": consume(self._property(alarm, "trigger")),
                    }
                    for alarm in component.subcomponents
                    if alarm.name == "VALARM"
                ],
            }
            results.append(event)
        result = {
            "status": "success",
            "mode": "read",
            "file_path": path,
            "calendar_name": consume(self._property(calendar, "X-WR-CALNAME")),
            "calendar_description": consume(self._property(calendar, "X-WR-CALDESC")),
            "event_count": len(results),
            "returned_event_count": len(results),
            "events": results,
            "truncated": truncated,
        }
        while result["events"] and self._json_size(result) > self.max_output_chars:
            result["events"].pop()
            result["returned_event_count"] = len(result["events"])
            result["truncated"] = True
        if self._json_size(result) > self.max_output_chars:
            result["calendar_name"] = ""
            result["calendar_description"] = ""
            result["truncated"] = True
        return result

    def _info(self, path: str, calendar: Any) -> dict[str, Any]:
        events = list(calendar.walk("VEVENT"))
        starts = [self._decoded_temporal(event, "dtstart") for event in events if event.get("dtstart")]
        ends = [self._decoded_temporal(event, "dtend") for event in events if event.get("dtend")]
        result = {
            "status": "success",
            "mode": "info",
            "file_path": path,
            "file_size": os.path.getsize(path),
            "event_count": len(events),
            "calendar_name": self._property(calendar, "X-WR-CALNAME"),
            "calendar_description": self._property(calendar, "X-WR-CALDESC"),
            "range_start": min(starts) if starts else None,
            "range_end": max(ends) if ends else None,
            "summaries": [self._property(event, "summary")[:500] for event in events],
        }
        while result["summaries"] and self._json_size(result) > self.max_output_chars:
            result["summaries"].pop()
        return result

    @staticmethod
    def _json_size(value: Any) -> int:
        return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")))

    @staticmethod
    def _property(component: Any, name: str) -> str:
        value = component.get(name)
        return str(value) if value is not None else ""

    @staticmethod
    def _multi_property(component: Any, name: str) -> list[str]:
        value = component.get(name)
        if value is None:
            return []
        values = value if isinstance(value, list) else [value]
        return [str(item) for item in values]

    @staticmethod
    def _categories(component: Any) -> list[str]:
        value = component.get("categories")
        if value is None:
            return []
        values = getattr(value, "cats", value if isinstance(value, list) else [value])
        return [str(item) for item in values]

    @staticmethod
    def _decoded_temporal(component: Any, name: str) -> str:
        try:
            value = component.decoded(name)
        except KeyError:
            return ""
        return value.isoformat() if isinstance(value, (date, datetime)) else str(value)

    @staticmethod
    def _bounded(value: Any, remaining: int) -> tuple[str, int, bool]:
        text = str(value or "")
        if len(text) <= remaining:
            return text, remaining - len(text), False
        if remaining <= 0:
            return "", 0, True
        if remaining == 1:
            return "…", 0, True
        return text[: remaining - 1] + "…", 0, True

    def _atomic_write(self, data: bytes, path: str) -> None:
        if len(data) > self.max_write_bytes:
            raise ValueError(f"generated calendar exceeds max_write_bytes ({self.max_write_bytes})")
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix=".icalendar-", suffix=".ics", dir=directory, delete=False
            ) as stream:
                temporary_path = stream.name
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_path, path)
            temporary_path = None
        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.unlink(temporary_path)
