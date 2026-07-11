# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/10 17:40
# @Author  : zhaoyifei
# @Email   : 2179709293@qq.com
# @FileName: feishu_reader.py

from typing import Any, List, Optional

from pydantic import ConfigDict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderDependencyError,
    ReaderLoadError,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.util.logging.logging_util import LOGGER

_DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class FeishuReader(Reader):
    """Reader for public Feishu documents using Selenium dynamic rendering.

    The Selenium WebDriver is initialized lazily so that simply registering or
    importing the reader does not require a Chrome/Chromium environment. Optional
    runtime parameters such as ``wait_time``, ``user_agent`` and ``timeout`` can
    be supplied through ``ext_info`` when calling ``load_data``.

    Attributes:
        wait_time (int): Seconds to wait for dynamic content to render.
        user_agent (str): User-Agent header used by the headless browser.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    wait_time: int = 5
    user_agent: str = _DEFAULT_USER_AGENT
    _driver: Optional[Any] = None

    def _get_driver(self):
        """Lazily create the Selenium WebDriver instance.

        Returns:
            The Selenium WebDriver.

        Raises:
            ReaderDependencyError: If selenium is not installed.
        """
        if self._driver is not None:
            return self._driver
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
        except ImportError as e:
            raise ReaderDependencyError(
                "Install selenium and a Chrome driver to use FeishuReader: "
                "`pip install selenium`",
                reader_name=self.__class__.__name__,
            ) from e
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument(f"user-agent={self.user_agent}")
        self._driver = webdriver.Chrome(options=chrome_options)
        return self._driver

    def _fetch_document_content(self, url: str, wait_time: int) -> str:
        """Fetch Feishu document content after dynamic rendering.

        Args:
            url (str): URL of the public Feishu document.
            wait_time (int): Seconds to wait for dynamic content loading.

        Returns:
            str: Extracted document content or empty string on failure.

        Raises:
            ReaderLoadError: If page loading fails.
        """
        import time
        from bs4 import BeautifulSoup

        driver = self._get_driver()
        try:
            driver.get(url)
            time.sleep(wait_time)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            return self._parse_content(soup)
        except ReaderLoadError:
            raise
        except Exception as e:
            LOGGER.error(f"FeishuReader error fetching document {url}: {e}")
            raise ReaderLoadError(
                f"Failed to fetch Feishu document {url}: {e}",
                reader_name=self.__class__.__name__,
            ) from e

    def _parse_content(self, soup) -> str:
        """Parse document content and extract meaningful text.

        Args:
            soup: Parsed HTML document object.

        Returns:
            str: Cleaned text content with deduplication.
        """
        body = soup.find('body')
        if not body:
            return "Body tag not found"

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
        return "\n".join(unique_content) if unique_content else "No meaningful content found"

    def _load_data(self, url: str, ext_info: Optional[dict] = None) -> List[Document]:
        """Load and process Feishu document data.

        Args:
            url (str): URL of the target Feishu document.
            ext_info (Optional[dict]): Optional runtime configuration, supports:
                - wait_time (int): override render wait seconds.
                - user_agent (str): override User-Agent.

        Returns:
            List[Document]: List of documents containing feishu online file content.
        """
        if not url:
            from agentuniverse.agent.action.knowledge.reader.reader_errors import ReaderConfigError
            raise ReaderConfigError(
                "FeishuReader requires a valid document url.",
                reader_name=self.__class__.__name__,
            )
        ext_info = ext_info or {}
        wait_time = ext_info.get('wait_time', self.wait_time)
        if 'user_agent' in ext_info:
            self.user_agent = ext_info['user_agent']

        LOGGER.debug(f"FeishuReader start load url={url}")
        content = self._fetch_document_content(url, wait_time)
        if not content:
            return []
        metadata = {"source": url}
        document = Document(text=content, metadata=metadata)
        return [document]

    def close(self):
        """Release the underlying WebDriver if it was created."""
        if self._driver is not None:
            try:
                self._driver.quit()
            except Exception as e:
                LOGGER.warning(f"FeishuReader failed to quit driver: {e}")
            finally:
                self._driver = None

    def __del__(self):
        """Cleanup resources by closing browser instance."""
        self.close()
