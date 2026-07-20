#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import io
import sys
import types
import unittest
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

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

    def test_load_data_does_not_print_debug_output(self):
        fake_client = MagicMock()
        fake_client.pages.retrieve.return_value = {"id": "page-id"}

        notion_module = types.ModuleType("notion_client")
        notion_module.Client = MagicMock(return_value=fake_client)

        reader = NotionReader()
        stdout = io.StringIO()

        with patch.dict(sys.modules, {"notion_client": notion_module}), \
                patch.object(reader, "_export_page", return_value=["content"]), \
                redirect_stdout(stdout):
            documents = reader._load_data(
                "page-id",
                ext_info={"NOTION_TOKEN": "token"}
            )

        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(documents[0].text, "content")
        self.assertEqual(documents[0].metadata["type"], "page")


if __name__ == "__main__":
    unittest.main()
