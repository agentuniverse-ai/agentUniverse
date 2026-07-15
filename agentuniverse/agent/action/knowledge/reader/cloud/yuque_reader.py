# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/7/15
# @FileName: yuque_reader.py
"""Yuque document reader.

Migrated from ``cloud_file_reader/`` to ``cloud/`` with:
- Semantic exception hierarchy (``ReaderDependencyError``,
  ``ReaderLoadError``)
- Structured logging via ``logging`` module (replaces ``print``)
- Proper ``Reader`` base class inheritance preserved
"""

import json
import logging
import random
import re
import time
import urllib.parse
from typing import Any, List, Optional

from pydantic import ConfigDict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderDependencyError,
    ReaderLoadError,
)
from agentuniverse.agent.action.knowledge.store.document import Document

logger = logging.getLogger(__name__)


class YuqueReader(Reader):
    """Reader for Yuque knowledge-base documents.

    Fetches all documents in a Yuque book and returns them as
    :class:`Document` objects with markdown source.

    Attributes:
        cookies: Optional cookies string for Yuque authentication.
        session: HTTP session with retry support.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    cookies: Optional[str] = None
    session: Optional[Any] = None

    def __init__(self, cookies: str = None, **data: Any):
        """Initialize HTTP session with retry support and optional cookies."""
        super().__init__(**data)
        self.cookies = cookies
        try:
            import requests  # type: ignore
            from requests.adapters import HTTPAdapter, Retry  # type: ignore
        except ImportError:
            raise ReaderDependencyError(
                "requests is required for YuqueReader",
                reader_name=self.name or "YuqueReader",
                dependency="requests",
                install_hint="pip install requests",
            )
        self.session = requests.Session()
        retries = Retry(
            total=5, backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _fetch_url_title(self, url: str) -> str:
        """Fetch page title and clean illegal filename characters."""
        headers = {"Cookie": self.cookies} if self.cookies else {}
        try:
            resp = self.session.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            from bs4 import BeautifulSoup  # type: ignore
            soup = BeautifulSoup(resp.text, "html.parser")
            tag = soup.title
            if not tag or not tag.string:
                return "Untitled"
            title = tag.string.strip()
            title = re.sub(r'[\\/:*?"<>|]', "-", title)
            return title.replace(" · 语雀", "")
        except Exception as exc:
            logger.debug("Failed to fetch Yuque page title for %s: %s", url, exc)
            return "Untitled"

    def _fetch_page_markdown(self, book_id: str, slug: str) -> str:
        """Fetch markdown source for a single Yuque document."""
        headers = {"Cookie": self.cookies} if self.cookies else {}
        url = (
            f"https://www.yuque.com/api/docs/{slug}"
            f"?book_id={book_id}&merge_dynamic_data=false&mode=markdown"
        )
        try:
            resp = self.session.get(url, headers=headers, timeout=20)
            if resp.status_code != 200:
                logger.warning(
                    "Yuque document download failed (HTTP %s) for book=%s slug=%s",
                    resp.status_code, book_id, slug,
                )
                return ""
            data = resp.json().get("data", {})
            md = data.get("sourcecode", "")
        except Exception as exc:
            logger.warning(
                "Yuque API request failed for book=%s slug=%s: %s",
                book_id, slug, exc,
            )
            return ""

        # Process image references inline
        def repl(m):
            src = m.group(1)
            return f"![]({src})"

        return re.sub(r"!\[.*?\]\((.*?)\)", repl, md)

    # ------------------------------------------------------------------
    # Core loading
    # ------------------------------------------------------------------

    def _load_data(self, url: str, ext_info: Optional[dict] = None) -> List[Document]:
        """Fetch all docs in a Yuque book and return as List[Document].

        Args:
            url: Publicly accessible Yuque book URL.
            ext_info: Unused; reserved for future extensions.

        Returns:
            List of :class:`Document` objects (one per page in the book).

        Raises:
            ReaderLoadError: If *url* is empty or the book cannot be
                fetched.
            ReaderDependencyError: If ``requests`` is not installed.
        """
        if not url:
            raise ReaderLoadError(
                "URL is required for YuqueReader",
                reader_name=self.name or "YuqueReader",
            )

        headers = {"Cookie": self.cookies} if self.cookies else {}
        try:
            resp = self.session.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            encoded = re.findall(
                r'decodeURIComponent\("(.+)"\)\);', resp.text
            )[0]
            docs = json.loads(urllib.parse.unquote(encoded))
        except Exception as exc:
            raise ReaderLoadError(
                f"Failed to fetch Yuque book: {exc}",
                reader_name=self.name or "YuqueReader",
                source=url,
            )

        book_title = self._fetch_url_title(url)
        # Sanitize titles for metadata keys
        chars = '/:*?"<>|\n\r'
        trans = str.maketrans({c: "_" for c in chars})

        documents: List[Document] = []
        for item in docs["book"]["toc"]:
            if item["title"] != book_title:
                continue
            md = self._fetch_page_markdown(str(docs["book"]["id"]), item["url"])
            if not md:
                continue
            metadata = {
                "source": url,
                "doc_title": item["title"],
                "sanitized_title": item["title"].translate(trans),
            }
            documents.append(Document(text=md, metadata=metadata))
            # Respectful delay
            time.sleep(random.uniform(1, 3))
        return documents

    def __del__(self):
        """Close HTTP session."""
        try:
            if self.session is not None:
                self.session.close()
        except Exception:
            pass