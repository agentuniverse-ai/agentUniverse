#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

import httpx

from agentuniverse.agent.action.tool.api_tool import (
    APITool,
    _sanitize_secrets_from_text,
    _sanitize_url_for_error,
)


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


class TestApiToolCredentialRedaction(unittest.TestCase):
    """Request context must never leak credentials into exception messages."""

    @staticmethod
    def _response_for(url: str, body: str,
                      status_code: int = 401) -> httpx.Response:
        return httpx.Response(
            status_code, text=body, request=httpx.Request("GET", url))

    def test_query_credentials_are_masked(self) -> None:
        response = self._response_for(
            'https://offline.invalid/items?api_key=synthetic-secret&limit=10',
            'denied')
        with self.assertRaises(Exception) as ctx:
            APITool.validate_and_parse_response(response)
        message = str(ctx.exception)
        self.assertNotIn('synthetic-secret', message)
        self.assertIn('api_key=***', message)
        self.assertIn('limit=10', message)

    def test_url_userinfo_is_masked(self) -> None:
        response = self._response_for(
            'https://user:pass@offline.invalid/x', 'denied')
        with self.assertRaises(Exception) as ctx:
            APITool.validate_and_parse_response(response)
        message = str(ctx.exception)
        self.assertNotIn('user:pass', message)
        self.assertIn('***@', message)

    def test_secrets_in_body_are_redacted_before_truncation(self) -> None:
        body = ('{"error":"invalid credentials",'
                '"api_key":"synthetic-secret-123456",'
                '"hint":"Bearer synthetic.bearer.token.value"}')
        response = self._response_for(
            'https://offline.invalid/auth', body, status_code=401)
        with self.assertRaises(Exception) as ctx:
            APITool.validate_and_parse_response(response)
        message = str(ctx.exception)
        self.assertNotIn('synthetic-secret-123456', message)
        self.assertNotIn('synthetic.bearer.token.value', message)
        self.assertIn('REDACTED', message)

    def test_masked_url_still_identifies_endpoint(self) -> None:
        response = self._response_for(
            'https://api.example.com/v1/search?token=abc123secret&q=refund',
            'nope')
        with self.assertRaises(Exception) as ctx:
            APITool.validate_and_parse_response(response)
        message = str(ctx.exception)
        self.assertNotIn('abc123secret', message)
        self.assertIn('https://api.example.com/v1/search', message)
        self.assertIn('token=***', message)
        self.assertIn('q=refund', message)


class TestSanitizeUrlForError(unittest.TestCase):
    """Direct coverage for the URL sanitizer's precision and recall."""

    def test_url_without_query_is_unchanged(self) -> None:
        self.assertEqual(
            _sanitize_url_for_error('https://api.example.com/v1/items'),
            'https://api.example.com/v1/items')

    def test_benign_params_are_not_masked(self) -> None:
        sanitized = _sanitize_url_for_error(
            'https://api.example.com/s?design=blue&author=lee&page=2')
        self.assertIn('design=blue', sanitized)
        self.assertIn('author=lee', sanitized)
        self.assertIn('page=2', sanitized)

    def test_sensitive_keys_masked_case_insensitively(self) -> None:
        sanitized = _sanitize_url_for_error(
            'https://api.example.com/s?API_KEY=k1&X-Auth-Token=k2'
            '&session_id=k3&client_secret=k4')
        for leaked in ('k1', 'k2', 'k3', 'k4'):
            self.assertNotIn(leaked, sanitized)
        self.assertIn('API_KEY=***', sanitized)
        self.assertIn('X-Auth-Token=***', sanitized)
        self.assertIn('session_id=***', sanitized)
        self.assertIn('client_secret=***', sanitized)

    def test_userinfo_is_masked(self) -> None:
        sanitized = _sanitize_url_for_error(
            'https://user:pass@api.example.com/s?x=1')
        self.assertNotIn('user:pass', sanitized)
        self.assertIn('***@api.example.com', sanitized)


class TestSanitizeSecretsFromText(unittest.TestCase):
    """Direct coverage for the response-body sanitizer."""

    def test_key_name_is_preserved_for_kv_secrets(self) -> None:
        sanitized = _sanitize_secrets_from_text(
            '{"password": "hunter2hunter2"}')
        self.assertIn('password', sanitized)
        self.assertNotIn('hunter2hunter2', sanitized)
        self.assertIn('[REDACTED]', sanitized)

    def test_standalone_token_shapes_are_redacted(self) -> None:
        sanitized = _sanitize_secrets_from_text(
            'sk-proj-abcdefghijklmnopqrstuv '
            'Bearer abcdefghijklmnop '
            'AKIA1234567890ABCDEF '
            'ghp_abcdefghijklmnopqrstuvwxyz123456 '
            'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N')
        self.assertNotIn('abcdefghijklmnopqrstuv', sanitized)
        self.assertNotIn('abcdefghijklmnop', sanitized)
        self.assertNotIn('AKIA1234567890ABCDEF', sanitized)
        self.assertNotIn('abcdefghijklmnopqrstuvwxyz123456', sanitized)
        self.assertNotIn('eyJzdWIiOiIxMjM0NTY3ODkwIn0', sanitized)

    def test_benign_text_is_untouched(self) -> None:
        text = 'design=blue&author=lee short'
        self.assertEqual(_sanitize_secrets_from_text(text), text)


if __name__ == "__main__":
    unittest.main()
