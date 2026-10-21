#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

import httpx

from agentuniverse.agent.action.tool.api_tool import APITool


class TestApiToolRecursionErrorMessage(unittest.TestCase):
    """The anyOf recursion limit should identify the pathological schema."""

    def test_recursion_error_previews_the_schema(self) -> None:
        tool = APITool()
        schema = {"type": "string"}
        for _ in range(12):
            schema = {"anyOf": [schema]}
        with self.assertRaises(Exception) as ctx:
            tool.convert_body_property_any_of({"x": 1}, "value", [schema])
        message = str(ctx.exception)
        self.assertIn("Max recursion depth reached", message)
        self.assertIn("anyOf", message)

    def test_recursion_error_preview_is_bounded(self) -> None:
        tool = APITool()
        schema = {"type": "string", "description": "y" * 1000}
        for _ in range(12):
            schema = {"anyOf": [schema]}
        with self.assertRaises(Exception) as ctx:
            tool.convert_body_property_any_of({"x": 1}, "value", [schema])
        self.assertLess(len(str(ctx.exception)), 400)


class TestApiToolHttpMethodErrorMessage(unittest.TestCase):
    """An unsupported HTTP method should be reported with the value and options."""

    def test_invalid_method_lists_supported_methods(self) -> None:
        tool = APITool()
        tool.openapi_spec = {"operation": {}}
        with self.assertRaises(ValueError) as ctx:
            tool.do_http_request(
                "https://example.com/api", "FETCH", {}, {})
        message = str(ctx.exception)
        # do_http_request normalizes the method to lowercase on entry.
        self.assertIn("fetch", message)
        self.assertIn("Supported methods", message)
        self.assertIn("get", message)


class TestApiToolMissingParameterErrorMessage(unittest.TestCase):
    """A missing required parameter should report where it is expected."""

    def test_missing_required_parameter_reports_location(self) -> None:
        parameter = {"name": "token", "in": "header", "required": True}
        with self.assertRaises(Exception) as ctx:
            APITool.get_parameter_value(parameter, {})
        message = str(ctx.exception)
        self.assertIn("token", message)
        self.assertIn("in: header", message)

    def test_missing_required_query_parameter_reports_location(self) -> None:
        parameter = {"name": "q", "in": "query", "required": True}
        with self.assertRaises(Exception) as ctx:
            APITool.get_parameter_value(parameter, {"other": 1})
        self.assertIn("in: query", str(ctx.exception))


class TestApiToolResponseErrorMessage(unittest.TestCase):
    """HTTP error responses should carry request context, not raw megabyte dumps."""

    @staticmethod
    def _response(status_code: int, body: str) -> httpx.Response:
        return httpx.Response(
            status_code,
            text=body,
            request=httpx.Request("GET", "https://api.example.com/v1/search"),
        )

    def test_error_response_includes_url_and_reason(self) -> None:
        with self.assertRaises(Exception) as ctx:
            APITool.validate_and_parse_response(
                self._response(404, "not here"))
        message = str(ctx.exception)
        self.assertIn("https://api.example.com/v1/search", message)
        self.assertIn("404", message)

    def test_large_error_body_is_truncated(self) -> None:
        big_body = "<html>" + "gateway error " * 2000 + "</html>"
        with self.assertRaises(Exception) as ctx:
            APITool.validate_and_parse_response(
                self._response(502, big_body))
        message = str(ctx.exception)
        self.assertIn("502", message)
        self.assertIn("truncated", message)
        # The whole body must not leak into the message.
        self.assertLess(len(message), 700)

    def test_empty_error_body_is_tolerated(self) -> None:
        with self.assertRaises(Exception) as ctx:
            APITool.validate_and_parse_response(
                self._response(500, ""))
        message = str(ctx.exception)
        self.assertIn("500", message)


if __name__ == "__main__":
    unittest.main()
