#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for HttpRequestTool."""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.tool.common_tool.http_request_tool import \
    HttpRequestTool


def _mock_response(status_code=200, text="ok", headers=None, url="http://example.com"):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.headers = headers or {"Content-Type": "application/json"}
    resp.url = url
    return resp


class TestHttpRequestToolValidation(unittest.TestCase):

    def test_empty_url_rejected(self):
        tool = HttpRequestTool()
        result = tool.execute(url="", method="GET")
        self.assertEqual(result["status"], "error")

    def test_non_http_url_rejected(self):
        tool = HttpRequestTool()
        result = tool.execute(url="ftp://files.example.com", method="GET")
        self.assertEqual(result["status"], "error")
        self.assertIn("http://", result["error"])

    def test_invalid_method_rejected(self):
        tool = HttpRequestTool()
        result = tool.execute(url="https://x.com", method="CONNECT")
        self.assertEqual(result["status"], "error")


class TestHttpRequestToolGet(unittest.TestCase):

    def test_get_returns_structured_response(self):
        tool = HttpRequestTool()
        with patch("agentuniverse.agent.action.tool.common_tool."
                   "http_request_tool.ssrf_proxy") as proxy:
            proxy.get.return_value = _mock_response(
                text='{"key": "value"}',
                headers={"Content-Type": "application/json"})
            result = tool.execute(url="https://api.example.com/data")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["status_code"], 200)
        self.assertIn("key", result["body"])
        self.assertFalse(result["truncated"])

    def test_redirects_disabled_by_default(self):
        tool = HttpRequestTool()
        with patch("agentuniverse.agent.action.tool.common_tool."
                   "http_request_tool.ssrf_proxy") as proxy:
            proxy.get.return_value = _mock_response()
            tool.execute(url="https://x.com")
            self.assertFalse(proxy.get.call_args.kwargs["follow_redirects"])

    def test_redirects_opt_in(self):
        tool = HttpRequestTool(allow_redirects=True, max_redirects=3)
        with patch("agentuniverse.agent.action.tool.common_tool."
                   "http_request_tool.ssrf_proxy") as proxy:
            proxy.get.return_value = _mock_response()
            tool.execute(url="https://x.com")
            self.assertTrue(proxy.get.call_args.kwargs["follow_redirects"])
            self.assertEqual(proxy.get.call_args.kwargs["max_redirects"], 3)

    def test_timeout_passed(self):
        tool = HttpRequestTool(default_timeout=10)
        with patch("agentuniverse.agent.action.tool.common_tool."
                   "http_request_tool.ssrf_proxy") as proxy:
            proxy.get.return_value = _mock_response()
            tool.execute(url="https://x.com")
            self.assertEqual(proxy.get.call_args.kwargs["timeout"], 10)


class TestHttpRequestToolPost(unittest.TestCase):

    def test_post_sends_json_body(self):
        tool = HttpRequestTool()
        with patch("agentuniverse.agent.action.tool.common_tool."
                   "http_request_tool.ssrf_proxy") as proxy:
            proxy.post.return_value = _mock_response(status_code=201, text="created")
            result = tool.execute(url="https://api.example.com/create",
                                  method="POST",
                                  body={"name": "test"})
        self.assertEqual(result["status_code"], 201)
        call = proxy.post.call_args
        self.assertIn("Content-Type", call.kwargs["headers"])
        self.assertEqual(call.kwargs["headers"]["Content-Type"],
                         "application/json")

    def test_post_raw_string_body(self):
        tool = HttpRequestTool()
        with patch("agentuniverse.agent.action.tool.common_tool."
                   "http_request_tool.ssrf_proxy") as proxy:
            proxy.post.return_value = _mock_response()
            tool.execute(url="https://x.com", method="POST", body="raw text")
            self.assertEqual(proxy.post.call_args.kwargs["data"], "raw text")


class TestHttpRequestToolBounding(unittest.TestCase):

    def test_response_truncated_at_max_bytes(self):
        tool = HttpRequestTool(max_response_bytes=10)
        long_text = "x" * 5000
        with patch("agentuniverse.agent.action.tool.common_tool."
                   "http_request_tool.ssrf_proxy") as proxy:
            proxy.get.return_value = _mock_response(text=long_text)
            result = tool.execute(url="https://x.com")
        self.assertTrue(result["truncated"])
        self.assertLess(len(result["body"]), 100)


class TestHttpRequestToolError(unittest.TestCase):

    def test_network_error_returns_structured_error(self):
        tool = HttpRequestTool()
        with patch("agentuniverse.agent.action.tool.common_tool."
                   "http_request_tool.ssrf_proxy") as proxy:
            proxy.get.side_effect = ConnectionError("dns failure")
            result = tool.execute(url="https://x.com")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "request_error")


if __name__ == "__main__":
    unittest.main(verbosity=2)
