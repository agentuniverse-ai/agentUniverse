# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_rendered_web_page_reader.py
"""Unit tests for RenderedWebPageReader (offline: no playwright is ever launched)."""

import sys

import pytest

from agentuniverse.agent.action.knowledge.reader.web.rendered_web_page_reader import RenderedWebPageReader
from agentuniverse.agent.action.knowledge.reader.web.web_page_reader import WebPageReader
from agentuniverse.agent.action.knowledge.store.document import Document


class TestRenderedWebPageReader:
    """Test RenderedWebPageReader guards and metadata shaping without rendering."""

    @pytest.fixture
    def reader(self):
        """Create a RenderedWebPageReader instance for testing."""
        return RenderedWebPageReader()

    @pytest.mark.parametrize("url", [None, "", 123, ["https://example.com"]])
    def test_load_data_requires_non_empty_string_url(self, reader, url):
        """A missing/non-string url raises ValueError before any rendering."""
        with pytest.raises(ValueError, match="requires a non-empty url string"):
            reader._load_data(url)

    def test_load_data_shapes_rendered_metadata(self, reader, monkeypatch):
        """The returned Document is marked rendered with source/url metadata."""
        reader._render_and_get_html = lambda url: "<html>body</html>"
        monkeypatch.setattr(
            WebPageReader,
            "_extract_main_text",
            lambda self, html, url: ("Rendered text", {}),
        )
        docs = reader._load_data("https://example.com/dynamic")
        assert len(docs) == 1
        assert isinstance(docs[0], Document)
        assert docs[0].text == "Rendered text"
        assert docs[0].metadata == {
            "source": "web",
            "url": "https://example.com/dynamic",
            "rendered": True,
        }

    def test_load_data_propagates_extractor_metadata(self, reader, monkeypatch):
        """The extractor name returned by WebPageReader is passed through."""
        reader._render_and_get_html = lambda url: "<html>body</html>"
        monkeypatch.setattr(
            WebPageReader,
            "_extract_main_text",
            lambda self, html, url: ("T", {"extractor": "readability"}),
        )
        docs = reader._load_data("https://example.com/p")
        assert docs[0].metadata["extractor"] == "readability"
        assert docs[0].metadata["rendered"] is True

    def test_load_data_merges_ext_info_into_metadata(self, reader, monkeypatch):
        """ext_info entries are merged and can override default url/source keys."""
        reader._render_and_get_html = lambda url: "<html>body</html>"
        monkeypatch.setattr(
            WebPageReader,
            "_extract_main_text",
            lambda self, html, url: ("T", {}),
        )
        docs = reader._load_data(
            "https://example.com/orig",
            ext_info={"source": "screenshot", "url": "https://example.com/new", "width": 1920},
        )
        assert docs[0].metadata["source"] == "screenshot"
        assert docs[0].metadata["url"] == "https://example.com/new"
        assert docs[0].metadata["width"] == 1920
        assert docs[0].metadata["rendered"] is True

    def test_render_and_get_html_raises_import_error_without_playwright(self, reader, monkeypatch):
        """A missing playwright import surfaces a clear ImportError, no browser launch."""
        monkeypatch.setitem(sys.modules, "playwright", None)
        with pytest.raises(ImportError, match="playwright is required"):
            reader._render_and_get_html("https://example.com/js")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
