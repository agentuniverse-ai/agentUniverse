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
from unittest.mock import MagicMock

from agentuniverse.agent.action.knowledge.reader.cloud_file_reader.yuque_reader import YuqueReader


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
        self.assertEqual(reader._fetch_page_markdown("123", "abc"), "")

    def test_fetch_page_markdown_returns_empty_on_non_200(self) -> None:
        reader = self._reader()
        resp = MagicMock()
        resp.status_code = 500
        reader.session.get.return_value = resp
        self.assertEqual(reader._fetch_page_markdown("123", "abc"), "")

    def test_load_data_returns_empty_when_book_key_missing(self) -> None:
        reader = self._reader()
        book_resp = MagicMock()
        book_resp.raise_for_status.return_value = None
        book_resp.text = _encode_docs({"meta": "no book here"})
        reader.session.get.side_effect = [book_resp, self._title_response()]
        self.assertEqual(reader._load_data("https://www.yuque.com/x/y"), [])

    def test_load_data_returns_empty_when_book_not_dict(self) -> None:
        reader = self._reader()
        book_resp = MagicMock()
        book_resp.raise_for_status.return_value = None
        book_resp.text = _encode_docs({"book": "wrong-type"})
        reader.session.get.side_effect = [book_resp, self._title_response()]
        self.assertEqual(reader._load_data("https://www.yuque.com/x/y"), [])


if __name__ == "__main__":
    unittest.main()
