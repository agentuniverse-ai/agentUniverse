#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

from agentuniverse.agent.action.tool.utils import ssrf_proxy


class TestSSRFProxy(unittest.TestCase):
    def test_default_timeout_is_used_when_not_provided(self):
        with patch.object(ssrf_proxy, "SSRF_PROXY_ALL_URL", ""):
            with patch.object(ssrf_proxy, "proxies", None):
                with patch.object(ssrf_proxy.httpx, "request", return_value="ok") as request:
                    result = ssrf_proxy.get("https://example.com")

        self.assertEqual(result, "ok")
        request.assert_called_once_with(
            method="GET",
            url="https://example.com",
            timeout=20,
        )

    def test_caller_timeout_overrides_default(self):
        with patch.object(ssrf_proxy, "SSRF_PROXY_ALL_URL", ""):
            with patch.object(ssrf_proxy, "proxies", None):
                with patch.object(ssrf_proxy.httpx, "request", return_value="ok") as request:
                    result = ssrf_proxy.get("https://example.com", timeout=5)

        self.assertEqual(result, "ok")
        request.assert_called_once_with(
            method="GET",
            url="https://example.com",
            timeout=5,
        )

    def test_proxy_url_is_added_without_overwriting_timeout(self):
        with patch.object(ssrf_proxy, "SSRF_PROXY_ALL_URL", "http://proxy.local"):
            with patch.object(ssrf_proxy.httpx, "request", return_value="ok") as request:
                result = ssrf_proxy.post("https://example.com", timeout=3)

        self.assertEqual(result, "ok")
        request.assert_called_once_with(
            method="POST",
            url="https://example.com",
            timeout=3,
            proxy="http://proxy.local",
        )


if __name__ == "__main__":
    unittest.main()
