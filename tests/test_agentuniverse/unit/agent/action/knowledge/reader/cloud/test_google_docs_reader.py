#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.agent.action.knowledge.reader.cloud.google_docs_reader import GoogleDocsReader


class FakeGoogleDocsReader(GoogleDocsReader):
    """Fake GoogleDocsReader subclass stubbing out network/service helpers."""

    def _build_drive_service(self, ext_info):
        """Return a stub drive service object instead of building a real one."""
        return object()

    def _export_html(self, drive, file_id: str) -> str:
        """Return canned HTML for the given file id without calling Drive."""
        return "<html><body>Hello</body></html>"

    def _html_to_text(self, html: str) -> str:
        """Convert the given HTML string to plain text (canned for tests)."""
        return "Hello"


class TestGoogleDocsReader(unittest.TestCase):
    """Tests for GoogleDocsReader metadata sanitization."""

    def test_service_account_path_is_not_copied_to_metadata(self):
        """Load data must not leak the service account JSON path into metadata."""
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
        """_public_metadata strips known secret keys such as credentials."""
        metadata = GoogleDocsReader._public_metadata({
            "service_account_json": "secret.json",
            "credentials": "secret",
            "source_name": "docs",
        })

        self.assertEqual(metadata, {"source_name": "docs"})


if __name__ == "__main__":
    unittest.main()
