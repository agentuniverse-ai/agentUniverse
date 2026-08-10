#!/usr/bin/env python3

"""Tests for shared Chroma client construction."""

import unittest
from pathlib import Path
from unittest.mock import patch

from agentuniverse.base.util.chroma_util import create_chroma_client


class ChromaClientFactoryTest(unittest.TestCase):
    """Verify each supported Chroma deployment mode."""

    @patch("agentuniverse.base.util.chroma_util.chromadb.EphemeralClient")
    def test_none_path_creates_ephemeral_client(self, ephemeral_client) -> None:
        create_chroma_client()
        ephemeral_client.assert_called_once_with(settings=None)

    @patch("agentuniverse.base.util.chroma_util.chromadb.PersistentClient")
    def test_local_path_creates_persistent_client(self, persistent_client) -> None:
        path = Path("chroma-data")
        create_chroma_client(path)
        persistent_client.assert_called_once_with(path=str(path), settings=None)

    @patch("agentuniverse.base.util.chroma_util.chromadb.HttpClient")
    def test_https_url_enables_ssl_and_default_port(self, http_client) -> None:
        create_chroma_client("https://chroma.example.com")
        http_client.assert_called_once_with(
            host="chroma.example.com",
            port=443,
            ssl=True,
            settings=None,
        )

    @patch("agentuniverse.base.util.chroma_util.chromadb.HttpClient")
    def test_http_url_preserves_explicit_port(self, http_client) -> None:
        create_chroma_client("http://localhost:9000")
        http_client.assert_called_once_with(
            host="localhost",
            port=9000,
            ssl=False,
            settings=None,
        )

    def test_server_url_requires_host(self) -> None:
        with self.assertRaisesRegex(ValueError, "must include a host"):
            create_chroma_client("https:///missing-host")


if __name__ == "__main__":
    unittest.main()
