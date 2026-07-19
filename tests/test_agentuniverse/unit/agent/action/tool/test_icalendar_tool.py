#!/usr/bin/env python3
"""Tests for the built-in ICalendarTool."""

import os
import tempfile
import unittest
from unittest.mock import patch

from agentuniverse.agent.action.tool.common_tool import icalendar_tool as calendar_module
from agentuniverse.agent.action.tool.common_tool.icalendar_tool import ICalendarTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(calendar_module.__file__), "icalendar_tool.yaml")


class CalendarTestCase(unittest.TestCase):
    def setUp(self):
        self.context = tempfile.TemporaryDirectory()
        self.base_dir = self.context.name
        self.tool = ICalendarTool(base_dir=self.base_dir)

    def tearDown(self):
        self.context.cleanup()

    @staticmethod
    def event(uid="event-1@example.com", summary="Planning"):
        return {
            "uid": uid,
            "summary": summary,
            "start": "2026-07-20T10:00:00+08:00",
            "end": "2026-07-20T11:00:00+08:00",
        }


class TestICalendarValidation(CalendarTestCase):
    def test_invalid_mode_and_extension(self):
        result = self.tool.execute(mode="remove", file_path="calendar.txt")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("mode must be", result["error"])

    def test_rejects_path_escape(self):
        result = self.tool.execute(mode="info", file_path="../calendar.ics")
        self.assertIn("escapes the allowed directory", result["error"])

    def test_rejects_invalid_configuration(self):
        self.tool.max_events = True
        result = self.tool.execute(mode="info", file_path="calendar.ics")
        self.assertIn("max_events must be a positive integer", result["error"])

    def test_create_requires_events(self):
        result = self.tool.execute(mode="create", file_path="calendar.ics", events=[])
        self.assertIn("events must be a non-empty list", result["error"])

    def test_rejects_unknown_event_field(self):
        event = self.event()
        event["script"] = "unsafe"
        result = self.tool.execute(mode="create", file_path="calendar.ics", events=[event])
        self.assertIn("unknown fields: script", result["error"])

    def test_rejects_invalid_range(self):
        event = self.event()
        event["end"] = event["start"]
        result = self.tool.execute(mode="create", file_path="calendar.ics", events=[event])
        self.assertIn("end must be after start", result["error"])

    def test_rejects_mixed_date_and_datetime_range(self):
        event = self.event()
        event["start"] = "2026-07-20"
        result = self.tool.execute(mode="create", file_path="calendar.ics", events=[event])
        self.assertIn("both be dates or both be date-times", result["error"])

    def test_rejects_duplicate_uids(self):
        result = self.tool.execute(mode="create", file_path="calendar.ics", events=[self.event(), self.event()])
        self.assertIn("duplicate event UID", result["error"])

    def test_rejects_unknown_timezone(self):
        event = self.event()
        event["start"] = "2026-07-20T10:00:00"
        event["end"] = "2026-07-20T11:00:00"
        result = self.tool.execute(
            mode="create",
            file_path="calendar.ics",
            events=[event],
            default_timezone="Mars/Olympus",
        )
        self.assertIn("unknown default_timezone", result["error"])

    def test_attendee_and_alarm_limits(self):
        self.tool.max_attendees_per_event = 1
        event = self.event()
        event["attendees"] = ["mailto:a@example.com", "mailto:b@example.com"]
        result = self.tool.execute(mode="create", file_path="calendar.ics", events=[event])
        self.assertIn("limited to 1", result["error"])

    def test_missing_dependency_has_install_hint(self):
        with patch.object(ICalendarTool, "_dependency", side_effect=ImportError("missing")):
            result = self.tool.execute(mode="create", file_path="calendar.ics", events=[self.event()])
        self.assertEqual(result["error_type"], "dependency_error")
        self.assertIn("pip install icalendar", result["error"])

    def test_write_limit_preserves_existing_file(self):
        path = os.path.join(self.base_dir, "calendar.ics")
        with open(path, "wb") as stream:
            stream.write(b"existing")
        self.tool.max_write_bytes = 4
        with self.assertRaisesRegex(ValueError, "max_write_bytes"):
            self.tool._atomic_write(b"oversized", path)
        with open(path, "rb") as stream:
            self.assertEqual(stream.read(), b"existing")


class TestICalendarOperations(CalendarTestCase):
    def test_create_read_and_info_round_trip(self):
        event = self.event(summary="全球发布 🚀")
        event.update(
            {
                "description": "Discuss résumé and 日本語",
                "location": "Shanghai",
                "status": "confirmed",
                "organizer": "mailto:owner@example.com",
                "attendees": ["mailto:team@example.com"],
                "categories": ["Release", "Planning"],
                "alarms": [{"minutes_before": 15, "description": "Join now"}],
            }
        )
        created = self.tool.execute(
            mode="create",
            file_path="nested/calendar.ics",
            events=[event],
            calendar_name="Engineering",
            calendar_description="Team schedule",
        )
        self.assertEqual(created["status"], "success")
        read = self.tool.execute(mode="read", file_path="nested/calendar.ics")
        self.assertEqual(read["events"][0]["summary"], "全球发布 🚀")
        self.assertEqual(read["events"][0]["status"], "CONFIRMED")
        self.assertEqual(read["events"][0]["attendees"], ["mailto:team@example.com"])
        self.assertEqual(read["events"][0]["alarms"][0]["description"], "Join now")
        info = self.tool.execute(mode="info", file_path="nested/calendar.ics")
        self.assertEqual(info["calendar_name"], "Engineering")
        self.assertEqual(info["event_count"], 1)
        self.assertTrue(info["range_start"].startswith("2026-07-20T10:00:00"))

    def test_all_day_event_round_trip(self):
        event = self.event()
        event["start"], event["end"] = "2026-07-20", "2026-07-22"
        self.tool.execute(mode="create", file_path="calendar.ics", events=[event])
        read = self.tool.execute(mode="read", file_path="calendar.ics")
        self.assertEqual(read["events"][0]["start"], "2026-07-20")
        self.assertEqual(read["events"][0]["end"], "2026-07-22")

    def test_default_timezone_applied(self):
        event = self.event()
        event["start"], event["end"] = "2026-07-20T10:00:00", "2026-07-20T11:00:00"
        self.tool.execute(
            mode="create",
            file_path="calendar.ics",
            events=[event],
            default_timezone="Asia/Shanghai",
        )
        read = self.tool.execute(mode="read", file_path="calendar.ics")
        self.assertEqual(read["events"][0]["start"], "2026-07-20T10:00:00+08:00")

    def test_merge_calendars(self):
        self.tool.execute(mode="create", file_path="one.ics", events=[self.event("one")])
        self.tool.execute(mode="create", file_path="two.ics", events=[self.event("two")])
        merged = self.tool.execute(
            mode="merge",
            file_path="merged.ics",
            input_paths=["one.ics", "two.ics"],
            calendar_name="Merged",
        )
        self.assertEqual(merged["event_count"], 2)
        read = self.tool.execute(mode="read", file_path="merged.ics")
        self.assertEqual([event["uid"] for event in read["events"]], ["one", "two"])

    def test_merge_rejects_duplicate_uid(self):
        self.tool.execute(mode="create", file_path="one.ics", events=[self.event()])
        self.tool.execute(mode="create", file_path="two.ics", events=[self.event()])
        result = self.tool.execute(mode="merge", file_path="merged.ics", input_paths=["one.ics", "two.ics"])
        self.assertIn("duplicate event UID", result["error"])
        self.assertFalse(os.path.exists(os.path.join(self.base_dir, "merged.ics")))

    def test_create_refuses_and_allows_explicit_overwrite(self):
        self.tool.execute(mode="create", file_path="calendar.ics", events=[self.event()])
        refused = self.tool.execute(mode="create", file_path="calendar.ics", events=[self.event("new")])
        self.assertIn("overwrite=true", refused["error"])
        replaced = self.tool.execute(
            mode="create", file_path="calendar.ics", events=[self.event("new")], overwrite=True
        )
        self.assertTrue(replaced["overwritten"])
        read = self.tool.execute(mode="read", file_path="calendar.ics")
        self.assertEqual(read["events"][0]["uid"], "new")

    def test_read_truncates_bounded_text(self):
        event = self.event()
        event["description"] = "x" * 40
        self.tool.execute(mode="create", file_path="calendar.ics", events=[event])
        self.tool.max_text_chars = 10
        read = self.tool.execute(mode="read", file_path="calendar.ics")
        self.assertTrue(read["truncated"])
        self.assertLessEqual(len(read["events"][0]["summary"]) + len(read["events"][0]["description"]), 10)


class TestICalendarRegistration(unittest.TestCase):
    def setUp(self):
        self.configer = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_yaml_component_schema(self):
        component = ComponentConfiger().load_by_configer(self.configer)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "ICalendarTool")

    def test_tool_manager_registration(self):
        configer = ToolConfiger().load_by_configer(self.configer)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, ICalendarTool)
        self.assertEqual(tool.input_keys, ["mode", "file_path"])
        self.assertEqual(tool.args_model_schema["properties"]["mode"]["enum"], ["create", "read", "info", "merge"])


if __name__ == "__main__":
    unittest.main()
