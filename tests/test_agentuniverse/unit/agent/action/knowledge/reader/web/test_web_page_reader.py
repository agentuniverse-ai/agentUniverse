# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import builtins
import io
import logging
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.web.web_page_reader import WebPageReader

HTML = """
<html>
  <head><style>a { color: red; }</style><script>console.log('x')</script></head>
  <body>
    <p>Hello main content</p>
    <noscript>javascript off</noscript>
  </body>
</html>
"""

READER_LOGGER_NAME = "agentuniverse.agent.action.knowledge.reader.web.web_page_reader"


class _ListHandler(logging.Handler):
    """Captures log records emitted during a test."""

    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append(record)


class TestWebPageReader(unittest.TestCase):

    def setUp(self):
        self.reader = WebPageReader()
        self.logger = logging.getLogger(READER_LOGGER_NAME)
        self.handler = _ListHandler()
        self._prev_level = self.logger.level
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.logger.setLevel(self._prev_level)

    def test_normal_read_does_not_write_to_stdout(self):
        # A normal read must produce a document and leave stdout/stderr clean —
        # the old code leaked debug prints; the fix routes diagnostics through a
        # module logger instead.
        with patch.object(WebPageReader, "_fetch_html", return_value=HTML):
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                docs = self.reader.load_data(url="https://example.com/article")

        self.assertEqual(len(docs), 1)
        self.assertIn("Hello main content", docs[0].text)
        self.assertNotIn("javascript off", docs[0].text)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), "")

    def test_fallback_failures_are_logged_not_swallowed(self):
        # trafilatura and readability are optional deps not installed in this
        # environment, so they raise ImportError and must be recorded (with the
        # URL and exception context) before falling through to the bs4 extractor.
        with patch.object(WebPageReader, "_fetch_html", return_value=HTML):
            docs = self.reader.load_data(url="https://example.com/article")

        messages = [self.handler.format(r) for r in self.handler.records]
        self.assertEqual(docs[0].metadata.get("extractor"), "bs4")
        self.assertTrue(
            any("trafilatura" in m and "example.com" in m for m in messages),
            f"expected a trafilatura fallback log mentioning the URL, got: {messages}",
        )
        # logged records must carry exception context so operators can diagnose
        # *why* a fallback was selected (dependency missing vs parse/TLS error)
        self.assertTrue(any(r.exc_info for r in self.handler.records))

    def test_missing_all_extractors_raises(self):
        # When every extractor is unavailable the reader must raise rather than
        # silently return empty content.
        real_import = builtins.__import__

        def _block_extractors(name, *args, **kwargs):
            if name in {"trafilatura", "readability", "bs4"}:
                raise ImportError(f"blocked {name}")
            return real_import(name, *args, **kwargs)

        with patch.object(WebPageReader, "_fetch_html", return_value=HTML), \
                patch("builtins.__import__", side_effect=_block_extractors):
            with self.assertRaises(RuntimeError) as ctx:
                self.reader.load_data(url="https://example.com/article")
        self.assertIn("extractors", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
