#!/usr/bin/env python3
"""Version-stable Chroma client construction helpers."""

# Public helpers intentionally use concise built-in validation exceptions.
# ruff: noqa: TRY003

import re
from typing import Any
from urllib.parse import urlparse


def create_chroma_client(persist_path: str | None, *, anonymized_telemetry: bool = False) -> Any:
    """Create a current Chroma HTTP or persistent client.

    This uses the public ``HttpClient`` and ``PersistentClient`` constructors
    available in Chroma 1.x rather than configuring its internal FastAPI class.
    """
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError as exc:
        raise ImportError("chromadb is required; install it with: pip install chromadb") from exc

    settings = Settings(anonymized_telemetry=anonymized_telemetry)
    value = persist_path or "./chroma"
    # ``urlparse`` treats the drive prefix in ``C:\\data`` as a URI scheme.
    # Recognize Windows drive and UNC paths before URL parsing so the same
    # configuration remains portable across supported operating systems.
    if re.match(r"^[A-Za-z]:[\\/]", value) or value.startswith("\\\\"):
        return chromadb.PersistentClient(path=value, settings=settings)
    parsed = urlparse(value)
    if parsed.scheme.lower() in {"http", "https"}:
        if not parsed.hostname:
            raise ValueError(f"invalid Chroma server URL: {value}")
        if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
            raise ValueError("Chroma server URL must not contain a path, query, or fragment")
        return chromadb.HttpClient(
            host=parsed.hostname,
            port=parsed.port or (443 if parsed.scheme.lower() == "https" else 8000),
            ssl=parsed.scheme.lower() == "https",
            settings=settings,
        )
    if parsed.scheme:
        raise ValueError("persist_path must be a local path or an http(s) URL")
    return chromadb.PersistentClient(path=value, settings=settings)
