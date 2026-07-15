# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/7/15
# @FileName: feishu_reader.py
"""Feishu public document reader using Selenium.

Migrated from ``cloud_file_reader/`` to ``cloud/`` with:
- Proper ``Reader`` base class inheritance
- Lazy WebDriver creation (no driver at ``__init__`` time)
- Semantic exception hierarchy (``ReaderDependencyError``,
  ``ReaderLoadError``, ``ReaderParseError``)
- Structured logging via ``logging`` module
- Explicit ``close()`` method with ``__del__`` fallback
"""

import logging
import time
from typing import List, Optional

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderDependencyError,
    ReaderLoadError,
    ReaderParseError,
)
from agentuniverse.agent.action.knowledge.store.document import Document

logger = logging.getLogger(__name__)


class FeishuReader(Reader):
    """Reader for public Feishu documents via headless Selenium.

    The Chrome WebDriver is created lazily on first use so that
    importing this module does not fail when Selenium is not
    installed.

    Attributes:
        _driver: Selenium WebDriver instance (created on demand).
    """

    _driver: Optional[object] = None

    # ------------------------------------------------------------------
    # Lazy WebDriver
    # ------------------------------------------------------------------

    def _get_driver(self):
        """Return the Selenium WebDriver, creating it if necessary.

        Raises:
            ReaderDependencyError: If selenium or ChromeDriver is not
                available.
        """
        if self._driver is not None:
            return self._driver

        try:
            from selenium import webdriver  # type: ignore
            from selenium.webdriver.chrome.options import Options  # type: ignore
        except ImportError:
            raise ReaderDependencyError(
                "Selenium is required for FeishuReader",
                reader_name=self.name or "FeishuReader",
                dependency="selenium",
                install_hint="pip install selenium",
            )

        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument(
                "User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
            self._driver = webdriver.Chrome(options=chrome_options)
            return self._driver
        except Exception as exc:
            raise ReaderDependencyError(
                f"Failed to initialise Chrome WebDriver: {exc}",
                reader_name=self.name or "FeishuReader",
                dependency="chromedriver",
                install_hint="pip install selenium && ensure chromedriver is on PATH",
            )

    # ------------------------------------------------------------------
    # Core loading
    # ------------------------------------------------------------------

    def _load_data(self, url: str, ext_info: Optional[dict] = None) -> List[Document]:
        """Load a public Feishu document.

        Args:
            url: URL of the public Feishu document.
            ext_info: Unused; reserved for future extensions.

        Returns:
            List containing a single :class:`Document` with the
            extracted text.

        Raises:
            ReaderLoadError: If the page cannot be loaded.
            ReaderDependencyError: If selenium / chromedriver is not
                installed.
            ReaderParseError: If the loaded HTML cannot be parsed.
        """
        if not url:
            raise ReaderLoadError(
                "URL is required for FeishuReader",
                reader_name=self.name or "FeishuReader",
            )

        content = self._fetch_document_content(url)
        metadata = {"source": url}
        return [Document(text=content, metadata=metadata)]

    # ------------------------------------------------------------------
    # Fetch & parse
    # ------------------------------------------------------------------

    def _fetch_document_content(self, url: str) -> str:
        """Fetch the Feishu page and extract text content.

        Raises:
            ReaderLoadError: On page-load failure.
            ReaderDependencyError: If BeautifulSoup is not installed.
            ReaderParseError: If parsing the page source fails.
        """
        try:
            driver = self._get_driver()
        except ReaderDependencyError:
            raise

        try:
            driver.get(url)
            time.sleep(5)  # wait for dynamic rendering
            page_source = driver.page_source
        except Exception as exc:
            raise ReaderLoadError(
                f"Failed to load Feishu page: {exc}",
                reader_name=self.name or "FeishuReader",
                source=url,
            )

        try:
            from bs4 import BeautifulSoup  # type: ignore
        except ImportError:
            raise ReaderDependencyError(
                "BeautifulSoup is required for FeishuReader",
                reader_name=self.name or "FeishuReader",
                dependency="beautifulsoup4",
                install_hint="pip install beautifulsoup4 lxml",
            )

        try:
            soup = BeautifulSoup(page_source, "html.parser")
            return self._parse_content(soup)
        except Exception as exc:
            raise ReaderParseError(
                f"Failed to parse Feishu page: {exc}",
                reader_name=self.name or "FeishuReader",
                source=url,
            )

    def _parse_content(self, soup) -> str:
        """Parse the BeautifulSoup tree and return cleaned text."""
        body = soup.find("body")
        if not body:
            return "Body tag not found"

        content: List[str] = []

        # Title
        title_tag = soup.find("h1")
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            if title_text:
                content.append(f"Title: {title_text}")

        # Irrelevant class names
        irrelevant_classes = [
            "footer", "nav", "navigation", "header",
            "comment", "help", "login",
        ]

        # Main content container
        content_div = soup.find("div", class_="doc-content")
        if content_div:
            for tag in content_div.find_all(["p", "div", "span"], recursive=True):
                if tag.get("class") and any(
                    cls.lower() in irrelevant_classes for cls in tag.get("class")
                ):
                    continue
                text = tag.get_text(strip=True)
                if text and not any(
                    kw in text.lower()
                    for kw in ["login", "sign up", "comment", "help"]
                ):
                    content.append(text)
        else:
            for div in body.find_all("div", recursive=True):
                if div.get("class") and any(
                    cls.lower() in irrelevant_classes for cls in div.get("class")
                ):
                    continue
                text = div.get_text(strip=True)
                if text and not any(
                    kw in text.lower()
                    for kw in ["login", "sign up", "comment", "help"]
                ):
                    content.append(text)

        # Deduplicate preserving order
        unique_content = list(dict.fromkeys(content))
        return "\n".join(unique_content) if unique_content else "No meaningful content found"

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def close(self):
        """Explicitly close the WebDriver session."""
        if self._driver is not None:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None

    def __del__(self):
        self.close()


# Backward compatibility alias — the old class name used in YAML
PublicFeishuReader = FeishuReader