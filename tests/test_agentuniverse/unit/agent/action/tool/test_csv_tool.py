"""Tests for the bounded CSVTool."""

# The optional-dependency shim must run before agentUniverse is imported.
# ruff: noqa: E402

import os
import tempfile
import unittest

from tests.test_agentuniverse.unit.agent.action.tool.csv_test_support import (
    install_optional_dependency_stubs,
)

install_optional_dependency_stubs()

from agentuniverse.agent.action.tool.common_tool import csv_tool as csv_module
from agentuniverse.agent.action.tool.common_tool.csv_tool import CSVTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(csv_module.__file__), "csv_tool.yaml")


class CSVToolTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.tool = CSVTool(base_dir=self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def write_file(self, name, data, encoding="utf-8"):
        path = os.path.join(self.directory.name, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding=encoding, newline="") as output:
            output.write(data)
        return path

    def read_bytes(self, name):
        with open(os.path.join(self.directory.name, name), "rb") as stream:
            return stream.read()

    def read_text(self, name, encoding="utf-8"):
        with open(os.path.join(self.directory.name, name), encoding=encoding, newline="") as stream:
            return stream.read()

    def test_quoted_fields_and_embedded_newlines_round_trip(self):
        rows = [
            ["name", "note"],
            ["Ada", "line one\nline two"],
            ["Grace", 'comma, and "quoted" text'],
        ]
        written = self.tool.execute(mode="write", file_path="data.csv", rows=rows)
        self.assertEqual(written["status"], "success")
        self.assertEqual(written["rows_written"], 3)
        self.assertEqual(written["row_count"], 2)
        self.assertEqual(written["column_count"], 2)

        read = self.tool.execute(mode="read", file_path="data.csv")
        self.assertEqual(read["status"], "success")
        self.assertEqual(read["header"], rows[0])
        self.assertEqual(read["rows"], rows[1:])
        self.assertEqual(read["row_count"], 2)
        self.assertEqual(read["column_count"], 2)
        self.assertEqual(read["delimiter"], ",")
        self.assertEqual(read["encoding"], "utf-8")
        self.assertIn('"line one', self.read_text("data.csv"))

    def test_append_adds_rows_and_keeps_existing_content(self):
        self.tool.execute(mode="write", file_path="data.csv", rows=[["name", "score"], ["Ada", 1]])
        appended = self.tool.execute(mode="append", file_path="data.csv", rows=[["Grace", 2]])
        self.assertEqual(appended["status"], "success")
        self.assertEqual(appended["rows_appended"], 1)
        self.assertEqual(appended["row_count"], 2)
        read = self.tool.execute(mode="read", file_path="data.csv")
        self.assertEqual(read["header"], ["name", "score"])
        self.assertEqual(read["rows"], [["Ada", "1"], ["Grace", "2"]])

    def test_append_terminates_a_missing_final_newline(self):
        self.write_file("data.csv", "name,score\r\nAda,1")
        appended = self.tool.execute(mode="append", file_path="data.csv", rows=[["Grace", "2"]])
        self.assertEqual(appended["status"], "success")
        read = self.tool.execute(mode="read", file_path="data.csv")
        self.assertEqual(read["rows"], [["Ada", "1"], ["Grace", "2"]])

    def test_append_requires_an_existing_file(self):
        result = self.tool.execute(mode="append", file_path="missing.csv", rows=[["a"]])
        self.assertIn("does not exist", result["error"])

    def test_append_to_empty_file_treats_first_row_as_header(self):
        self.write_file("empty.csv", "")
        appended = self.tool.execute(mode="append", file_path="empty.csv", rows=[["a", "b"], ["1", "2"]])
        self.assertEqual(appended["status"], "success")
        self.assertEqual(appended["row_count"], 1)
        read = self.tool.execute(mode="read", file_path="empty.csv")
        self.assertEqual(read["header"], ["a", "b"])
        self.assertEqual(read["rows"], [["1", "2"]])

    def test_append_rejects_mixed_width_existing_file(self):
        path = self.write_file("data.csv", "a,b\n1,2,3\n")
        result = self.tool.execute(mode="append", file_path="data.csv", rows=[["4", "5"]])
        self.assertIn("same number of columns", result["error"])
        with open(path, encoding="utf-8", newline="") as stream:
            self.assertEqual(stream.read(), "a,b\n1,2,3\n")

    def test_append_rejects_rows_with_wrong_width(self):
        path = self.write_file("data.csv", "a,b\n1,2\n")
        result = self.tool.execute(mode="append", file_path="data.csv", rows=[["3", "4", "5"]])
        self.assertIn("match the existing column count", result["error"])
        with open(path, encoding="utf-8", newline="") as stream:
            self.assertEqual(stream.read(), "a,b\n1,2\n")

    def test_append_rejects_mismatched_encoding_without_touching_file(self):
        self.tool.execute(mode="write", file_path="data.csv", rows=[["a", "b"], ["1", "2"]], encoding="utf-16")
        original = self.read_bytes("data.csv")
        result = self.tool.execute(mode="append", file_path="data.csv", rows=[["3", "4"]], encoding="utf-8")
        self.assertEqual(result["status"], "error")
        self.assertEqual(self.read_bytes("data.csv"), original)

    def test_append_rewrites_existing_content_in_requested_encoding(self):
        self.tool.execute(mode="write", file_path="data.csv", rows=[["a", "b"], ["1", "2"]], encoding="utf-16")
        appended = self.tool.execute(mode="append", file_path="data.csv", rows=[["3", "4"]], encoding="utf-16")
        self.assertEqual(appended["status"], "success")
        self.assertEqual(self.read_bytes("data.csv").count(b"\xff\xfe"), 1)
        read = self.tool.execute(mode="read", file_path="data.csv", encoding="utf-16")
        self.assertEqual(read["rows"], [["1", "2"], ["3", "4"]])

    def test_append_enforces_read_byte_limit_on_existing_file(self):
        self.write_file("data.csv", "a,b\n1,2\n")
        self.tool.max_read_bytes = 3
        result = self.tool.execute(mode="append", file_path="data.csv", rows=[["3", "4"]])
        self.assertIn("max_read_bytes", result["error"])

    def test_info_reports_size_and_shape_without_rows(self):
        self.tool.execute(
            mode="write",
            file_path="data.csv",
            rows=[["name", "score"], ["Ada", 1], ["Grace", 2]],
        )
        info = self.tool.execute(mode="info", file_path="data.csv")
        self.assertEqual(info["status"], "success")
        self.assertEqual(info["mode"], "info")
        self.assertEqual(info["file_size"], os.path.getsize(os.path.join(self.directory.name, "data.csv")))
        self.assertEqual(info["row_count"], 2)
        self.assertEqual(info["column_count"], 2)
        self.assertEqual(info["delimiter"], ",")
        self.assertEqual(info["encoding"], "utf-8")
        self.assertNotIn("rows", info)

    def test_encoding_round_trip(self):
        rows = [["city", "name"], ["M\u00fcnchen", "Zo\u00eb"]]
        written = self.tool.execute(mode="write", file_path="data.csv", rows=rows, encoding="utf-16")
        self.assertEqual(written["status"], "success")
        self.assertTrue(self.read_bytes("data.csv").startswith((b"\xff\xfe", b"\xfe\xff")))
        read = self.tool.execute(mode="read", file_path="data.csv", encoding="utf-16")
        self.assertEqual(read["header"], rows[0])
        self.assertEqual(read["rows"], rows[1:])
        info = self.tool.execute(mode="info", file_path="data.csv", encoding="utf-16")
        self.assertEqual(info["encoding"], "utf-16")

    def test_invalid_encoding_is_rejected(self):
        self.write_file("data.csv", "a\n")
        result = self.tool.execute(mode="info", file_path="data.csv", encoding="not-a-real-codec")
        self.assertIn("encoding", result["error"])

    def test_none_cells_are_written_as_empty_fields(self):
        written = self.tool.execute(mode="write", file_path="data.csv", rows=[["a", "b"], ["1", None]])
        self.assertEqual(written["status"], "success")
        read = self.tool.execute(mode="read", file_path="data.csv")
        self.assertEqual(read["rows"], [["1", ""]])

    def test_write_rejects_non_list_rows(self):
        result = self.tool.execute(mode="write", file_path="data.csv", rows=(("a",), ("b",)))
        self.assertIn("non-empty list", result["error"])

    def test_custom_delimiter_round_trip(self):
        rows = [["name", "note"], ["Ada", "one; two"]]
        self.tool.execute(mode="write", file_path="data.csv", rows=rows, delimiter=";")
        read = self.tool.execute(mode="read", file_path="data.csv", delimiter=";")
        self.assertEqual(read["rows"], rows[1:])
        self.assertIn("one; two", self.read_text("data.csv"))

    def test_path_escape_is_rejected(self):
        result = self.tool.execute(mode="write", file_path="../escape.csv", rows=[["a"]])
        self.assertIn("escapes the allowed directory", result["error"])
        result = self.tool.execute(mode="info", file_path="../escape.csv")
        self.assertIn("escapes the allowed directory", result["error"])

    def test_overwrite_is_refused_until_requested(self):
        self.tool.execute(mode="write", file_path="data.csv", rows=[["old"]])
        refused = self.tool.execute(mode="write", file_path="data.csv", rows=[["new"]])
        self.assertIn("overwrite=true", refused["error"])
        self.assertEqual(self.tool.execute(mode="read", file_path="data.csv", has_header=False)["rows"], [["old"]])

        replaced = self.tool.execute(mode="write", file_path="data.csv", rows=[["new"]], overwrite=True)
        self.assertEqual(replaced["status"], "success")
        self.assertEqual(self.tool.execute(mode="read", file_path="data.csv", has_header=False)["rows"], [["new"]])

    def test_invalid_mode_extension_and_delimiter_are_rejected(self):
        self.write_file("data.csv", "a\n")
        self.assertIn("mode must be", self.tool.execute(mode="delete", file_path="data.csv")["error"])
        self.assertIn(".csv", self.tool.execute(mode="info", file_path="data.txt")["error"])
        self.assertIn("one character", self.tool.execute(mode="info", file_path="data.csv", delimiter="||")["error"])
        self.assertIn("newline", self.tool.execute(mode="info", file_path="data.csv", delimiter="\n")["error"])
        self.assertIn("quote", self.tool.execute(mode="info", file_path="data.csv", delimiter='"')["error"])

    def test_row_limit_is_enforced(self):
        self.tool.max_rows = 1
        result = self.tool.execute(mode="write", file_path="data.csv", rows=[["a"], ["b"]])
        self.assertIn("max_rows", result["error"])
        self.write_file("read.csv", "a\n1\n")
        self.tool.max_rows = 1
        self.assertIn("max_rows", self.tool.execute(mode="read", file_path="read.csv")["error"])

    def test_column_and_field_limits_are_enforced(self):
        self.tool.max_columns = 2
        result = self.tool.execute(mode="write", file_path="columns.csv", rows=[["a", "b", "c"]])
        self.assertIn("max_columns", result["error"])

        self.tool.max_columns = 10
        self.tool.max_field_chars = 3
        result = self.tool.execute(mode="write", file_path="fields.csv", rows=[["abcd"]])
        self.assertIn("max_field_chars", result["error"])

    def test_total_character_limit_is_enforced(self):
        self.tool.max_total_chars = 3
        result = self.tool.execute(mode="write", file_path="data.csv", rows=[["ab", "cd"]])
        self.assertIn("max_total_chars", result["error"])

    def test_read_and_write_byte_limits_are_enforced(self):
        self.write_file("large.csv", "name\nvalue-that-is-too-long\n")
        self.tool.max_read_bytes = 4
        self.assertIn("max_read_bytes", self.tool.execute(mode="info", file_path="large.csv")["error"])

        self.tool.max_read_bytes = 1_000
        self.tool.max_write_bytes = 1
        result = self.tool.execute(mode="write", file_path="small.csv", rows=[["value"]])
        self.assertIn("max_write_bytes", result["error"])
        self.assertFalse(os.path.exists(os.path.join(self.directory.name, "small.csv")))

    def test_write_byte_limit_counts_encoded_bytes_not_characters(self):
        # "é" is one character but two UTF-8 bytes, so the character budget
        # passes while the encoded file still exceeds max_write_bytes. This
        # keeps the two budgets independently observable.
        self.tool.max_total_chars = 10
        self.tool.max_write_bytes = 2
        result = self.tool.execute(mode="write", file_path="data.csv", rows=[["é"]])
        self.assertIn("max_write_bytes", result["error"])
        self.assertFalse(os.path.exists(os.path.join(self.directory.name, "data.csv")))

    def test_failed_validation_preserves_an_existing_destination(self):
        path = self.write_file("data.csv", "original\n")
        result = self.tool.execute(
            mode="write",
            file_path="data.csv",
            rows=[["a", "b"], ["c"]],
            overwrite=True,
        )
        self.assertIn("same number of columns", result["error"])
        with open(path, encoding="utf-8", newline="") as stream:
            self.assertEqual(stream.read(), "original\n")

        result = self.tool.execute(
            mode="write",
            file_path="data.csv",
            rows=[["a", {"nested": "object"}]],
            overwrite=True,
        )
        self.assertIn("scalar", result["error"])
        with open(path, encoding="utf-8", newline="") as stream:
            self.assertEqual(stream.read(), "original\n")

    def test_failed_write_size_limit_preserves_an_existing_destination(self):
        path = self.write_file("data.csv", "original\n")
        self.tool.max_write_bytes = 1
        result = self.tool.execute(mode="write", file_path="data.csv", rows=[["new"]], overwrite=True)
        self.assertIn("max_write_bytes", result["error"])
        with open(path, encoding="utf-8", newline="") as stream:
            self.assertEqual(stream.read(), "original\n")

    def test_failed_append_preserves_an_existing_destination(self):
        path = self.write_file("data.csv", "a,b\n1,2\n")
        self.tool.max_rows = 2
        result = self.tool.execute(mode="append", file_path="data.csv", rows=[["3", "4"]])
        self.assertIn("max_rows", result["error"])
        with open(path, encoding="utf-8", newline="") as stream:
            self.assertEqual(stream.read(), "a,b\n1,2\n")

    def test_append_enforces_character_budget_on_existing_content(self):
        path = self.write_file("data.csv", "a,b\n")
        self.tool.max_total_chars = 3
        result = self.tool.execute(mode="append", file_path="data.csv", rows=[["1", "2"]])
        self.assertIn("max_total_chars", result["error"])
        with open(path, encoding="utf-8", newline="") as stream:
            self.assertEqual(stream.read(), "a,b\n")

    def test_append_byte_budget_uses_encoded_size_and_preserves_destination(self):
        path = self.write_file("data.csv", "a\n")
        # The character budget accepts "a" plus "é", but the rewritten file is
        # five UTF-8 bytes, so the encoded byte budget must reject it and leave
        # the original destination untouched.
        self.tool.max_total_chars = 10
        self.tool.max_write_bytes = 4
        result = self.tool.execute(mode="append", file_path="data.csv", rows=[["é"]])
        self.assertIn("max_write_bytes", result["error"])
        with open(path, encoding="utf-8", newline="") as stream:
            self.assertEqual(stream.read(), "a\n")

    def test_has_header_false_returns_all_records_as_rows(self):
        self.write_file("data.csv", "a,b\n1,2\n")
        read = self.tool.execute(mode="read", file_path="data.csv", has_header=False)
        self.assertNotIn("header", read)
        self.assertEqual(read["rows"], [["a", "b"], ["1", "2"]])


class CSVToolRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "CSVTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, CSVTool)
        self.assertEqual(tool.input_keys, ["mode", "file_path"])
        self.assertEqual(tool.max_rows, 100_000)
        self.assertEqual(tool.max_columns, 1_000)
        self.assertEqual(tool.args_model_schema["properties"]["mode"]["enum"], ["read", "write", "append", "info"])
        self.assertFalse(tool.args_model_schema["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
