# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_web_page_reader.py
"""Unit tests for WebPageReader (offline: fetchers/extractors are faked)."""

import sys
import types

import pytest

from agentuniverse.agent.action.knowledge.reader.web.web_page_reader import WebPageReader


class _FakeResponse:
    """Minimal stand-in for an HTTP response object."""

    def __init__(self, text="", status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP error {self.status_code}")


def _fake_httpx(fail_on_init=False, response=None):
    """Return a fake httpx module whose Client records usage without a network."""
    module = types.ModuleType("httpx")
    module.calls = []

    class _Client:
        def __init__(self, **kwargs):
            module.calls.append(dict(kwargs))
            if fail_on_init:
                raise RuntimeError("httpx unavailable")

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def get(self, url, follow_redirects=None):
            module.calls[-1].update(url=url, follow_redirects=follow_redirects)
            return response

    module.Client = _Client
    return module


def _fake_requests(fail=False, response=None):
    """Return a fake requests module whose get() records usage without a network."""
    module = types.ModuleType("requests")
    module.calls = []

    def get(url, timeout=None, headers=None):
        module.calls.append({"url": url, "timeout": timeout, "headers": headers})
        if fail:
            raise RuntimeError("requests unavailable")
        return response

    module.get = get
    return module


class TestWebPageReader:
    """Test WebPageReader guards, fetching and metadata shaping without HTTP."""

    @pytest.fixture
    def reader(self):
        return WebPageReader()

    @pytest.mark.parametrize("url", [None, "", 123])
    def test_load_data_requires_non_empty_string_url(self, reader, url):
        with pytest.raises(ValueError, match="requires a non-empty url string"):
            reader._load_data(url)

    def test_load_data_shapes_web_metadata(self, reader):
        reader._fetch_html = lambda url: "<html>text</html>"
        reader._extract_main_text = lambda html, url: ("Article body", {"extractor": "trafilatura"})
        docs = reader._load_data("https://example.com/article")
        assert len(docs) == 1
        assert docs[0].text == "Article body"
        assert docs[0].metadata == {
            "source": "web",
            "url": "https://example.com/article",
            "extractor": "trafilatura",
        }

    def test_load_data_merges_ext_info_into_metadata(self, reader):
        reader._fetch_html = lambda url: "<html>text</html>"
        reader._extract_main_text = lambda html, url: ("t", {"extractor": "bs4"})
        docs = reader._load_data(
            "https://example.com/x",
            ext_info={"source": "crawl", "url": "https://mirror.example.com/x", "depth": 2},
        )
        assert docs[0].metadata["source"] == "crawl"
        assert docs[0].metadata["url"] == "https://mirror.example.com/x"
        assert docs[0].metadata["depth"] == 2
        assert docs[0].metadata["extractor"] == "bs4"

    def test_fetch_html_uses_httpx_with_headers(self, reader, monkeypatch):
        fake_httpx = _fake_httpx(response=_FakeResponse(text="fetched page"))
        monkeypatch.setitem(sys.modules, "httpx", fake_httpx)
        assert reader._fetch_html("https://example.com/a") == "fetched page"
        call = fake_httpx.calls[0]
        assert call["url"] == "https://example.com/a"
        assert call["follow_redirects"] is True
        assert call["timeout"] == 20.0
        assert "agentUniverse/1.0" in call["headers"]["User-Agent"]

    def test_fetch_html_falls_back_to_requests(self, reader, monkeypatch):
        monkeypatch.setitem(sys.modules, "httpx", _fake_httpx(fail_on_init=True))
        fake_requests = _fake_requests(response=_FakeResponse(text="fallback page"))
        monkeypatch.setitem(sys.modules, "requests", fake_requests)
        assert reader._fetch_html("https://example.com/b") == "fallback page"
        assert fake_requests.calls[0]["url"] == "https://example.com/b"
        assert fake_requests.calls[0]["timeout"] == 20

    def test_fetch_html_raises_runtime_error_when_all_transports_fail(self, reader, monkeypatch):
        monkeypatch.setitem(sys.modules, "httpx", _fake_httpx(fail_on_init=True))
        monkeypatch.setitem(sys.modules, "requests", _fake_requests(fail=True))
        with pytest.raises(RuntimeError, match="Failed to fetch url: https://example.com/c"):
            reader._fetch_html("https://example.com/c")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
