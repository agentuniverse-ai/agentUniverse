#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.agent.action.tool.api_tool import APITool


class TestAPIToolTypeConversion(unittest.TestCase):
    def setUp(self):
        self.tool = APITool()

    def test_boolean_string_false_is_false(self):
        result = self.tool.convert_body_property_type(
            {"type": "boolean"},
            "false",
        )

        self.assertIs(result, False)

    def test_boolean_rejects_unknown_strings(self):
        result = self.tool.convert_body_property_type(
            {"type": "boolean"},
            "definitely",
        )

        self.assertEqual(result, "definitely")

    def test_boolean_numeric_zero_and_one(self):
        self.assertIs(
            self.tool.convert_body_property_type({"type": "boolean"}, 0),
            False,
        )
        self.assertIs(
            self.tool.convert_body_property_type({"type": "boolean"}, 1),
            True,
        )

    def test_number_accepts_native_numeric_values(self):
        self.assertEqual(
            self.tool.convert_body_property_type({"type": "number"}, 12),
            12,
        )
        self.assertEqual(
            self.tool.convert_body_property_type({"type": "number"}, 12.5),
            12.5,
        )

    def test_anyof_uses_same_scalar_conversion(self):
        result = self.tool.convert_body_property_any_of(
            {},
            "false",
            [{"type": "boolean"}, {"type": "string"}],
        )

        self.assertIs(result, False)


if __name__ == "__main__":
    unittest.main()
