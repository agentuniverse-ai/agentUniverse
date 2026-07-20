# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: test_yuque_reader.py

"""
Unit tests for YuqueReader robustness.

The HTTP layer (``self.session``) is stubbed, so the suite is deterministic and
runs without a network connection. The cases cover the previously unguarded
paths: a non-JSON document response body, a non-200 status, and a decoded book
payload that does not carry the expected ``book`` structure (which used to raise
KeyError inside the read loop).
"""

import json
import unittest
import urllib.parse
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.reader.cloud_file_reader.yuque_reader import YuqueReader

_LOGGER = "agentuniverse.agent.action.knowledge.reader.cloud_file_reader.yuque_reader"


def _encode_docs(docs_obj) -> str:
    """Build the script payload text _load_data scrapes the book json from."""
    encoded = urllib.parse.quote(json.dumps(docs_obj))
    return f'JSON.parse(decodeURIComponent("{encoded}"));'


class YuqueReaderTest(unittest.TestCase):

    def _reader(self) -> YuqueReader:
        reader = YuqueReader(cookies=None)
        reader.session = MagicMock()
        return reader

    @staticmethod
    def _title_response(title: str = "Book") -> MagicMock:
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        resp.text = f"<html><head><title>{title}</title></head></html>"
        return resp

    def test_fetch_page_markdown_returns_empty_on_non_json(self) -> None:
        reader = self._reader()
        resp = MagicMock()
        resp.status_code = 200
        resp.json.side_effect = ValueError("not json")
        reader.session.get.return_value = resp
        with self.assertLogs(_LOGGER, level="WARNING") as cm:
            self.assertEqual(reader._fetch_page_markdown("123", "abc"), "")
        # The failure is observable and carries the book/slug context.
        self.assertTrue(any("book_id=123" in m and "slug=abc" in m
                            for m in cm.output))

    def test_fetch_page_markdown_returns_empty_on_non_200(self) -> None:
        reader = self._reader()
        resp = MagicMock()
        resp.status_code = 500
        reader.session.get.return_value = resp
        with self.assertLogs(_LOGGER, level="WARNING"):
            self.assertEqual(reader._fetch_page_markdown("123", "abc"), "")

    def test_fetch_page_markdown_returns_empty_on_non_dict_json(self) -> None:
        # A valid JSON list/string used to crash at .get('data'); it now logs
        # and is skipped like other unusable bodies.
        reader = self._reader()
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = ["not", "an", "object"]
        reader.session.get.return_value = resp
        with self.assertLogs(_LOGGER, level="WARNING"):
            self.assertEqual(reader._fetch_page_markdown("123", "abc"), "")

    def test_fetch_page_markdown_extracts_sourcecode(self) -> None:
        reader = self._reader()
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"data": {"sourcecode": "# Hello world"}}
        reader.session.get.return_value = resp
        self.assertIn("# Hello world", reader._fetch_page_markdown("1", "s"))

    def test_load_data_raises_when_book_key_missing(self) -> None:
        reader = self._reader()
        book_resp = MagicMock()
        book_resp.raise_for_status.return_value = None
        book_resp.text = _encode_docs({"meta": "no book here"})
        reader.session.get.return_value = book_resp
        with self.assertRaises(RuntimeError) as ctx:
            reader._load_data("https://www.yuque.com/x/y")
        self.assertIn("yuque.com/x/y", str(ctx.exception))

    def test_load_data_raises_when_book_not_dict(self) -> None:
        reader = self._reader()
        book_resp = MagicMock()
        book_resp.raise_for_status.return_value = None
        book_resp.text = _encode_docs({"book": "wrong-type"})
        reader.session.get.return_value = book_resp
        with self.assertRaises(RuntimeError):
            reader._load_data("https://www.yuque.com/x/y")

    def test_load_data_raises_when_book_id_missing(self) -> None:
        reader = self._reader()
        book_resp = MagicMock()
        book_resp.raise_for_status.return_value = None
        book_resp.text = _encode_docs({"book": {"toc": []}})  # no id
        reader.session.get.return_value = book_resp
        with self.assertRaises(RuntimeError) as ctx:
            reader._load_data("https://www.yuque.com/x/y")
        self.assertIn("no id", str(ctx.exception))

    def test_load_data_raises_on_non_dict_payload(self) -> None:
        reader = self._reader()
        book_resp = MagicMock()
        book_resp.raise_for_status.return_value = None
        book_resp.text = _encode_docs(["a", "list", "not", "an", "object"])
        reader.session.get.return_value = book_resp
        with self.assertRaises(RuntimeError):
            reader._load_data("https://www.yuque.com/x/y")

    def test_load_data_skips_toc_entry_missing_url(self) -> None:
        # A toc entry with the right title but no 'url' is logged and skipped
        # rather than passed to the page fetch as None.
        reader = self._reader()
        book_resp = MagicMock()
        book_resp.raise_for_status.return_value = None
        book_resp.text = _encode_docs(
            {"book": {"id": 42, "toc": [{"title": "Book"}]}})  # no url
        reader.session.get.side_effect = [book_resp, self._title_response("Book")]
        with self.assertLogs(_LOGGER, level="WARNING") as cm:
            docs = reader._load_data("https://www.yuque.com/x/y")
        self.assertEqual(docs, [])
        self.assertTrue(any("missing 'url'" in m for m in cm.output))

    def test_load_data_returns_documents_on_happy_path(self) -> None:
        reader = self._reader()
        book_resp = MagicMock()
        book_resp.raise_for_status.return_value = None
        book_resp.text = _encode_docs(
            {"book": {"id": 42, "toc": [{"title": "Book", "url": "doc-slug"}]}})
        page_resp = MagicMock()
        page_resp.status_code = 200
        page_resp.json.return_value = {"data": {"sourcecode": "# Body"}}
        reader.session.get.side_effect = [
            book_resp, self._title_response("Book"), page_resp]
        with patch("time.sleep"):
            docs = reader._load_data("https://www.yuque.com/x/y")
        self.assertEqual(len(docs), 1)
        self.assertIn("# Body", docs[0].text)
        self.assertEqual(docs[0].metadata["doc_title"], "Book")


if __name__ == "__main__":
    unittest.main()
