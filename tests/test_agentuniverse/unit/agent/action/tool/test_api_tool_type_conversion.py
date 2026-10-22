#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

from agentuniverse.agent.action.tool.api_tool import APITool


class TestAPIToolTypeConversion(unittest.TestCase):
    """Unit tests for APITool JSON-schema property type conversions."""
    def setUp(self):
        """Create an APITool instance for the conversion tests."""
        self.tool = APITool()

    def test_boolean_string_false_is_false(self):
        """Verify the string "false" converts to the boolean False."""
        result = self.tool.convert_body_property_type(
            {"type": "boolean"},
            "false",
        )

        self.assertIs(result, False)

    def test_boolean_rejects_unknown_strings(self):
        """Verify an unrecognized string is returned unchanged instead of being converted."""
        result = self.tool.convert_body_property_type(
            {"type": "boolean"},
            "definitely",
        )

        self.assertEqual(result, "definitely")

    def test_boolean_numeric_zero_and_one(self):
        """Verify numeric 0 and 1 convert to False and True respectively."""
        self.assertIs(
            self.tool.convert_body_property_type({"type": "boolean"}, 0),
            False,
        )
        self.assertIs(
            self.tool.convert_body_property_type({"type": "boolean"}, 1),
            True,
        )

    def test_number_accepts_native_numeric_values(self):
        """Verify native int and float values pass through the number conversion unchanged."""
        self.assertEqual(
            self.tool.convert_body_property_type({"type": "number"}, 12),
            12,
        )
        self.assertEqual(
            self.tool.convert_body_property_type({"type": "number"}, 12.5),
            12.5,
        )

    def test_anyof_uses_same_scalar_conversion(self):
        """Verify anyOf conversion applies the same scalar conversion rules."""
        result = self.tool.convert_body_property_any_of(
            {},
            "false",
            [{"type": "boolean"}, {"type": "string"}],
        )

        self.assertIs(result, False)

    def test_missing_required_body_parameter_reports_operation(self):
        self.tool.openapi_spec = {
            "operation": {
                "operationId": "createUser",
                "parameters": [],
            },
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "required": ["name"],
                            "properties": {"name": {"type": "string"}},
                        },
                    },
                },
            },
        }

        with patch("agentuniverse.agent.action.tool.api_tool.ssrf_proxy.post") as post:
            with self.assertRaisesRegex(
                ValueError,
                "Missing required parameter name in operation createUser",
            ):
                self.tool.do_http_request(
                    "https://example.com/users",
                    "post",
                    {},
                    {},
                )

        post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
