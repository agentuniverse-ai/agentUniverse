#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/10 17:40
# @Author  : zhaoyifei
# @Email   : 2179709293@qq.com
# @FileName: feishu_reader.py

import logging
import time
from typing import Dict, List, Optional

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderLoadError,
    ReaderDependencyError,
    ReaderParseError,
)
from agentuniverse.agent.action.knowledge.store.document import Document

logger = logging.getLogger(__name__)


class FeishuReader(Reader):
    """Feishu public document reader using Selenium for dynamic rendering.

    Extracts content from public Feishu documents through web scraping with
    headless Chrome. The WebDriver is created lazily on first use and cleaned
    up automatically.

    Dependencies (optional):
        - selenium (required for dynamic page rendering)
        - beautifulsoup4 (required for HTML parsing)

    Usage:
        reader = FeishuReader()
        docs = reader.load_data(url="https://www.feishu.cn/docx/...")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._driver = None

    def _get_driver(self):
        """Lazily create and cache the Selenium WebDriver."""
        if self._driver is not None:
            return self._driver
        try:
            from selenium import webdriver  # type: ignore
            from selenium.webdriver.chrome.options import Options  # type: ignore
        except ImportError:
            raise ReaderDependencyError(
                "selenium is required for FeishuReader",
                reader_name="FeishuReader",
                dependency="selenium",
                install_hint="pip install selenium",
            )

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument(
            "User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self._driver = webdriver.Chrome(options=chrome_options)
        logger.debug("FeishuReader created WebDriver instance")
        return self._driver

    def _load_data(self, url: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Load and process Feishu document data.

        Args:
            url: URL of the public Feishu document
            ext_info: Optional additional metadata

        Returns:
            List[Document]: List containing a single Document with the extracted content
        """
        if not isinstance(url, str) or not url:
            raise ReaderLoadError(
                "FeishuReader._load_data requires a non-empty url string",
                reader_name="FeishuReader",
            )

        logger.info("FeishuReader start load url=%s", url)
        content = self._fetch_document_content(url)
        if not content:
            logger.warning("FeishuReader extracted empty content from url=%s", url)
            return []

        metadata = {"source": "feishu", "url": url}
        if ext_info:
            metadata.update(ext_info)

        logger.info("FeishuReader extracted text length=%d from %s", len(content), url)
        return [Document(text=content, metadata=metadata)]

    def _fetch_document_content(self, url: str) -> str:
        """Fetch Feishu document content after dynamic rendering.

        Args:
            url: URL of the public Feishu document

        Returns:
            str: Extracted document content or empty string on failure
        """
        try:
            from bs4 import BeautifulSoup  # type: ignore
        except ImportError:
            raise ReaderDependencyError(
                "beautifulsoup4 is required for FeishuReader HTML parsing",
                reader_name="FeishuReader",
                dependency="beautifulsoup4",
                install_hint="pip install beautifulsoup4",
            )

        driver = self._get_driver()
        try:
            driver.get(url)
            time.sleep(5)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            return self._parse_content(soup)
        except ReaderDependencyError:
            raise
        except Exception as e:
            raise ReaderLoadError(
                f"Failed to fetch Feishu document: {url}. Error: {e}",
                reader_name="FeishuReader",
                source=url,
            )

    def _parse_content(self, soup) -> str:
        """Parse document content and extract meaningful text.

        Args:
            soup: Parsed HTML document object

        Returns:
            str: Cleaned text content with deduplication
        """
        try:
            body = soup.find('body')
            if not body:
                raise ReaderParseError(
                    "No <body> tag found in Feishu document HTML",
                    reader_name="FeishuReader",
                )

            content = []

            title_tag = soup.find('h1')
            if title_tag:
                title_text = title_tag.get_text(strip=True)
                if title_text:
                    content.append(f"Title: {title_text}")

            irrelevant_classes = ['footer', 'nav', 'navigation', 'header', 'comment', 'help', 'login']

            content_div = soup.find('div', class_='doc-content')
            if content_div:
                for tag in content_div.find_all(['p', 'div', 'span'], recursive=True):
                    if tag.get('class') and any(cls.lower() in irrelevant_classes for cls in tag.get('class')):
                        continue
                    text = tag.get_text(strip=True)
                    if text and text.strip() and not any(
                            keyword in text.lower() for keyword in ['login', 'sign up', 'comment', 'help']):
                        content.append(text)
            else:
                for div in body.find_all('div', recursive=True):
                    if div.get('class') and any(cls.lower() in irrelevant_classes for cls in div.get('class')):
                        continue
                    text = div.get_text(strip=True)
                    if text and text.strip() and not any(
                            keyword in text.lower() for keyword in ['login', 'sign up', 'comment', 'help']):
                        content.append(text)

            unique_content = list(dict.fromkeys(content))
            return "\n".join(unique_content) if unique_content else ""
        except ReaderParseError:
            raise
        except Exception as e:
            raise ReaderParseError(
                f"Failed to parse Feishu document content: {e}",
                reader_name="FeishuReader",
            ) from e

    def close(self):
        """Explicitly close the WebDriver."""
        if self._driver is not None:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None
            logger.debug("FeishuReader closed WebDriver")

    def __del__(self):
        """Cleanup resources by closing browser instance."""
        self.close()


# Backward compatibility alias
PublicFeishuReader = FeishuReader