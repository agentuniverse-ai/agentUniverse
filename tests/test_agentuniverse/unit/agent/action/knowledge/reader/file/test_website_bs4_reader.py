#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.file.website_bs4_reader import WebsiteBs4Reader


class WebsiteBs4ReaderTest(unittest.TestCase):
    def test_load_data_resets_crawl_state_between_calls(self):
        url = "https://example.com"
        reader = WebsiteBs4Reader()
        reader._visited.add(url)
        reader._urls_to_crawl.append((url, 2))

        with patch.object(reader, "_crawl_website", return_value={url: "example text"}):
            docs = reader._load_data(url)

        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].text, "example text")
        self.assertEqual(reader._visited, set())
        self.assertEqual(reader._urls_to_crawl, [])

    def test_crawl_website_logs_fetch_errors_without_printing(self):
        reader = WebsiteBs4Reader(max_links=1)
        url = "https://example.com"

        with patch("agentuniverse.agent.action.knowledge.reader.file.website_bs4_reader.time.sleep"), \
                patch("agentuniverse.agent.action.knowledge.reader.file.website_bs4_reader.httpx.get",
                      side_effect=RuntimeError("boom")), \
                patch("agentuniverse.agent.action.knowledge.reader.file.website_bs4_reader.LOGGER") as mock_logger, \
                patch("builtins.print") as mock_print:
            result = reader._crawl_website(url)

        self.assertEqual(result, {})
        mock_logger.debug.assert_called_once_with(
            "WebsiteBs4Reader skipped https://example.com due to error: boom"
        )
        mock_print.assert_not_called()


if __name__ == "__main__":
    unittest.main()
