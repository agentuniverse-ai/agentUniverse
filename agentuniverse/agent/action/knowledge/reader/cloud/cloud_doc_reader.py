# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @FileName: cloud_doc_reader.py
"""Unified cloud document reader with automatic domain-based routing.

``CloudDocReader`` inspects a target URL and dispatches the read request to the
appropriate concrete cloud reader (Feishu, Yuque, Notion, Confluence or Google
Docs). New cloud platforms can be registered dynamically through
:meth:`CloudDocReader.register_platform`.
"""
from typing import Dict, List, Optional
from urllib.parse import urlparse

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderConfigError,
    ReaderDependencyError,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.util.logging.logging_util import LOGGER

# Reuse the canonical domain -> reader mapping maintained by the ReaderManager
# so that routing rules have a single source of truth.
from agentuniverse.agent.action.knowledge.reader.reader_manager import URL_PATTERN_MAP


def _match_reader_name(url: str) -> Optional[str]:
    """Return the registered reader component name for the given url.

    Args:
        url (str): The cloud document url.

    Returns:
        Optional[str]: The matched reader component name, or ``None``.
    """
    if not url:
        return None
    netloc = urlparse(url).netloc.lower()
    host = netloc.split(":")[0] if netloc else url.lower()
    for pattern, reader_name in URL_PATTERN_MAP.items():
        if pattern in host:
            return reader_name
    return None


def get_url_default_reader(url: str) -> Optional[Reader]:
    """Resolve the default cloud reader instance for a url.

    Delegates to the :class:`ReaderManager` so the resolved reader is consistent
    with the rest of the reader subsystem.

    Args:
        url (str): The cloud document url.

    Returns:
        Optional[Reader]: A reader instance, or ``None`` if no platform matches.
    """
    from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
    return ReaderManager().get_url_default_reader(url)


class CloudDocReader(Reader):
    """Unified entry point for cloud document reading with auto-routing.

    ``CloudDocReader`` inspects the supplied URL, selects the matching cloud
    reader via :data:`URL_PATTERN_MAP` and delegates ``load_data`` to it. New
    cloud platforms can be plugged in at runtime through
    :meth:`register_platform`.
    """

    def _load_data(self, url: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Auto-route a cloud document url to the matching reader.

        Args:
            url (str): The cloud document url.
            ext_info (Optional[Dict]): Optional runtime configuration forwarded
                to the underlying reader.

        Returns:
            List[Document]: Documents produced by the dispatched reader.

        Raises:
            ReaderConfigError: If the url is empty or no platform matches.
            ReaderDependencyError: If the resolved reader cannot be loaded.
        """
        if not url:
            raise ReaderConfigError(
                "CloudDocReader requires a valid cloud document url",
                reader_name=self.__class__.__name__,
            )
        reader_name = _match_reader_name(url)
        if not reader_name:
            raise ReaderConfigError(
                f"No cloud reader registered for url: {url}",
                reader_name=self.__class__.__name__,
            )

        reader = self._get_reader(reader_name)
        if reader is None:
            raise ReaderDependencyError(
                f"Cloud reader '{reader_name}' is not available",
                reader_name=self.__class__.__name__,
            )
        LOGGER.debug(f"CloudDocReader dispatching {url} to {reader_name}")
        return reader.load_data(url, ext_info) if ext_info else reader.load_data(url)

    @staticmethod
    def _get_reader(reader_name: str) -> Optional[Reader]:
        """Retrieve a reader instance from the ``ReaderManager`` by name."""
        try:
            from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
            return ReaderManager().get_instance_obj(reader_name)
        except Exception as e:
            LOGGER.warning(f"CloudDocReader failed to load reader '{reader_name}': {e}")
            return None

    @staticmethod
    def register_platform(domain_pattern: str, reader_name: str) -> None:
        """Dynamically register a new cloud platform routing rule.

        Args:
            domain_pattern (str): Substring matched against the url host.
            reader_name (str): Registered reader component name to dispatch to.
        """
        URL_PATTERN_MAP[domain_pattern.lower()] = reader_name
        LOGGER.debug(f"CloudDocReader registered platform '{domain_pattern}' -> '{reader_name}'")

    @staticmethod
    def get_supported_platforms() -> List[str]:
        """Return the list of currently supported domain patterns."""
        return list(URL_PATTERN_MAP.keys())
