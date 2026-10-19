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


if __name__ == "__main__":
    unittest.main()
