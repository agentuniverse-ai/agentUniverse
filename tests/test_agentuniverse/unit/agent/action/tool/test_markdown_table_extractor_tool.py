#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import markdown_table_extractor_tool as md_module
from agentuniverse.agent.action.tool.common_tool.markdown_table_extractor_tool import (
    MarkdownTableExtractorTool,
)
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = md_module.__file__.replace(".py", ".yaml")

SINGLE = """# Title

Some intro text.

| Name | Age | City |
|------|-----|------|
| Alice | 30 | Beijing |
| Bob | 25 | Shanghai |

Trailing paragraph.
"""

TWO_TABLES = """| A | B |
|---|---|
| 1 | 2 |

text in between

| X | Y |
|---|---|
| 9 | 8 |
"""

NO_TABLE = "Just a paragraph. No table here."


class MarkdownTableExtractorToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = MarkdownTableExtractorTool()

    # ---- extract ------------------------------------------------------------
    def test_extract_single_table(self) -> None:
        result = self.tool.execute(text=SINGLE, mode="extract")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["table_count"], 1)
        table = result["tables"][0]
        self.assertEqual(table["header"], ["Name", "Age", "City"])
        self.assertEqual(table["rows"], [["Alice", "30", "Beijing"], ["Bob", "25", "Shanghai"]])
        self.assertEqual(table["row_count"], 2)
        self.assertEqual(table["column_count"], 3)

    def test_extract_multiple_tables(self) -> None:
        result = self.tool.execute(text=TWO_TABLES, mode="extract")
        self.assertEqual(result["table_count"], 2)
        self.assertEqual(result["tables"][0]["header"], ["A", "B"])
        self.assertEqual(result["tables"][1]["header"], ["X", "Y"])

    def test_extract_no_table(self) -> None:
        result = self.tool.execute(text=NO_TABLE, mode="extract")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["table_count"], 0)
        self.assertEqual(result["tables"], [])

    def test_extract_first(self) -> None:
        result = self.tool.execute(text=TWO_TABLES, mode="extract_first")
        self.assertEqual(result["table"]["header"], ["A", "B"])
        self.assertEqual(result["table"]["rows"], [["1", "2"]])

    def test_extract_first_none(self) -> None:
        result = self.tool.execute(text=NO_TABLE, mode="extract_first")
        self.assertIsNone(result["table"])

    def test_table_without_outer_pipes(self) -> None:
        text = "Name | Age\n--- | ---\nCara | 40"
        result = self.tool.execute(text=text, mode="extract")
        self.assertEqual(result["table_count"], 1)
        self.assertEqual(result["tables"][0]["header"], ["Name", "Age"])
        self.assertEqual(result["tables"][0]["rows"], [["Cara", "40"]])

    def test_alignment_colons_in_separator(self) -> None:
        text = "| a | b |\n|:--:|---:|\n| 1 | 2 |"
        result = self.tool.execute(text=text, mode="extract")
        self.assertEqual(result["table_count"], 1)
        self.assertEqual(result["tables"][0]["rows"], [["1", "2"]])

    def test_escaped_pipes_in_cells(self) -> None:
        text = "| col |\n|-----|\n| a\\|b |"
        result = self.tool.execute(text=text, mode="extract")
        self.assertEqual(result["tables"][0]["rows"], [["a|b"]])

    def test_table_with_no_data_rows(self) -> None:
        text = "| H1 | H2 |\n|----|----|"
        result = self.tool.execute(text=text, mode="extract")
        self.assertEqual(result["table_count"], 1)
        self.assertEqual(result["tables"][0]["row_count"], 0)
        self.assertEqual(result["tables"][0]["rows"], [])

    def test_separator_without_dashes_rejected(self) -> None:
        # A row of only pipes/colons (no dash) is not a separator.
        text = "| a | b |\n| ::: | ::: |\n| 1 | 2 |"
        result = self.tool.execute(text=text, mode="extract")
        self.assertEqual(result["table_count"], 0)

    def test_empty_cells_preserved(self) -> None:
        text = "| a | b |\n|---|---|\n|  |  |"
        result = self.tool.execute(text=text, mode="extract")
        self.assertEqual(result["tables"][0]["rows"], [["", ""]])

    # ---- to_csv -------------------------------------------------------------
    def test_to_csv_single_table(self) -> None:
        result = self.tool.execute(text=SINGLE, mode="to_csv")
        self.assertEqual(result["status"], "success")
        lines = result["csv"].strip().split("\n")
        self.assertEqual(lines[0], "Name,Age,City")
        self.assertEqual(lines[1], "Alice,30,Beijing")
        self.assertEqual(lines[2], "Bob,25,Shanghai")

    def test_to_csv_by_index(self) -> None:
        result = self.tool.execute(text=TWO_TABLES, mode="to_csv", table_index=1)
        self.assertEqual(result["table_index"], 1)
        lines = result["csv"].strip().split("\n")
        self.assertEqual(lines[0], "X,Y")
        self.assertEqual(lines[1], "9,8")

    def test_to_csv_out_of_range(self) -> None:
        result = self.tool.execute(text=SINGLE, mode="to_csv", table_index=5)
        self.assertEqual(result["status"], "error")
        self.assertIn("out of range", result["error"])

    def test_to_csv_no_table(self) -> None:
        result = self.tool.execute(text=NO_TABLE, mode="to_csv")
        self.assertEqual(result["csv"], "")

    # ---- to_json ------------------------------------------------------------
    def test_to_json_objects(self) -> None:
        result = self.tool.execute(text=SINGLE, mode="to_json")
        data = json.loads(result["json"])
        self.assertEqual(data[0], {"Name": "Alice", "Age": "30", "City": "Beijing"})
        self.assertEqual(data[1]["Name"], "Bob")

    def test_to_json_by_index(self) -> None:
        result = self.tool.execute(text=TWO_TABLES, mode="to_json", table_index=0)
        data = json.loads(result["json"])
        self.assertEqual(data, [{"A": "1", "B": "2"}])

    def test_to_json_no_table(self) -> None:
        result = self.tool.execute(text=NO_TABLE, mode="to_json")
        self.assertEqual(result["json"], "[]")

    # ---- validation ---------------------------------------------------------
    def test_rejects_non_string_text(self) -> None:
        result = self.tool.execute(text=123)
        self.assertEqual(result["error_type"], "validation_error")

    def test_rejects_bad_mode(self) -> None:
        result = self.tool.execute(text=SINGLE, mode="convert")
        self.assertIn("mode must be", result["error"])

    def test_rejects_negative_index(self) -> None:
        result = self.tool.execute(text=SINGLE, mode="to_csv", table_index=-1)
        self.assertIn("table_index", result["error"])


class MarkdownTableRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.config = Configer(path=YAML_PATH).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "MarkdownTableExtractorTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, MarkdownTableExtractorTool)
        self.assertEqual(tool.input_keys, ["text"])

    def test_yaml_loads_as_dict(self):
        with open(YAML_PATH, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        self.assertEqual(data["name"], "markdown_table_extractor_tool")
        self.assertEqual(data["metadata"]["class"], "MarkdownTableExtractorTool")


if __name__ == "__main__":
    unittest.main()
