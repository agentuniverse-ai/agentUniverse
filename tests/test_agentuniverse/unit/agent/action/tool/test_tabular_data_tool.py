#!/usr/bin/env python3
"""Tests for TabularDataTool."""

import json
import os
import tempfile
import unittest

from agentuniverse.agent.action.tool.common_tool import tabular_data_tool as module
from agentuniverse.agent.action.tool.common_tool.tabular_data_tool import TabularDataTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(module.__file__), "tabular_data_tool.yaml")


class TabularTestCase(unittest.TestCase):
    def setUp(self):
        self.context = tempfile.TemporaryDirectory()
        self.base_dir = self.context.name
        self.tool = TabularDataTool(base_dir=self.base_dir)
        self.rows = [
            {"id": 1, "name": "Alice", "amount": 1200.5, "region": "APAC"},
            {"id": 2, "name": "Bob", "amount": 400, "region": "EMEA"},
            {"id": 3, "name": "蔡", "amount": 2100, "region": "APAC"},
            {"id": 3, "name": "蔡 duplicate", "amount": 2100, "region": "APAC"},
        ]

    def tearDown(self):
        self.context.cleanup()

    def create(self, path="data.csv"):
        return self.tool.execute(mode="create", file_path=path, rows=self.rows)


class TestTabularValidation(TabularTestCase):
    def test_invalid_mode(self):
        result = self.tool.execute(mode="execute", file_path="data.csv")
        self.assertIn("mode must be", result["error"])

    def test_invalid_extension(self):
        result = self.tool.execute(mode="read", file_path="data.xlsx")
        self.assertIn(".csv, .tsv, or .jsonl", result["error"])

    def test_path_escape(self):
        result = self.tool.execute(mode="read", file_path="../data.csv")
        self.assertIn("escapes the allowed directory", result["error"])

    def test_invalid_configuration(self):
        self.tool.max_rows = False
        result = self.tool.execute(mode="read", file_path="data.csv")
        self.assertIn("max_rows must be a positive integer", result["error"])

    def test_create_requires_rows(self):
        result = self.tool.execute(mode="create", file_path="data.csv", rows=[])
        self.assertIn("rows must be a non-empty list", result["error"])

    def test_rejects_nested_cell(self):
        result = self.tool.execute(mode="create", file_path="data.jsonl", rows=[{"x": {"nested": 1}}])
        self.assertIn("must be a scalar", result["error"])

    def test_rejects_nonfinite_cell(self):
        result = self.tool.execute(mode="create", file_path="data.jsonl", rows=[{"x": float("inf")}])
        self.assertIn("must be finite", result["error"])

    def test_rejects_duplicate_csv_headers(self):
        with open(os.path.join(self.base_dir, "data.csv"), "w", encoding="utf-8") as stream:
            stream.write("a,a\n1,2\n")
        result = self.tool.execute(mode="read", file_path="data.csv")
        self.assertIn("column names must be unique", result["error"])

    def test_rejects_invalid_jsonl_line(self):
        with open(os.path.join(self.base_dir, "data.jsonl"), "w", encoding="utf-8") as stream:
            stream.write('{"ok":1}\nnot-json\n')
        result = self.tool.execute(mode="read", file_path="data.jsonl")
        self.assertIn("invalid JSON on line 2", result["error"])

    def test_transform_requires_distinct_output_path(self):
        self.create()
        result = self.tool.execute(mode="transform", file_path="data.csv", output_path="data.csv")
        self.assertIn("must differ", result["error"])

    def test_rejects_unknown_filter_column_and_operator(self):
        self.create()
        result = self.tool.execute(
            mode="transform",
            file_path="data.csv",
            output_path="out.csv",
            filters=[{"column": "missing", "operator": "eval", "value": "x"}],
        )
        self.assertIn("existing column", result["error"])

    def test_is_null_filter_requires_boolean_value(self):
        self.create()
        result = self.tool.execute(
            mode="transform",
            file_path="data.csv",
            output_path="out.csv",
            filters=[{"column": "name", "operator": "is_null", "value": "yes"}],
        )
        self.assertIn("must be a boolean", result["error"])

    def test_write_limit_preserves_destination(self):
        destination = os.path.join(self.base_dir, "out.csv")
        with open(destination, "wb") as stream:
            stream.write(b"existing")
        self.tool.max_write_bytes = 4
        with self.assertRaisesRegex(ValueError, "max_write_bytes"):
            self.tool._write(destination, [{"a": "long-value"}], ["a"])
        with open(destination, "rb") as stream:
            self.assertEqual(stream.read(), b"existing")


class TestTabularOperations(TabularTestCase):
    def test_csv_create_read_round_trip(self):
        created = self.create("nested/data.csv")
        self.assertEqual(created["row_count"], 4)
        read = self.tool.execute(mode="read", file_path="nested/data.csv")
        self.assertEqual(read["columns"], ["id", "name", "amount", "region"])
        self.assertEqual(read["rows"][2]["name"], "蔡")
        self.assertEqual(read["rows"][0]["amount"], "1200.5")

    def test_tsv_round_trip(self):
        self.create("data.tsv")
        read = self.tool.execute(mode="read", file_path="data.tsv")
        self.assertEqual(read["row_count"], 4)
        self.assertEqual(read["rows"][1]["name"], "Bob")

    def test_jsonl_preserves_scalar_types(self):
        self.create("data.jsonl")
        read = self.tool.execute(mode="read", file_path="data.jsonl")
        self.assertEqual(read["rows"][0]["id"], 1)
        self.assertEqual(read["rows"][0]["amount"], 1200.5)

    def test_profile_numeric_and_top_values(self):
        self.create("data.jsonl")
        profile = self.tool.execute(mode="profile", file_path="data.jsonl")
        by_name = {column["name"]: column for column in profile["columns"]}
        self.assertEqual(by_name["amount"]["numeric"]["max"], 2100)
        self.assertEqual(by_name["region"]["top_values"][0], {"value": "APAC", "count": 3})

    def test_transform_filter_sort_project_convert(self):
        self.create()
        transformed = self.tool.execute(
            mode="transform",
            file_path="data.csv",
            output_path="out.jsonl",
            filters=[{"column": "amount", "operator": "gte", "value": 1000}],
            select_columns=["name", "amount"],
            sort_by="amount",
            descending=True,
            deduplicate_by=["amount"],
        )
        self.assertEqual(transformed["output_row_count"], 2)
        with open(transformed["output_path"], encoding="utf-8") as stream:
            rows = [json.loads(line) for line in stream]
        self.assertEqual(rows[0], {"name": "蔡", "amount": "2100"})
        self.assertEqual(rows[1]["name"], "Alice")

    def test_all_structured_filter_operators(self):
        self.create("data.jsonl")
        cases = [
            ({"column": "region", "operator": "eq", "value": "EMEA"}, 1),
            ({"column": "region", "operator": "ne", "value": "APAC"}, 1),
            ({"column": "amount", "operator": "gt", "value": 1000}, 3),
            ({"column": "name", "operator": "contains", "value": "蔡"}, 2),
            ({"column": "id", "operator": "in", "value": [1, 2]}, 2),
        ]
        for index, (predicate, expected) in enumerate(cases):
            result = self.tool.execute(
                mode="transform",
                file_path="data.jsonl",
                output_path=f"out-{index}.jsonl",
                filters=[predicate],
            )
            self.assertEqual(result["output_row_count"], expected)

    def test_limit_and_output_context_truncation(self):
        self.create("data.jsonl")
        read = self.tool.execute(mode="read", file_path="data.jsonl", limit=2)
        self.assertEqual(read["returned_row_count"], 2)
        self.assertTrue(read["truncated"])
        self.tool.max_output_chars = 3
        read = self.tool.execute(mode="read", file_path="data.jsonl")
        self.assertTrue(read["truncated"])

    def test_overwrite_is_explicit(self):
        self.create()
        refused = self.tool.execute(mode="create", file_path="data.csv", rows=[{"x": 1}])
        self.assertIn("overwrite=true", refused["error"])
        replaced = self.tool.execute(mode="create", file_path="data.csv", rows=[{"x": 1}], overwrite=True)
        self.assertTrue(replaced["overwritten"])


class TestTabularRegistration(unittest.TestCase):
    def setUp(self):
        self.configer = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_yaml_schema(self):
        component = ComponentConfiger().load_by_configer(self.configer)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "TabularDataTool")

    def test_manager_registration(self):
        configer = ToolConfiger().load_by_configer(self.configer)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, TabularDataTool)
        self.assertEqual(tool.input_keys, ["mode", "file_path"])


if __name__ == "__main__":
    unittest.main()
