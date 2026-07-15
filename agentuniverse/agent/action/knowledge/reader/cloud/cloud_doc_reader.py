# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/7/15
# @FileName: cloud_doc_reader.py
"""Unified entry point for cloud document readers.

CloudDocReader auto-detects the cloud platform from a URL and
delegates to the appropriate platform-specific Reader (Feishu,
Yuque, Notion, Confluence, or Google Docs).

Platform routing is driven by a module-level ``_platform_map`` so
that the map can be extended at runtime without triggering Pydantic
v2 metaclass issues with mutable defaults.
"""

from typing import Dict, List, Optional
from urllib.parse import urlparse

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderLoadError,
)
from agentuniverse.agent.action.knowledge.store.document import Document

# ---------------------------------------------------------------------------
# Module-level platform map (avoids Pydantic v2 metaclass stripping)
# ---------------------------------------------------------------------------
# Keys are domain substrings to match against the URL hostname.
# Values are the *registered reader names* used by ReaderManager.
_platform_map: Dict[str, str] = {
    "feishu.cn": "default_feishu_reader",
    "yuque.com": "default_yuque_reader",
    "notion.so": "default_notion_reader",
    "confluence": "default_confluence_reader",
    "docs.google.com": "default_google_docs_reader",
}


def register_platform(domain: str, reader_name: str) -> None:
    """Register or override a platform mapping at runtime.

    Args:
        domain: Substring to match in URL hostname (e.g. ``"feishu.cn"``).
        reader_name: Registered reader name in ReaderManager.
    """
    _platform_map[domain] = reader_name


def unregister_platform(domain: str) -> None:
    """Remove a previously registered platform mapping."""
    _platform_map.pop(domain, None)


def get_platform_map() -> Dict[str, str]:
    """Return a shallow copy of the current platform map."""
    return dict(_platform_map)


class CloudDocReader(Reader):
    """Unified cloud document reader that routes by URL domain.

    Given a cloud document URL, CloudDocReader inspects the hostname,
    matches it against the platform map, and delegates to the
    corresponding platform-specific Reader instance.

    Example::

        reader = CloudDocReader()
        docs = reader.load_data("https://www.feishu.cn/docx/xxxxx")
        # internally delegates to FeishuReader
    """

    def _detect_platform(self, url: str) -> Optional[str]:
        """Return the reader name for *url*, or ``None`` if unmatched.

        The detection walks the ``_platform_map`` and returns the first
        entry whose domain key appears as a substring of the URL
        hostname.
        """
        try:
            hostname = urlparse(url).hostname or ""
        except Exception:
            return None

        hostname = hostname.lower()
        for domain_key, reader_name in _platform_map.items():
            if domain_key in hostname:
                return reader_name
        return None

    def _load_data(self, url: str, ext_info: Optional[dict] = None) -> List[Document]:
        """Load data from a cloud document URL.

        Args:
            url: Cloud document URL (Feishu, Yuque, Notion, Confluence,
                 or Google Docs).
            ext_info: Optional dict forwarded to the platform reader.

        Returns:
            List of :class:`Document` objects.

        Raises:
            ReaderLoadError: If *url* is empty, the platform cannot be
                detected, or the platform reader is not registered.
        """
        if not url:
            raise ReaderLoadError(
                "URL is required for CloudDocReader",
                reader_name=self.name or "CloudDocReader",
            )

        reader_name = self._detect_platform(url)
        if not reader_name:
            raise ReaderLoadError(
                f"Unsupported cloud document URL: {url}",
                reader_name=self.name or "CloudDocReader",
                source=url,
            )

        # Lazy import to avoid circular dependency
        from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager

        mgr = ReaderManager()
        reader = mgr.get_instance_obj(reader_name)
        if reader is None:
            raise ReaderLoadError(
                f"Reader '{reader_name}' is not registered; "
                f"ensure the corresponding YAML is loaded",
                reader_name=self.name or "CloudDocReader",
                source=url,
            )

        return reader.load_data(url, ext_info=ext_info)