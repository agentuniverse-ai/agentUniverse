# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: confluence_reader.py
import logging
import os
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderLoadError,
    ReaderDependencyError,
    ReaderConfigError,
)
from agentuniverse.agent.action.knowledge.store.document import Document

logger = logging.getLogger(__name__)


class ConfluenceReader(Reader):
    """Reader for Atlassian Confluence pages.

    Requires:
        pip install atlassian-python-api
    Credentials:
        site_url, username, token must be provided via ext_info or env.
    """

    def _load_data(self, page_id: str, ext_info: Optional[Dict] = None) -> List[Document]:
        logger.info("ConfluenceReader start load page_id=%s", page_id)
        if not page_id:
            raise ReaderLoadError(
                "ConfluenceReader requires page_id",
                reader_name="ConfluenceReader",
            )

        site_url, username, token = self._resolve_cred(ext_info)
        try:
            from atlassian import Confluence  # type: ignore
        except Exception:
            raise ReaderDependencyError(
                "atlassian-python-api is required for ConfluenceReader",
                reader_name="ConfluenceReader",
                dependency="atlassian-python-api",
                install_hint="pip install agentuniverse[cloud]",
            )

        conf = Confluence(url=site_url, username=username, password=token, cloud=True)
        page = conf.get_page_by_id(page_id, expand="body.view,version,metadata.labels")
        html = page.get("body", {}).get("view", {}).get("value", "")

        text = self._html_to_text(html)
        logger.info("ConfluenceReader extracted text length=%d from page_id=%s", len(text), page_id)
        metadata: Dict = {
            "source": "confluence",
            "page_id": page_id,
            "title": page.get("title"),
            "version": page.get("version", {}).get("number")
        }
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text, metadata=metadata)]

    def _resolve_cred(self, ext_info: Optional[Dict]) -> (str, str, str):
        site_url = (ext_info or {}).get("site_url") or os.environ.get("CONFLUENCE_URL")
        username = (ext_info or {}).get("username") or os.environ.get("CONFLUENCE_USERNAME")
        token = (ext_info or {}).get("token") or os.environ.get("CONFLUENCE_TOKEN")
        if not site_url or not username or not token:
            raise ReaderConfigError(
                "Confluence credentials required: site_url, username, token",
                reader_name="ConfluenceReader",
                config_key="CONFLUENCE_URL/CONFLUENCE_USERNAME/CONFLUENCE_TOKEN",
            )
        return site_url, username, token

    def _html_to_text(self, html: str) -> str:
        try:
            from bs4 import BeautifulSoup  # type: ignore
        except Exception:
            raise ReaderDependencyError(
                "beautifulsoup4 and lxml are required for ConfluenceReader",
                reader_name="ConfluenceReader",
                dependency="beautifulsoup4[lxml]",
                install_hint="pip install beautifulsoup4 lxml",
            )
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        text = soup.get_text("\n")
        return "\n".join([line.strip() for line in text.splitlines() if line.strip()])
