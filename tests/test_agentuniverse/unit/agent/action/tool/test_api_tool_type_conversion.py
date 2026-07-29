#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import unittest
from unittest.mock import patch

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

    def test_request_body_omits_missing_optional_properties(self):
        self.tool.openapi_spec = {
            "operation": {"parameters": []},
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string"},
                                "nickname": {"type": "string"},
                            },
                        },
                    },
                },
            },
        }

        with patch(
            "agentuniverse.agent.action.tool.api_tool.ssrf_proxy.post"
        ) as post:
            self.tool.do_http_request(
                "https://example.com/users",
                "post",
                {},
                {"name": "Ada"},
            )

        request_body = json.loads(post.call_args.kwargs["data"])
        self.assertEqual(request_body, {"name": "Ada"})


if __name__ == "__main__":
    unittest.main()
