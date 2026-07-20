#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch, MagicMock

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

    def test_no_redirects_uses_top_level_request_without_max_redirects(self):
        # Default path: follow_redirects is False (or unset). The request goes
        # through httpx.request directly, with no max_redirects key (the
        # top-level helper does not accept it).
        with patch.object(ssrf_proxy, "SSRF_PROXY_ALL_URL", ""):
            with patch.object(ssrf_proxy, "proxies", None):
                with patch.object(ssrf_proxy.httpx, "request", return_value="ok") as request:
                    result = ssrf_proxy.get("https://example.com",
                                            follow_redirects=False, max_redirects=5)

        self.assertEqual(result, "ok")
        request.assert_called_once_with(
            method="GET",
            url="https://example.com",
            timeout=20,
            follow_redirects=False,
        )
        # max_redirects must not leak into the top-level httpx.request kwargs.
        self.assertNotIn("max_redirects", request.call_args.kwargs)

    def test_redirects_with_max_redirects_route_through_client(self):
        # When redirects are followed AND a bound is supplied, the request goes
        # through a short-lived httpx.Client so the chain is bounded; the
        # top-level httpx.request would otherwise follow up to 20.
        fake_client = MagicMock()
        fake_client.request.return_value = "redirected-ok"
        fake_cm = MagicMock()
        fake_cm.__enter__.return_value = fake_client
        fake_cm.__exit__.return_value = False
        with patch.object(ssrf_proxy, "SSRF_PROXY_ALL_URL", ""):
            with patch.object(ssrf_proxy, "proxies", None):
                with patch.object(ssrf_proxy.httpx, "Client", return_value=fake_cm) as client_cls:
                    result = ssrf_proxy.get("https://example.com",
                                            follow_redirects=True, max_redirects=3)

        self.assertEqual(result, "redirected-ok")
        client_cls.assert_called_once_with(
            follow_redirects=True, max_redirects=3)
        fake_client.request.assert_called_once_with(
            method="GET", url="https://example.com",
            follow_redirects=True, timeout=20)


if __name__ == "__main__":
    unittest.main()
