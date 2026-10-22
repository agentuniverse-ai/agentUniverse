#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for APITool redirect / SSRF defaults.

Locks in the contract that APITool does NOT follow redirects by default
(closing an SSRF escape hatch where a 30x from an attacker-controlled
endpoint could redirect an authenticated request to an internal metadata
service), and that redirects are a deliberate opt-in bounded by
``max_redirects``.
"""

import unittest
from unittest.mock import patch, MagicMock

from agentuniverse.agent.action.tool.api_tool import APITool
from agentuniverse.agent.action.tool.tool import ToolInput


def _make_tool(allow_redirects=None, max_redirects=None) -> APITool:
    tool = APITool()
    tool.openapi_spec = {
        "url": "https://api.example.com/v1/items",
        "method": "GET",
        "operation": {"parameters": []},
    }
    if allow_redirects is not None:
        tool.allow_redirects = allow_redirects
    if max_redirects is not None:
        tool.max_redirects = max_redirects
    return tool


class TestAPIToolRedirectDefaults(unittest.TestCase):
    """The defaults are part of the security contract; pin them."""

    def test_default_disallows_redirects(self) -> None:
        tool = APITool()
        self.assertFalse(tool.allow_redirects,
                         "APITool must not follow redirects by default; it is "
                         "an SSRF escape hatch.")

    def test_default_max_redirects_is_bounded(self) -> None:
        tool = APITool()
        self.assertEqual(tool.max_redirects, 5)
        self.assertGreater(tool.max_redirects, 0)


class TestAPIToolRequestRedirectBehavior(unittest.TestCase):
    """The do_http_request path passes the configured redirect contract."""

    def test_default_request_does_not_follow_redirects(self) -> None:
        tool = _make_tool()
        with patch("agentuniverse.agent.action.tool.api_tool.ssrf_proxy") as proxy:
            proxy.get.return_value = MagicMock(text="ok")
            tool.do_http_request(tool.openapi_spec["url"], "GET", {}, {})
        # follow_redirects=False is passed explicitly so the contract is
        # observable in the call.
        self.assertFalse(proxy.get.call_args.kwargs["follow_redirects"])
        # max_redirects is 0 when redirects are off (defensive; never used).
        self.assertEqual(proxy.get.call_args.kwargs["max_redirects"], 0)

    def test_opting_into_redirects_passes_bounded_max_redirects(self) -> None:
        tool = _make_tool(allow_redirects=True, max_redirects=3)
        with patch("agentuniverse.agent.action.tool.api_tool.ssrf_proxy") as proxy:
            proxy.get.return_value = MagicMock(text="ok")
            tool.do_http_request(tool.openapi_spec["url"], "GET", {}, {})
        self.assertTrue(proxy.get.call_args.kwargs["follow_redirects"])
        self.assertEqual(proxy.get.call_args.kwargs["max_redirects"], 3)

    def test_opting_into_redirects_uses_configured_max_not_default(self) -> None:
        tool = _make_tool(allow_redirects=True, max_redirects=10)
        with patch("agentuniverse.agent.action.tool.api_tool.ssrf_proxy") as proxy:
            proxy.get.return_value = MagicMock(text="ok")
            tool.do_http_request(tool.openapi_spec["url"], "GET", {}, {})
        self.assertEqual(proxy.get.call_args.kwargs["max_redirects"], 10)

    def test_post_method_also_respects_redirect_default(self) -> None:
        # All methods share the same redirect contract.
        tool = _make_tool()
        tool.openapi_spec["method"] = "POST"
        with patch("agentuniverse.agent.action.tool.api_tool.ssrf_proxy") as proxy:
            proxy.post.return_value = MagicMock(text="ok")
            tool.do_http_request(tool.openapi_spec["url"], "POST", {}, {})
        self.assertFalse(proxy.post.call_args.kwargs["follow_redirects"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
