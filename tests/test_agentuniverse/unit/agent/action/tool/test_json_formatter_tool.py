#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for JSONFormatterTool."""

import os
import unittest

from agentuniverse.agent.action.tool.common_tool import json_formatter_tool as module
from agentuniverse.agent.action.tool.common_tool.json_formatter_tool import JSONFormatterTool

YAML_PATH = os.path.join(os.path.dirname(module.__file__), "json_formatter_tool.yaml.example")


class JSONFormatterToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = JSONFormatterTool()

    # --- beautify -------------------------------------------------------
    def test_beautify_indents_object(self):
        result = self.tool.execute(mode="beautify", input='{"a":1,"b":2}')
        self.assertEqual(result["status"], "success")
        self.assertIn('"a": 1', result["output"])
        self.assertIn("\n", result["output"])

    def test_beautify_preserves_unicode(self):
        result = self.tool.execute(mode="beautify", input='{"name":"中文"}')
        self.assertEqual(result["status"], "success")
        self.assertIn("中文", result["output"])

    def test_beautify_respects_custom_indent(self):
        tool = JSONFormatterTool(indent=4)
        result = tool.execute(mode="beautify", input='{"a":1}')
        self.assertIn('    "a"', result["output"])

    # --- minify ---------------------------------------------------------
    def test_minify_removes_whitespace(self):
        result = self.tool.execute(mode="minify", input='{"a": 1, "b": [1, 2]}')
        self.assertEqual(result["output"], '{"a":1,"b":[1,2]}')
        self.assertLess(result["output_chars"], result["input_chars"])

    def test_minify_on_already_minimal(self):
        result = self.tool.execute(mode="minify", input='{"a":1}')
        self.assertEqual(result["output"], '{"a":1}')

    # --- validate -------------------------------------------------------
    def test_validate_accepts_valid_json(self):
        result = self.tool.execute(mode="validate", input='{"a": 1, "b": [1,2]}')
        self.assertTrue(result["valid"])
        self.assertEqual(result["type"], "object")
        self.assertEqual(result["size"]["keys"], 2)

    def test_validate_reports_top_level_type(self):
        cases = {
            "42": "integer",
            "3.14": "number",
            '"hi"': "string",
            "true": "boolean",
            "null": "null",
            "[1, 2, 3]": "array",
        }
        for raw, expected in cases.items():
            result = self.tool.execute(mode="validate", input=raw)
            self.assertTrue(result["valid"], msg=raw)
            self.assertEqual(result["type"], expected, msg=raw)

    def test_validate_rejects_empty_input(self):
        result = self.tool.execute(mode="validate", input="   ")
        self.assertFalse(result["valid"])

    def test_validate_rejects_invalid_json(self):
        result = self.tool.execute(mode="validate", input="{not json}")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "json_error")

    # --- extract --------------------------------------------------------
    def test_extract_from_fenced_block(self):
        text = 'Here is the data:\n```json\n{"a": 1}\n```\nThanks!'
        result = self.tool.execute(mode="extract", input=text)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["type"], "object")
        self.assertIn('"a"', result["output"])

    def test_extract_from_prose_braces(self):
        text = 'The answer is {"x": 10, "y": 20} as shown above.'
        result = self.tool.execute(mode="extract", input=text)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["type"], "object")
        self.assertGreaterEqual(result["end"], result["start"])

    def test_extract_array(self):
        text = 'prefix [1, 2, 3] suffix'
        result = self.tool.execute(mode="extract", input=text)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["type"], "array")

    def test_extract_none_found(self):
        result = self.tool.execute(mode="extract", input="no json here at all")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "json_error")

    def test_extract_brace_inside_string_does_not_confuse_scan(self):
        # A brace inside a JSON string value must not break balancing.
        text = 'noise {"msg": "hello {world}"} trailing'
        result = self.tool.execute(mode="extract", input=text)
        self.assertEqual(result["status"], "success")
        self.assertIn("hello {world}", result["output"])

    # --- config / errors ------------------------------------------------
    def test_invalid_mode(self):
        result = self.tool.execute(mode="compress", input="{}")
        self.assertEqual(result["status"], "error")
        self.assertIn("mode must be", result["error"])

    def test_input_too_large(self):
        tool = JSONFormatterTool(max_input_chars=10)
        result = tool.execute(mode="beautify", input="x" * 50)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_input_chars", result["error"])

    def test_non_string_input(self):
        result = self.tool.execute(mode="beautify", input={"not": "a string"})
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")

    def test_invalid_indent_config(self):
        tool = JSONFormatterTool(indent=0)
        result = tool.execute(mode="beautify", input="{}")
        self.assertEqual(result["status"], "error")
        self.assertIn("indent", result["error"])


class JSONFormatterYamlTest(unittest.TestCase):
    def test_yaml_example_exists(self):
        self.assertTrue(os.path.isfile(YAML_PATH))

    def test_yaml_example_has_required_fields(self):
        import yaml

        with open(YAML_PATH, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        self.assertEqual(data["name"], "json_formatter_tool")
        self.assertEqual(data["metadata"]["class"], "JSONFormatterTool")
        self.assertIn("mode", data["input_keys"])
        self.assertEqual(data["max_input_chars"], 100000)


if __name__ == "__main__":
    unittest.main()
