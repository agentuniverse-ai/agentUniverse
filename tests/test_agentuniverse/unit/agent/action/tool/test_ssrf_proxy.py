#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import contextlib
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import httpx

from agentuniverse.agent.action.tool.utils import ssrf_proxy


class _ProxyHandler(BaseHTTPRequestHandler):
    """A minimal HTTP proxy that records the request line it receives."""

    recorded_paths = []

    def do_GET(self):
        type(self).recorded_paths.append(self.path)
        body = b'proxied'
        self.send_response(200)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        """Keep the test output free of request logs."""


@contextlib.contextmanager
def _local_proxy():
    """Serve a real HTTP proxy on localhost and yield its URL."""
    _ProxyHandler.recorded_paths = []
    server = ThreadingHTTPServer(('127.0.0.1', 0), _ProxyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield 'http://127.0.0.1:%d' % server.server_port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


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

    def test_split_scheme_proxies_are_used_for_a_real_request(self):
        """The per-scheme proxies must route the request, not raise TypeError.

        Proxies set through SSRF_PROXY_HTTP_URL/SSRF_PROXY_HTTPS_URL were passed
        to httpx as the `proxies=` argument, which httpx 0.28 removed, so this
        branch failed before any connection was opened.
        """
        with _local_proxy() as proxy_url:
            with patch.object(ssrf_proxy, "SSRF_PROXY_ALL_URL", ""):
                with patch.object(ssrf_proxy, "proxies",
                                  {'http://': proxy_url, 'https://': proxy_url}):
                    response = ssrf_proxy.get("http://example.com/through-proxy")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, 'proxied')
        # An HTTP proxy receives the absolute URL of the target.
        self.assertEqual(_ProxyHandler.recorded_paths, ["http://example.com/through-proxy"])

    def test_all_url_proxy_is_used_for_a_real_request(self):
        """The SSRF_PROXY_ALL_URL branch must keep routing after the rewrite.

        That branch already used httpx's `proxy=` argument and keeps calling
        httpx.request directly, so it is pinned with a live request rather than
        a mocked one.
        """
        with _local_proxy() as proxy_url:
            with patch.object(ssrf_proxy, "SSRF_PROXY_ALL_URL", proxy_url):
                with patch.object(ssrf_proxy, "proxies", None):
                    response = ssrf_proxy.get("http://example.com/all-url-proxy")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(_ProxyHandler.recorded_paths, ["http://example.com/all-url-proxy"])

    def test_split_scheme_proxies_keep_the_request_arguments(self):
        with _local_proxy() as proxy_url:
            with patch.object(ssrf_proxy, "SSRF_PROXY_ALL_URL", ""):
                with patch.object(ssrf_proxy, "proxies",
                                  {'http://': proxy_url, 'https://': proxy_url}):
                    response = ssrf_proxy.get("http://example.com/with-headers",
                                              timeout=5,
                                              headers={'X-Probe': 'yes'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(_ProxyHandler.recorded_paths, ["http://example.com/with-headers"])

    def test_split_scheme_proxies_work_on_the_installed_httpx(self):
        """Guard the httpx API this branch relies on."""
        self.assertTrue(hasattr(httpx, "HTTPTransport"))
        transport = httpx.HTTPTransport(proxy='http://127.0.0.1:1')
        self.assertIsInstance(httpx.Client(mounts={'http://': transport}), httpx.Client)


if __name__ == "__main__":
    unittest.main()
