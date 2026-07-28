# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: web_page_reader.py
import logging
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderConfigError,
    ReaderLoadError,
    ReaderParseError,
    ReaderDependencyError,
)
from agentuniverse.agent.action.knowledge.store.document import Document

logger = logging.getLogger(__name__)


class WebPageReader(Reader):
    """Reader for static web pages via HTTP fetching and boilerplate removal.

    Usage:
        reader = WebPageReader()
        docs = reader.load_data(url="https://example.com/article")

    Dependencies (optional but recommended):
        - trafilatura (preferred for article extraction)
        - readability-lxml (fallback for extraction)
        - beautifulsoup4 (last-resort plain text)
        - httpx or requests
    """

    def _load_data(self, url: str, ext_info: Optional[Dict] = None) -> List[Document]:
        logger.info("WebPageReader start load url=%s", url)
        if not isinstance(url, str) or not url:
            raise ReaderConfigError(
                "WebPageReader._load_data requires a non-empty url string",
                reader_name="WebPageReader",
            )

        html = self._fetch_html(url)
        logger.info("WebPageReader fetched html length=%d", len(html))

        text, metadata_extra = self._extract_main_text(html, url)
        logger.info("WebPageReader extracted text length=%d", len(text))

        metadata: Dict = {"source": "web", "url": url}
        metadata.update(metadata_extra)
        if ext_info:
            metadata.update(ext_info)

        return [Document(text=text, metadata=metadata)]

    def _fetch_html(self, url: str) -> str:
        try:
            import httpx  # type: ignore
            logger.debug("WebPageReader using httpx")
            with httpx.Client(timeout=20.0, headers={
                "User-Agent": "agentUniverse/1.0 (+https://github.com/)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }) as client:
                resp = client.get(url, follow_redirects=True)
                resp.raise_for_status()
                return resp.text
        except Exception as e_httpx:
            logger.debug("WebPageReader httpx failed: %s", e_httpx)
            try:
                import requests  # type: ignore
                logger.debug("WebPageReader using requests fallback")
                resp = requests.get(url, timeout=20, headers={
                    "User-Agent": "agentUniverse/1.0 (+https://github.com/)",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                })
                resp.raise_for_status()
                return resp.text
            except Exception as e_requests:
                raise ReaderLoadError(
                    f"Failed to fetch url: {url}. httpx_error={e_httpx}, requests_error={e_requests}",
                    reader_name="WebPageReader",
                    source=url,
                )

    def _extract_main_text(self, html: str, url: str) -> (str, Dict):
        # Try trafilatura
        try:
            import trafilatura  # type: ignore
            logger.debug("WebPageReader using trafilatura")
            extracted = trafilatura.extract(html, include_links=False, include_images=False)
            if extracted and extracted.strip():
                return extracted.strip(), {"extractor": "trafilatura"}
        except Exception as e_traf:
            logger.debug("WebPageReader trafilatura failed: %s", e_traf)

        # Fallback to readability
        try:
            from readability import Document as ReadabilityDocument  # type: ignore
            from bs4 import BeautifulSoup  # type: ignore
            logger.debug("WebPageReader using readability-lxml")
            article_html = ReadabilityDocument(html).summary(html_partial=True)
            soup = BeautifulSoup(article_html, "lxml")
            text = soup.get_text("\n")
            text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            if text:
                return text, {"extractor": "readability"}
        except Exception as e_read:
            logger.debug("WebPageReader readability failed: %s", e_read)

        # Last resort: BeautifulSoup plain text
        try:
            from bs4 import BeautifulSoup  # type: ignore
            logger.debug("WebPageReader using BeautifulSoup fallback")
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style", "noscript"]):
                tag.extract()
            text = soup.get_text("\n")
            text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            return text, {"extractor": "bs4"}
        except Exception as e_bs:
            raise ReaderDependencyError(
                "Install one of the extractors: trafilatura or readability-lxml beautifulsoup4 lxml",
                reader_name="WebPageReader",
                dependency="trafilatura|readability-lxml|beautifulsoup4",
                install_hint="pip install trafilatura OR pip install readability-lxml beautifulsoup4 lxml",
            )
