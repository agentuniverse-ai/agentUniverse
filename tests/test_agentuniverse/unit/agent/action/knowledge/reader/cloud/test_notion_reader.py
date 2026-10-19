#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.agent.action.knowledge.reader.cloud.notion_reader import NotionReader


class TestNotionReader(unittest.TestCase):
    def test_public_metadata_filters_token_fields(self):
        metadata = NotionReader._public_metadata({
            "NOTION_TOKEN": "secret",
            "notion_token": "secret-2",
            "token": "secret-3",
            "source_name": "notion",
        })

        self.assertEqual(metadata, {"source_name": "notion"})

    def test_public_metadata_keeps_non_secret_fields(self):
        metadata = NotionReader._public_metadata({
            "workspace": "team-space",
            "page_title": "Roadmap",
        })

        self.assertEqual(
            metadata,
            {"workspace": "team-space", "page_title": "Roadmap"},
        )


if __name__ == "__main__":
    unittest.main()
