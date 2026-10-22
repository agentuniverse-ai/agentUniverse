#!/usr/bin/env python3

"""Shared Chroma client construction helpers."""

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import chromadb
from chromadb.config import Settings


class ChromaClientConfigurationError(ValueError):
    """Raised when Chroma client connection settings are invalid."""

    @classmethod
    def missing_host(cls) -> "ChromaClientConfigurationError":
        """Build an error for a server URL without a host."""
        return cls("Chroma server URL must include a host")


def create_chroma_client(
    persist_path: str | Path | None = None,
    settings: Settings | None = None,
) -> Any:
    """Create an HTTP, persistent, or ephemeral Chroma client.

    Args:
        persist_path: HTTP(S) server URL, local persistence path, or ``None``
            for an in-memory client.
        settings: Optional Chroma client settings.

    Returns:
        A Chroma client configured for the requested storage mode.

    Raises:
        ValueError: If an HTTP(S) URL does not contain a host.
    """
    path_value = str(persist_path) if persist_path is not None else ""
    parsed_url = urlparse(path_value)
    if parsed_url.scheme.lower() in {"http", "https"}:
        if not parsed_url.hostname:
            raise ChromaClientConfigurationError.missing_host()
        use_ssl = parsed_url.scheme.lower() == "https"
        return chromadb.HttpClient(
            host=parsed_url.hostname,
            port=parsed_url.port or (443 if use_ssl else 8000),
            ssl=use_ssl,
            settings=settings,
        )
    if path_value:
        return chromadb.PersistentClient(path=path_value, settings=settings)
    return chromadb.EphemeralClient(settings=settings)
