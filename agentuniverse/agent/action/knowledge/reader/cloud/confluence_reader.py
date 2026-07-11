# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: confluence_reader.py
"""Reader for Atlassian Confluence cloud pages.

The reader lazily imports the optional ``atlassian-python-api`` dependency so
that simply registering the reader does not require the package to be present.
Runtime configuration (``site_url``, ``username``, ``token``) can be supplied
through ``ext_info`` or the standard ``CONFLUENCE_*`` environment variables.
"""
import os
from typing import Dict, List, Optional

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderConfigError,
    ReaderDependencyError,
    ReaderLoadError,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.util.logging.logging_util import LOGGER


class ConfluenceReader(Reader):
    """Reader for Atlassian Confluence pages.

    Requires:
        pip install atlassian-python-api
    Credentials:
        site_url, username, token must be provided via ext_info or env.
    """

    def _load_data(self, page_id: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Load a Confluence page by id and return it as a Document.

        Args:
            page_id (str): The Confluence page id.
            ext_info (Optional[Dict]): Optional runtime configuration, supports:
                - site_url (str): Confluence base url.
                - username (str): Confluence username.
                - token (str): Confluence api token / password.

        Returns:
            List[Document]: Documents produced from the Confluence page.

        Raises:
            ReaderConfigError: If page_id is missing or credentials are absent.
            ReaderDependencyError: If a required optional dependency is missing.
            ReaderLoadError: If the page cannot be retrieved or parsed.
        """
        if not page_id:
            raise ReaderConfigError(
                "ConfluenceReader requires a page_id.",
                reader_name=self.__class__.__name__,
            )
        LOGGER.debug(f"ConfluenceReader start load page_id={page_id}")

        site_url, username, token = self._resolve_cred(ext_info)
        try:
            from atlassian import Confluence  # type: ignore
        except ImportError as e:
            raise ReaderDependencyError(
                "Install atlassian-python-api to use ConfluenceReader: "
                "`pip install atlassian-python-api`",
                reader_name=self.__class__.__name__,
            ) from e

        try:
            conf = Confluence(url=site_url, username=username, password=token, cloud=True)
            page = conf.get_page_by_id(page_id, expand="body.view,version,metadata.labels")
            html = page.get("body", {}).get("view", {}).get("value", "")
            text = self._html_to_text(html)
        except Exception as e:
            LOGGER.error(f"ConfluenceReader failed to load page {page_id}: {e}")
            raise ReaderLoadError(
                f"Failed to fetch Confluence page {page_id}: {e}",
                reader_name=self.__class__.__name__,
            ) from e

        metadata: Dict = {
            "source": "confluence",
            "page_id": page_id,
            "title": page.get("title"),
            "version": page.get("version", {}).get("number"),
        }
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text, metadata=metadata)]

    def _resolve_cred(self, ext_info: Optional[Dict]) -> tuple:
        """Resolve Confluence credentials from ext_info or environment.

        Args:
            ext_info (Optional[Dict]): Optional runtime configuration.

        Returns:
            tuple: The resolved (site_url, username, token).

        Raises:
            ReaderConfigError: If any required credential is missing.
        """
        site_url = (ext_info or {}).get("site_url") or os.environ.get("CONFLUENCE_URL")
        username = (ext_info or {}).get("username") or os.environ.get("CONFLUENCE_USERNAME")
        token = (ext_info or {}).get("token") or os.environ.get("CONFLUENCE_TOKEN")
        if not site_url or not username or not token:
            raise ReaderConfigError(
                "Confluence credentials required: provide site_url, username and token "
                "via ext_info or the CONFLUENCE_URL/CONFLUENCE_USERNAME/CONFLUENCE_TOKEN env vars.",
                reader_name=self.__class__.__name__,
            )
        return site_url, username, token

    def _html_to_text(self, html: str) -> str:
        """Convert Confluence html body to plain text.

        Args:
            html (str): The html body of the Confluence page.

        Returns:
            str: Cleaned plain text content.

        Raises:
            ReaderDependencyError: If beautifulsoup4/lxml is not installed.
            ReaderParseError: If the html cannot be parsed.
        """
        try:
            from bs4 import BeautifulSoup  # type: ignore
        except ImportError as e:
            raise ReaderDependencyError(
                "Install beautifulsoup4 and lxml for ConfluenceReader: "
                "`pip install beautifulsoup4 lxml`",
                reader_name=self.__class__.__name__,
            ) from e
        try:
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style", "noscript"]):
                tag.extract()
            text = soup.get_text("\n")
            return "\n".join([line.strip() for line in text.splitlines() if line.strip()])
        except Exception as e:
            raise ReaderParseError(
                f"Failed to parse Confluence html body: {e}",
                reader_name=self.__class__.__name__,
            ) from e
