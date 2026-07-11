# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: web_page_reader.py
"""Reader for static web pages via HTTP fetching and boilerplate removal.

Optional HTTP and extraction dependencies are imported lazily. Runtime options
such as ``timeout`` and ``user_agent`` can be supplied through ``ext_info``.

Dependencies (optional but recommended):
    - trafilatura (preferred for article extraction)
    - readability-lxml (fallback for extraction)
    - beautifulsoup4 (last-resort plain text)
    - httpx or requests
"""
from typing import Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderConfigError,
    ReaderDependencyError,
    ReaderLoadError,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.util.logging.logging_util import LOGGER

_DEFAULT_TIMEOUT = 20.0
_DEFAULT_USER_AGENT = "agentUniverse/1.0 (+https://github.com/)"


class WebPageReader(Reader):
    """Reader for static web pages via HTTP fetching and boilerplate removal.

    Usage:
        reader = WebPageReader()
        docs = reader.load_data(url="https://example.com/article")
    """

    def _load_data(self, url: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Fetch a static web page and extract its main text.

        Args:
            url (str): The target web page url.
            ext_info (Optional[Dict]): Optional runtime configuration, supports:
                - timeout (float): HTTP request timeout in seconds.
                - user_agent (str): Custom User-Agent header.

        Returns:
            List[Document]: Documents containing the extracted page text.

        Raises:
            ReaderConfigError: If the url is empty.
            ReaderLoadError: If the page cannot be fetched.
            ReaderDependencyError: If no extractor is available.
        """
        if not isinstance(url, str) or not url:
            raise ReaderConfigError(
                "WebPageReader requires a non-empty url string.",
                reader_name=self.__class__.__name__,
            )
        LOGGER.debug(f"WebPageReader start load url={url}")

        timeout = (ext_info or {}).get("timeout", _DEFAULT_TIMEOUT)
        user_agent = (ext_info or {}).get("user_agent", _DEFAULT_USER_AGENT)

        html = self._fetch_html(url, timeout, user_agent)
        LOGGER.debug(f"WebPageReader fetched html length={len(html)}")

        text, metadata_extra = self._extract_main_text(html, url)
        LOGGER.debug(f"WebPageReader extracted text length={len(text)}")

        metadata: Dict = {"source": "web", "url": url}
        metadata.update(metadata_extra)
        if ext_info:
            metadata.update(ext_info)

        return [Document(text=text, metadata=metadata)]

    def _fetch_html(self, url: str, timeout=_DEFAULT_TIMEOUT, user_agent=_DEFAULT_USER_AGENT) -> str:
        """Fetch raw html for a url, trying httpx then requests.

        Args:
            url (str): The target web page url.
            timeout (float): HTTP request timeout in seconds.
            user_agent (str): User-Agent header value.

        Returns:
            str: The fetched html content.

        Raises:
            ReaderLoadError: If both httpx and requests fail.
        """
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        try:
            import httpx  # type: ignore
            LOGGER.debug("WebPageReader using httpx")
            with httpx.Client(timeout=timeout, headers=headers) as client:
                resp = client.get(url, follow_redirects=True)
                resp.raise_for_status()
                return resp.text
        except Exception as e_httpx:
            LOGGER.debug(f"WebPageReader httpx failed: {e_httpx}")
            try:
                import requests  # type: ignore
                LOGGER.debug("WebPageReader using requests fallback")
                resp = requests.get(url, timeout=timeout, headers=headers)
                resp.raise_for_status()
                return resp.text
            except Exception as e_requests:
                raise ReaderLoadError(
                    f"Failed to fetch url: {url}. httpx_error={e_httpx}, requests_error={e_requests}",
                    reader_name=self.__class__.__name__,
                ) from e_requests

    def _extract_main_text(self, html: str, url: str) -> Tuple[str, Dict]:
        """Extract the main article text from html.

        Args:
            html (str): The raw html content.
            url (str): The source url (used for metadata only).

        Returns:
            Tuple[str, Dict]: The extracted (text, extra_metadata).

        Raises:
            ReaderDependencyError: If no extractor is available.
        """
        # Try trafilatura
        try:
            import trafilatura  # type: ignore
            LOGGER.debug("WebPageReader using trafilatura")
            extracted = trafilatura.extract(html, include_links=False, include_images=False)
            if extracted and extracted.strip():
                return extracted.strip(), {"extractor": "trafilatura"}
        except Exception as e_traf:
            LOGGER.debug(f"WebPageReader trafilatura failed: {e_traf}")

        # Fallback to readability
        try:
            from readability import Document as ReadabilityDocument  # type: ignore
            from bs4 import BeautifulSoup  # type: ignore
            LOGGER.debug("WebPageReader using readability-lxml")
            article_html = ReadabilityDocument(html).summary(html_partial=True)
            soup = BeautifulSoup(article_html, "lxml")
            text = soup.get_text("\n")
            text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            if text:
                return text, {"extractor": "readability"}
        except Exception as e_read:
            LOGGER.debug(f"WebPageReader readability failed: {e_read}")

        # Last resort: BeautifulSoup plain text
        try:
            from bs4 import BeautifulSoup  # type: ignore
            LOGGER.debug("WebPageReader using BeautifulSoup fallback")
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style", "noscript"]):
                tag.extract()
            text = soup.get_text("\n")
            text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            return text, {"extractor": "bs4"}
        except Exception as e_bs:
            raise ReaderDependencyError(
                "Install one of the extractors: `pip install trafilatura` or "
                "`pip install readability-lxml beautifulsoup4 lxml`",
                reader_name=self.__class__.__name__,
            ) from e_bs
