# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: rendered_web_page_reader.py
"""Reader for dynamic web pages using Playwright rendering.

Requires:
    pip install playwright
    playwright install

The Playwright dependency is imported lazily and runtime options such as
``timeout`` can be supplied through ``ext_info``.
"""
from typing import Dict, List, Optional

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderConfigError,
    ReaderDependencyError,
    ReaderLoadError,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.util.logging.logging_util import LOGGER

_DEFAULT_TIMEOUT = 20000


class RenderedWebPageReader(Reader):
    """Reader for dynamic web pages using Playwright rendering.

    Requires:
        pip install playwright
        playwright install
    """

    def _load_data(self, url: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Render a dynamic web page and extract its main text.

        Args:
            url (str): The target web page url.
            ext_info (Optional[Dict]): Optional runtime configuration, supports:
                - timeout (int): Playwright navigation timeout in milliseconds.

        Returns:
            List[Document]: Documents containing the extracted page text.

        Raises:
            ReaderConfigError: If the url is empty.
            ReaderDependencyError: If playwright is not installed.
            ReaderLoadError: If the page cannot be rendered.
        """
        if not isinstance(url, str) or not url:
            raise ReaderConfigError(
                "RenderedWebPageReader requires a non-empty url string.",
                reader_name=self.__class__.__name__,
            )
        LOGGER.debug(f"RenderedWebPageReader start load url={url}")

        timeout = int((ext_info or {}).get("timeout", _DEFAULT_TIMEOUT))
        html = self._render_and_get_html(url, timeout)
        LOGGER.debug(f"RenderedWebPageReader rendered html length={len(html)}")

        # Reuse extraction logic from WebPageReader by importing on demand
        from .web_page_reader import WebPageReader
        text, metadata_extra = WebPageReader()._extract_main_text(html, url)

        metadata: Dict = {"source": "web", "url": url, "rendered": True}
        metadata.update(metadata_extra)
        if ext_info:
            metadata.update(ext_info)

        return [Document(text=text, metadata=metadata)]

    def _render_and_get_html(self, url: str, timeout: int = _DEFAULT_TIMEOUT) -> str:
        """Render a url with a headless browser and return the html.

        Args:
            url (str): The target web page url.
            timeout (int): Playwright navigation timeout in milliseconds.

        Returns:
            str: The rendered html content.

        Raises:
            ReaderDependencyError: If playwright is not installed.
            ReaderLoadError: If rendering fails.
        """
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError as e:
            raise ReaderDependencyError(
                "playwright is required for RenderedWebPageReader. "
                "Install with `pip install playwright` and run `playwright install`",
                reader_name=self.__class__.__name__,
            ) from e

        LOGGER.debug("RenderedWebPageReader using playwright")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    context = browser.new_context()
                    page = context.new_page()
                    page.set_default_timeout(timeout)
                    page.set_default_navigation_timeout(timeout)
                    page.goto(url)
                    page.wait_for_load_state("networkidle")
                    return page.content()
                finally:
                    browser.close()
        except Exception as e:
            raise ReaderLoadError(
                f"Failed to render url {url}: {e}",
                reader_name=self.__class__.__name__,
            ) from e
