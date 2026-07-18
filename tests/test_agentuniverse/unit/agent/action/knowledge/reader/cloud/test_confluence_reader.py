#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.agent.action.knowledge.reader.cloud.confluence_reader import ConfluenceReader


class TestConfluenceReader(unittest.TestCase):
    def test_public_metadata_filters_token_fields(self):
        metadata = ConfluenceReader._public_metadata({
            "token": "secret",
            "password": "secret-2",
            "CONFLUENCE_TOKEN": "secret-3",
            "site_url": "https://example.atlassian.net",
        })

        self.assertEqual(metadata, {"site_url": "https://example.atlassian.net"})

    def test_public_metadata_keeps_non_secret_fields(self):
        metadata = ConfluenceReader._public_metadata({
            "space": "ENG",
            "label": "design",
        })

        self.assertEqual(metadata, {"space": "ENG", "label": "design"})


if __name__ == "__main__":
    unittest.main()
