#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import io
import unittest
from contextlib import redirect_stdout

from agentuniverse.agent.action.knowledge.reader.cloud.google_docs_reader import GoogleDocsReader


class FakeGoogleDocsReader(GoogleDocsReader):
    def _build_drive_service(self, ext_info):
        return object()

    def _export_html(self, drive, file_id: str) -> str:
        return "<html><body>Hello</body></html>"

    def _html_to_text(self, html: str) -> str:
        return "Hello"


class TestGoogleDocsReader(unittest.TestCase):
    def test_service_account_path_is_not_copied_to_metadata(self):
        reader = FakeGoogleDocsReader()

        docs = reader._load_data(
            "doc-1",
            ext_info={
                "GOOGLE_SERVICE_ACCOUNT_JSON": "/tmp/service-account.json",
                "project": "demo",
            },
        )

        metadata = docs[0].metadata
        self.assertEqual(metadata["project"], "demo")
        self.assertNotIn("GOOGLE_SERVICE_ACCOUNT_JSON", metadata)

    def test_public_metadata_filters_known_secret_keys(self):
        metadata = GoogleDocsReader._public_metadata({
            "service_account_json": "secret.json",
            "credentials": "secret",
            "source_name": "docs",
        })

        self.assertEqual(metadata, {"source_name": "docs"})

    def test_load_data_does_not_print_debug_output(self):
        reader = FakeGoogleDocsReader()
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            docs = reader._load_data("doc-1", ext_info={"project": "demo"})

        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(docs[0].text, "Hello")


if __name__ == "__main__":
    unittest.main()
