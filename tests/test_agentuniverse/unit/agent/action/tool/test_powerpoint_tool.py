#!/usr/bin/env python3

"""Tests for the built-in PowerPointTool."""

import importlib.util
import os
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from agentuniverse.agent.action.tool.common_tool import powerpoint_tool as ppt_module
from agentuniverse.agent.action.tool.common_tool.powerpoint_tool import PowerPointTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.base.config.component_configer.component_configer import (
    ComponentConfiger,
)
from agentuniverse.base.config.component_configer.configers.tool_configer import (
    ToolConfiger,
)
from agentuniverse.base.config.configer import Configer

PPTX_AVAILABLE = importlib.util.find_spec("pptx") is not None
YAML_PATH = os.path.join(os.path.dirname(ppt_module.__file__), "powerpoint_tool.yaml")


class TestPowerPointValidation(unittest.TestCase):
    """Input, configuration, path, and atomic-write boundaries."""

    def setUp(self) -> None:
        self.temp_dir_context = tempfile.TemporaryDirectory()
        self.base_dir = self.temp_dir_context.name
        self.tool = PowerPointTool(base_dir=self.base_dir)

    def tearDown(self) -> None:
        self.temp_dir_context.cleanup()

    def test_invalid_mode_is_structured_error(self) -> None:
        result = self.tool.execute(mode="delete", file_path="deck.pptx")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("invalid mode", result["error"])

    def test_rejects_non_pptx_extension(self) -> None:
        result = self.tool.execute(mode="info", file_path="deck.ppt")
        self.assertIn(".pptx extension", result["error"])

    def test_rejects_parent_path_escape(self) -> None:
        result = self.tool.execute(mode="info", file_path="../deck.pptx")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("escapes the allowed directory", result["error"])

    def test_rejects_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            outside_file = os.path.join(outside, "outside.pptx")
            with open(outside_file, "wb") as output:
                output.write(b"not a presentation")
            os.symlink(outside, os.path.join(self.base_dir, "linked"))
            result = self.tool.execute(
                mode="info",
                file_path="linked/outside.pptx",
            )
        self.assertIn("escapes the allowed directory", result["error"])

    def test_rejects_invalid_config_limit(self) -> None:
        self.tool.max_slides = 0
        result = self.tool.execute(mode="info", file_path="deck.pptx")
        self.assertIn("max_slides must be a positive integer", result["error"])

    def test_rejects_boolean_config_limit(self) -> None:
        self.tool.max_text_chars = True
        result = self.tool.execute(mode="info", file_path="deck.pptx")
        self.assertIn("max_text_chars must be a positive integer", result["error"])

    def test_rejects_invalid_pptx_archive(self) -> None:
        with open(os.path.join(self.base_dir, "invalid.pptx"), "wb") as output:
            output.write(b"not-a-zip")
        result = self.tool.execute(mode="info", file_path="invalid.pptx")
        self.assertIn("not a valid PPTX ZIP archive", result["error"])

    def test_rejects_archive_expansion_over_limit(self) -> None:
        archive_path = os.path.join(self.base_dir, "oversized.pptx")
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("ppt/slides/slide1.xml", "x" * 100)
        self.tool.max_uncompressed_bytes = 32
        result = self.tool.execute(mode="info", file_path="oversized.pptx")
        self.assertIn("max_uncompressed_bytes", result["error"])

    def test_rejects_archive_entry_count_over_limit(self) -> None:
        archive_path = os.path.join(self.base_dir, "many-entries.pptx")
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("one", "1")
            archive.writestr("two", "2")
        self.tool.max_archive_entries = 1
        result = self.tool.execute(mode="info", file_path="many-entries.pptx")
        self.assertIn("max_archive_entries", result["error"])

    def test_rejects_file_size_over_read_limit_before_parsing(self) -> None:
        presentation_path = os.path.join(self.base_dir, "oversized.pptx")
        with open(presentation_path, "wb") as output:
            output.write(b"PK" + b"x" * 30)
        self.tool.max_read_bytes = 16

        result = self.tool.execute(mode="read", file_path="oversized.pptx")

        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("max_read_bytes", result["error"])

    def test_rejects_invalid_template_archive(self) -> None:
        with open(os.path.join(self.base_dir, "template.pptx"), "wb") as output:
            output.write(b"not-a-template")

        result = self.tool.execute(
            mode="create",
            file_path="deck.pptx",
            template_path="template.pptx",
            slides=[{"title": "Generated"}],
        )

        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("template_path is not a valid PPTX ZIP archive", result["error"])
        self.assertFalse(os.path.exists(os.path.join(self.base_dir, "deck.pptx")))

    def test_create_requires_non_empty_slides(self) -> None:
        result = self.tool.execute(
            mode="create",
            file_path="deck.pptx",
            slides=[],
        )
        self.assertIn("slides must be a non-empty list", result["error"])

    def test_rejects_unknown_slide_field(self) -> None:
        result = self.tool.execute(
            mode="create",
            file_path="deck.pptx",
            slides=[{"title": "Hello", "script": "do something"}],
        )
        self.assertIn("unknown fields: script", result["error"])

    def test_rejects_invalid_bullet_level(self) -> None:
        result = self.tool.execute(
            mode="create",
            file_path="deck.pptx",
            slides=[
                {
                    "title": "Hello",
                    "bullets": [{"text": "Too deep", "level": 9}],
                }
            ],
        )
        self.assertIn("integer from 0 to 8", result["error"])

    def test_rejects_table_column_overflow(self) -> None:
        self.tool.max_table_columns = 2
        result = self.tool.execute(
            mode="create",
            file_path="deck.pptx",
            slides=[{"title": "Data", "table": [[1, 2, 3]]}],
        )
        self.assertIn("max_table_columns", result["error"])

    def test_rejects_text_budget_overflow(self) -> None:
        self.tool.max_text_chars = 5
        result = self.tool.execute(
            mode="create",
            file_path="deck.pptx",
            slides=[{"title": "sixsix"}],
        )
        self.assertIn("exceeding max_text_chars", result["error"])

    def test_missing_dependency_has_install_hint(self) -> None:
        with patch.object(
            self.tool,
            "_load_pptx",
            side_effect=ImportError("missing"),
        ):
            result = self.tool.execute(
                mode="create",
                file_path="deck.pptx",
                slides=[{"title": "Hello"}],
            )
        self.assertEqual(result["error_type"], "dependency_error")
        self.assertIn("pip install python-pptx", result["error"])

    def test_atomic_save_preserves_destination_when_size_limit_fails(self) -> None:
        destination = os.path.join(self.base_dir, "deck.pptx")
        original = b"existing-presentation"
        with open(destination, "wb") as output:
            output.write(original)

        class OversizedPresentation:
            @staticmethod
            def save(path):
                with open(path, "wb") as output:
                    output.write(b"x" * 32)

        self.tool.max_write_bytes = 16
        with self.assertRaisesRegex(ValueError, "max_write_bytes"):
            self.tool._atomic_save(OversizedPresentation(), destination)
        with open(destination, "rb") as existing:
            self.assertEqual(existing.read(), original)
        leftovers = [name for name in os.listdir(self.base_dir) if name.startswith(".powerpoint-")]
        self.assertEqual(leftovers, [])

    def test_atomic_save_preserves_destination_when_expansion_limit_fails(self) -> None:
        destination = os.path.join(self.base_dir, "deck.pptx")
        original = b"existing-presentation"
        with open(destination, "wb") as output:
            output.write(original)

        class ExpandingPresentation:
            @staticmethod
            def save(path):
                with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
                    archive.writestr("ppt/slides/slide1.xml", "x" * 64)

        self.tool.max_uncompressed_bytes = 32
        with self.assertRaisesRegex(ValueError, "max_uncompressed_bytes"):
            self.tool._atomic_save(ExpandingPresentation(), destination)
        with open(destination, "rb") as existing:
            self.assertEqual(existing.read(), original)
        leftovers = [name for name in os.listdir(self.base_dir) if name.startswith(".powerpoint-")]
        self.assertEqual(leftovers, [])


@unittest.skipUnless(PPTX_AVAILABLE, "python-pptx is required")
class TestPowerPointOperations(unittest.TestCase):
    """Real, deterministic PPTX round trips without network access."""

    def setUp(self) -> None:
        self.temp_dir_context = tempfile.TemporaryDirectory()
        self.base_dir = self.temp_dir_context.name
        self.tool = PowerPointTool(base_dir=self.base_dir)

    def tearDown(self) -> None:
        self.temp_dir_context.cleanup()

    def _create_deck(self, file_path: str = "deck.pptx"):
        return self.tool.execute(
            mode="create",
            file_path=file_path,
            slides=[
                {
                    "title": "Quarterly Review",
                    "subtitle": "Q2 2026",
                    "notes": "Open with the headline.",
                },
                {
                    "title": "Highlights",
                    "bullets": [
                        "Revenue grew 20%",
                        {"text": "APAC led growth", "level": 1},
                    ],
                    "table": [
                        ["Metric", "Value"],
                        ["Revenue", 123],
                    ],
                    "notes": "Explain the regional mix.",
                },
            ],
            metadata={"title": "Quarterly Review", "author": "agentUniverse"},
        )

    def test_create_read_and_info_round_trip(self) -> None:
        created = self._create_deck()
        self.assertEqual(created["status"], "success")
        self.assertEqual(created["slide_count"], 2)
        self.assertTrue(os.path.isfile(created["file_path"]))

        read = self.tool.execute(mode="read", file_path="deck.pptx")
        self.assertEqual(read["status"], "success")
        self.assertFalse(read["truncated"])
        self.assertEqual(read["slides"][0]["title"], "Quarterly Review")
        self.assertIn("Q2 2026", read["slides"][0]["texts"])
        self.assertEqual(read["slides"][0]["notes"], "Open with the headline.")
        self.assertIn("Revenue grew 20%", read["slides"][1]["texts"][0])
        self.assertEqual(read["slides"][1]["tables"][0][1], ["Revenue", "123"])

        info = self.tool.execute(mode="info", file_path="deck.pptx")
        self.assertEqual(info["slide_count"], 2)
        self.assertEqual(info["metadata"]["title"], "Quarterly Review")
        self.assertEqual(info["metadata"]["author"], "agentUniverse")
        self.assertEqual(info["slides"][1]["table_count"], 1)
        self.assertTrue(info["slides"][0]["has_notes"])

    def test_append_preserves_existing_slides(self) -> None:
        self._create_deck()
        appended = self.tool.execute(
            mode="append",
            file_path="deck.pptx",
            slides=[{"title": "Next Steps", "bullets": ["Ship the release"]}],
        )
        self.assertEqual(appended["status"], "success")
        self.assertEqual(appended["slides_added"], 1)
        self.assertEqual(appended["slide_count"], 3)
        read = self.tool.execute(mode="read", file_path="deck.pptx")
        self.assertEqual(read["slides"][0]["title"], "Quarterly Review")
        self.assertEqual(read["slides"][2]["title"], "Next Steps")

    def test_create_refuses_overwrite_and_preserves_file(self) -> None:
        self._create_deck()
        deck_path = os.path.join(self.base_dir, "deck.pptx")
        with open(deck_path, "rb") as original_file:
            original = original_file.read()
        result = self.tool.execute(
            mode="create",
            file_path="deck.pptx",
            slides=[{"title": "Replacement"}],
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("set overwrite=true", result["error"])
        with open(deck_path, "rb") as unchanged_file:
            self.assertEqual(unchanged_file.read(), original)

    def test_create_can_overwrite_explicitly(self) -> None:
        self._create_deck()
        result = self.tool.execute(
            mode="create",
            file_path="deck.pptx",
            slides=[{"title": "Replacement"}],
            overwrite=True,
        )
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["overwritten"])
        self.assertEqual(result["slide_count"], 1)

    def test_template_preserves_template_slides(self) -> None:
        self.tool.execute(
            mode="create",
            file_path="template.pptx",
            slides=[{"title": "Template Cover"}],
        )
        created = self.tool.execute(
            mode="create",
            file_path="from-template.pptx",
            template_path="template.pptx",
            slides=[{"title": "Generated Slide"}],
        )
        self.assertEqual(created["status"], "success")
        self.assertEqual(created["slide_count"], 2)
        read = self.tool.execute(mode="read", file_path="from-template.pptx")
        self.assertEqual(
            [slide["title"] for slide in read["slides"]],
            ["Template Cover", "Generated Slide"],
        )

    def test_read_truncates_to_context_budget(self) -> None:
        self.tool.execute(
            mode="create",
            file_path="deck.pptx",
            slides=[{"title": "A long title", "bullets": ["long body text"]}],
        )
        self.tool.max_text_chars = 8
        read = self.tool.execute(mode="read", file_path="deck.pptx")
        self.assertEqual(read["status"], "success")
        self.assertTrue(read["truncated"])
        emitted = sum(
            len(slide["title"]) + sum(len(text) for text in slide["texts"]) + len(slide["notes"])
            for slide in read["slides"]
        )
        self.assertLessEqual(emitted, 8)

    def test_append_rejects_result_over_slide_limit(self) -> None:
        self._create_deck()
        self.tool.max_slides = 2
        result = self.tool.execute(
            mode="append",
            file_path="deck.pptx",
            slides=[{"title": "One too many"}],
        )
        self.assertIn("exceeding max_slides", result["error"])

    def test_unicode_ragged_table_and_explicit_layout_round_trip(self) -> None:
        created = self.tool.execute(
            mode="create",
            file_path="unicode.pptx",
            slides=[
                {
                    "layout": "title_only",
                    "title": "全球发布 🚀",
                    "bullets": ["Español", {"text": "日本語", "level": 1}],
                    "table": [["地区", "ARR", "Owner"], ["亚太", 42]],
                    "notes": "演讲人备注 ✓",
                }
            ],
        )

        self.assertEqual(created["status"], "success")
        read = self.tool.execute(mode="read", file_path="unicode.pptx")
        self.assertEqual(read["slides"][0]["title"], "全球发布 🚀")
        self.assertIn("Español", read["slides"][0]["texts"][0])
        self.assertIn("日本語", read["slides"][0]["texts"][0])
        self.assertEqual(read["slides"][0]["tables"][0][1], ["亚太", "42", ""])
        self.assertEqual(read["slides"][0]["notes"], "演讲人备注 ✓")

    def test_blank_layout_fallback_title_round_trip(self) -> None:
        created = self.tool.execute(
            mode="create",
            file_path="blank-layout.pptx",
            slides=[{"layout": "blank", "title": "Semantic fallback title"}],
        )

        self.assertEqual(created["status"], "success")
        read = self.tool.execute(mode="read", file_path="blank-layout.pptx")
        info = self.tool.execute(mode="info", file_path="blank-layout.pptx")
        self.assertEqual(read["slides"][0]["title"], "Semantic fallback title")
        self.assertNotIn("Semantic fallback title", read["slides"][0]["texts"])
        self.assertEqual(info["slides"][0]["title"], "Semantic fallback title")

    def test_create_uses_write_limit_not_read_limit(self) -> None:
        self.tool.max_read_bytes = 1
        self.tool.max_write_bytes = 2 * 1024 * 1024

        created = self.tool.execute(
            mode="create",
            file_path="deck.pptx",
            slides=[{"title": "Generated independently of the read limit"}],
        )

        self.assertEqual(created["status"], "success")
        self.assertGreater(created["file_size"], self.tool.max_read_bytes)

    def test_append_write_failure_preserves_original_presentation(self) -> None:
        self._create_deck()
        deck_path = os.path.join(self.base_dir, "deck.pptx")
        with open(deck_path, "rb") as original_file:
            original = original_file.read()
        self.tool.max_write_bytes = 1

        result = self.tool.execute(
            mode="append",
            file_path="deck.pptx",
            slides=[{"title": "Must not be partially written"}],
        )

        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("max_write_bytes", result["error"])
        with open(deck_path, "rb") as unchanged_file:
            self.assertEqual(unchanged_file.read(), original)

    def test_template_slide_count_is_checked_before_destination_write(self) -> None:
        self.tool.execute(
            mode="create",
            file_path="template.pptx",
            slides=[{"title": "Template one"}, {"title": "Template two"}],
        )
        self.tool.max_slides = 2

        result = self.tool.execute(
            mode="create",
            file_path="from-template.pptx",
            template_path="template.pptx",
            slides=[{"title": "Would exceed the limit"}],
        )

        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("template slides plus requested slides", result["error"])
        self.assertFalse(os.path.exists(os.path.join(self.base_dir, "from-template.pptx")))

    # -- read-side structural bounds (regression for crafted PPTX expansion) --

    def test_read_caps_slide_count(self) -> None:
        # More slides than max_slides; read still succeeds but the archive
        # guard rejects the file before parsing.
        many_slides = [{"title": f"slide {i}"} for i in range(5)]
        self.tool.execute(mode="create", file_path="many.pptx", slides=many_slides)
        self.tool.max_slides = 2
        result = self.tool.execute(mode="read", file_path="many.pptx")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("exceeding max_slides", result["error"])

    def test_read_caps_shapes_per_slide(self) -> None:
        # A slide with a body plus a table carries multiple shapes; the read
        # must stop at max_shapes_per_slide instead of walking every shape and
        # expanding every table cell into the result.
        self.tool.execute(
            mode="create",
            file_path="shapes.pptx",
            slides=[{"title": "t", "bullets": ["b1", "b2"], "table": [["a", "b"], ["c", "d"]]}],
        )
        # Lower the cap so the table shape is never reached; the read reports
        # truncated and emits no table rows.
        self.tool.max_shapes_per_slide = 1
        result = self.tool.execute(mode="read", file_path="shapes.pptx")
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["truncated"])
        self.assertEqual(result["slides"][0]["tables"], [])

    def test_read_caps_table_rows(self) -> None:
        # A table with more rows than max_table_rows; read must stop early.
        big_rows = [[f"r{i}c0", f"r{i}c1"] for i in range(40)]
        self.tool.execute(
            mode="create",
            file_path="rows.pptx",
            slides=[{"title": "t", "table": big_rows}],
        )
        self.tool.max_table_rows = 5
        result = self.tool.execute(mode="read", file_path="rows.pptx")
        self.assertEqual(result["status"], "success")
        for table in result["slides"][0]["tables"]:
            self.assertLessEqual(len(table), self.tool.max_table_rows)
        self.assertTrue(result["truncated"])

    def test_read_caps_table_columns(self) -> None:
        # A wide table; read must stop at max_table_columns per row.
        wide_row = [str(i) for i in range(15)]
        self.tool.execute(
            mode="create",
            file_path="wide.pptx",
            slides=[{"title": "t", "table": [wide_row, wide_row]}],
        )
        self.tool.max_table_columns = 4
        result = self.tool.execute(mode="read", file_path="wide.pptx")
        self.assertEqual(result["status"], "success")
        for table in result["slides"][0]["tables"]:
            for row in table:
                self.assertLessEqual(len(row), self.tool.max_table_columns)
        self.assertTrue(result["truncated"])

    def test_read_stops_when_text_budget_exhausted(self) -> None:
        # Once max_text_chars is consumed, the read must stop traversing rather
        # than continuing to walk every remaining slide/shape and padding the
        # result with empty strings.
        slides = [{"title": f"title-{i}", "bullets": [f"body text line {i}"]} for i in range(15)]
        self.tool.execute(mode="create", file_path="mixed.pptx", slides=slides)
        self.tool.max_text_chars = 30
        result = self.tool.execute(mode="read", file_path="mixed.pptx")
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["truncated"])
        # No empty-string padding from continued traversal after budget hit.
        emitted = sum(
            len(slide["title"]) + sum(len(text) for text in slide["texts"]) + len(slide["notes"])
            for slide in result["slides"]
        )
        # Allow a small overshoot for the truncation ellipsis on the last field.
        self.assertLessEqual(emitted, self.tool.max_text_chars + len(result["slides"]))


class TestPowerPointRegistration(unittest.TestCase):
    """Load the shipped YAML through the real component pipeline."""

    def setUp(self) -> None:
        self.configer = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous_app_configer = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous_app_configer = None

    def tearDown(self) -> None:
        ApplicationConfigManager().app_configer = self.previous_app_configer

    def test_yaml_resolves_to_tool_component(self) -> None:
        component = ComponentConfiger().load_by_configer(self.configer)
        self.assertEqual(
            component.get_component_config_type(),
            ComponentEnum.TOOL.value,
        )
        self.assertEqual(
            component.metadata_module,
            "agentuniverse.agent.action.tool.common_tool.powerpoint_tool",
        )
        self.assertEqual(component.metadata_class, "PowerPointTool")

    def test_tool_manager_resolves_configured_tool(self) -> None:
        tool_configer = ToolConfiger().load_by_configer(self.configer)
        app_configer = AppConfiger()
        app_configer.tool_configer_map = {tool_configer.name: tool_configer}
        ApplicationConfigManager().app_configer = app_configer

        tool = ToolManager().get_instance_obj(tool_configer.name)

        self.assertIsInstance(tool, PowerPointTool)
        self.assertEqual(tool.name, "powerpoint_tool")
        self.assertEqual(tool.input_keys, ["mode", "file_path"])
        self.assertEqual(tool.max_slides, 100)
        self.assertEqual(tool.max_uncompressed_bytes, 104_857_600)
        self.assertEqual(
            tool.args_model_schema["properties"]["mode"]["enum"],
            ["create", "append", "read", "info"],
        )


if __name__ == "__main__":
    unittest.main()
