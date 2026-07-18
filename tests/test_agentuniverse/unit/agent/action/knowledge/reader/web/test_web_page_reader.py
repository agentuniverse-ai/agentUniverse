#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.web.web_page_reader import WebPageReader


class FakeWebPageReader(WebPageReader):
    def _fetch_html(self, url: str) -> str:
        return "<html><body>Hello</body></html>"

    def _extract_main_text(self, html: str, url: str):
        return "Hello", {"extractor": "fake"}


class TestWebPageReader(unittest.TestCase):
    def test_load_data_does_not_print_debug_output(self):
        reader = FakeWebPageReader()

        with patch("builtins.print") as print_mock:
            docs = reader._load_data("https://example.com")

        print_mock.assert_not_called()
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].text, "Hello")
        self.assertEqual(docs[0].metadata["url"], "https://example.com")
        self.assertEqual(docs[0].metadata["extractor"], "fake")


if __name__ == "__main__":
    unittest.main()
