# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/7/5
# @FileName: cloud_doc_reader.py
"""CloudDocReader – unified entry point for all cloud document platforms.

Automatically detects the platform from the URL and routes to the
appropriate platform-specific Reader.
"""
import logging
from typing import List, Optional, Dict
from urllib.parse import urlparse

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.agent.action.knowledge.reader.reader_errors import ReaderLoadError
from agentuniverse.agent.action.knowledge.store.document import Document

logger = logging.getLogger(__name__)

# Module-level platform map (not a Pydantic class attribute
# to avoid Pydantic v2 metaclass stripping mutable defaults).
_platform_map: Dict[str, str] = {
    "feishu.cn": "default_feishu_reader",
    "yuque.com": "default_yuque_reader",
    "notion.so": "default_notion_reader",
    "confluence": "default_confluence_reader",
    "docs.google.com": "default_google_docs_reader",
}


class CloudDocReader(Reader):
    """Unified cloud document reader with automatic platform detection.

    Routes a URL to the appropriate platform-specific Reader based on
    domain matching. Supports extensible platform registration via
    module-level functions and class methods.

    Supported platforms (built-in):
        - Feishu (feishu.cn)
        - Yuque (yuque.com)
        - Notion (notion.so)
        - Confluence (atlassian.net / custom domains with 'confluence')
        - Google Docs (docs.google.com)

    Usage:
        reader = CloudDocReader()
        docs = reader.load_data(url="https://www.feishu.cn/docx/ABC123")
    """

    @classmethod
    def register_platform(cls, domain_pattern: str, reader_name: str) -> None:
        """Register a new cloud platform for automatic detection.

        Args:
            domain_pattern: Case-insensitive substring to match in the URL domain
                            (e.g. 'shimo.im' for Shimo Docs).
            reader_name: The registered name of the Reader instance in ReaderManager
                         (e.g. 'default_shimo_reader').
        """
        _platform_map[domain_pattern.lower()] = reader_name
        logger.info("CloudDocReader registered platform: %s -> %s", domain_pattern, reader_name)

    @classmethod
    def unregister_platform(cls, domain_pattern: str) -> None:
        """Remove a platform from the detection map."""
        _platform_map.pop(domain_pattern.lower(), None)
        logger.info("CloudDocReader unregistered platform: %s", domain_pattern)

    @classmethod
    def get_platform_map(cls) -> Dict[str, str]:
        """Return a copy of the current platform map."""
        return dict(_platform_map)

    def _load_data(self, url: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Load document from a cloud platform URL with automatic routing.

        Args:
            url: Full URL of the cloud document.
            ext_info: Optional dict with platform-specific parameters
                      (tokens, credentials, cookies, etc.).

        Returns:
            List[Document]: Documents extracted by the platform-specific reader.

        Raises:
            ReaderLoadError: If the platform cannot be detected or the
                             platform reader is not registered.
        """
        if not isinstance(url, str) or not url:
            raise ReaderLoadError(
                "CloudDocReader requires a non-empty url string",
                reader_name="CloudDocReader",
            )

        platform = self._detect_platform(url)
        reader_name = _platform_map.get(platform)
        if not reader_name:
            raise ReaderLoadError(
                f"No cloud reader registered for platform '{platform}' from url={url}. "
                f"Registered platforms: {list(_platform_map.keys())}",
                reader_name="CloudDocReader",
                source=url,
            )

        logger.info("CloudDocReader routing url=%s to reader=%s (platform=%s)", url, reader_name, platform)

        reader = ReaderManager().get_instance_obj(reader_name)
        if reader is None:
            raise ReaderLoadError(
                f"Platform reader '{reader_name}' is not registered in ReaderManager. "
                f"Ensure the corresponding YAML config exists.",
                reader_name="CloudDocReader",
                source=url,
            )

        return reader.load_data(url=url, ext_info=ext_info)

    @staticmethod
    def _detect_platform(url: str) -> str:
        """Detect the cloud platform from a URL by domain matching.

        Args:
            url: The document URL.

        Returns:
            str: The matched platform key, or empty string if no match.
        """
        try:
            domain = urlparse(url).netloc.lower()
        except Exception:
            return ""

        # Check all registered platform patterns against the domain
        for pattern in _platform_map:
            if pattern in domain:
                return pattern

        return ""
