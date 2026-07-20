# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for WebPageReader diagnostics and extractor fallback.

These tests control the extractor branch under test by mocking the optional
``trafilatura`` / ``readability`` modules directly, so the suite passes in a
minimal install (deps absent -> ImportError) AND in an environment with the
reader extras installed (deps present). The previous version assumed the
deps were absent and asserted extractor-specific output, which made it
non-portable.
"""

import builtins
import io
import logging
import sys
import types
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

# Modules the reader imports lazily inside _extract_main_text / _fetch_html.
# We install / remove fakes for these per test rather than depending on what
# the local environment happens to have installed.
_OPTIONAL_READER_MODULES = ("trafilatura", "readability", "bs4", "lxml")


class _ListHandler(logging.Handler):
    """Captures log records emitted during a test."""

    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append(record)


class _ModuleGuard:
    """Context manager that swaps fake modules into ``sys.modules`` and
    restores the prior state on exit, including removing fakes that were not
    there before.

    Lets each test control exactly which optional extractor is available and
    how it behaves, independent of what is installed in the environment.
    """

    def __init__(self, **fakes):
        # fakes maps module name -> module object (or None to force removal).
        self.fakes = fakes
        self._prev = {}

    def __enter__(self):
        for name, fake in self.fakes.items():
            self._prev[name] = sys.modules.get(name)
            if fake is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = fake
        return self

    def __exit__(self, exc_type, exc, tb):
        for name, prev in self._prev.items():
            if prev is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = prev


def _stub_module(name, **attrs):
    """Create a throwaway module object with the given attributes."""
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    return module


def _fake_trafilatura(extract_side_effect=None, extract_return=None):
    def _extract(*args, **kwargs):
        if extract_side_effect is not None:
            raise extract_side_effect
        return extract_return

    return _stub_module("trafilatura", extract=_extract)


def _fake_readability():
    # readability.Document(html).summary(...) -> a small html fragment.
    class _Doc:
        def __init__(self, html):
            pass

        def summary(self, html_partial=False):
            return "<p>readability text</p>"

    return _stub_module("readability", Document=_Doc)


def _fake_bs4():
    # bs4.BeautifulSoup(html, "lxml").get_text("\n") -> the text we injected.
    from bs4 import BeautifulSoup as _RealBs4  # use the real parser if installed

    return _stub_module("bs4", BeautifulSoup=_RealBs4)


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
        # A normal read must produce a document and leave stdout/stderr clean,
        # regardless of which extractor happens to win. We mock the trafilatura
        # extractor to return content so the test does not depend on which
        # optional deps are installed in the environment.
        trafilatura = _fake_trafilatura(extract_return="Hello main content")
        with (
            _ModuleGuard(trafilatura=trafilatura, readability=None, bs4=None, lxml=None),
            patch.object(WebPageReader, "_fetch_html", return_value=HTML),
        ):
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                docs = self.reader.load_data(url="https://example.com/article")

        # Successful document produced via the trafilatura branch.
        self.assertEqual(len(docs), 1)
        self.assertIn("Hello main content", docs[0].text)
        # stdout / stderr must stay clean (the old code leaked debug prints).
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), "")

    def test_fallback_failures_are_logged_not_swallowed(self):
        # The fallback path must be exercised by *forcing* trafilatura and
        # readability to fail (not by assuming they are absent). bs4 is the
        # last-resort extractor and must still produce a document, and each
        # upstream failure must be logged with the URL + exception context.
        trafilatura = _fake_trafilatura(extract_side_effect=RuntimeError("simulated trafilatura crash"))
        with (
            _ModuleGuard(trafilatura=trafilatura, readability=_fake_readability_failing(), bs4=_fake_bs4(), lxml=None),
            patch.object(WebPageReader, "_fetch_html", return_value=HTML),
        ):
            docs = self.reader.load_data(url="https://example.com/article")

        messages = [self.handler.format(r) for r in self.handler.records]
        # bs4 is the last-resort extractor that produced the document.
        self.assertEqual(docs[0].metadata.get("extractor"), "bs4")
        # trafilatura's failure must be logged, naming the URL.
        self.assertTrue(
            any("trafilatura" in m and "example.com" in m for m in messages),
            f"expected a trafilatura fallback log mentioning the URL, got: {messages}",
        )
        # readability's failure must be logged too (the chain has two hops).
        self.assertTrue(
            any("readability" in m and "example.com" in m for m in messages),
            f"expected a readability fallback log mentioning the URL, got: {messages}",
        )
        # Logged records must carry exception context so operators can tell
        # *why* a fallback was selected (dependency missing vs parse/TLS error).
        self.assertTrue(any(r.exc_info for r in self.handler.records))

    def test_empty_trafilatura_result_falls_through_silently(self):
        # When trafilatura succeeds but returns no content, the reader must
        # fall through to the next extractor without an exception log (only a
        # "returned no content" debug line).
        trafilatura = _fake_trafilatura(extract_return="")
        with (
            _ModuleGuard(trafilatura=trafilatura, readability=_fake_readability_failing(), bs4=_fake_bs4(), lxml=None),
            patch.object(WebPageReader, "_fetch_html", return_value=HTML),
        ):
            docs = self.reader.load_data(url="https://example.com/article")
        # Still produced a document via the bs4 fallback.
        self.assertEqual(docs[0].metadata.get("extractor"), "bs4")
        messages = [self.handler.format(r) for r in self.handler.records]
        self.assertTrue(any("no content" in m for m in messages), f"expected a 'no content' log, got: {messages}")

    def test_missing_all_extractors_raises(self):
        # When every extractor is unavailable the reader must raise rather than
        # silently return empty content. We force ImportError on all three.
        real_import = builtins.__import__

        def _block_extractors(name, *args, **kwargs):
            if name in _OPTIONAL_READER_MODULES:
                raise ImportError(f"blocked {name}")
            return real_import(name, *args, **kwargs)

        with (
            _ModuleGuard(trafilatura=None, readability=None, bs4=None, lxml=None),
            patch.object(WebPageReader, "_fetch_html", return_value=HTML),
            patch("builtins.__import__", side_effect=_block_extractors),
        ):
            with self.assertRaises(RuntimeError) as ctx:
                self.reader.load_data(url="https://example.com/article")
        self.assertIn("extractors", str(ctx.exception))


def _fake_readability_failing():
    # readability.Document(html).summary(...) raises so the reader falls
    # through to bs4.
    class _FailingDoc:
        def __init__(self, html):
            raise RuntimeError("simulated readability crash")

    return _stub_module("readability", Document=_FailingDoc)


if __name__ == "__main__":
    unittest.main()
