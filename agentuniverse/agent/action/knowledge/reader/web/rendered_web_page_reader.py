# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: rendered_web_page_reader.py
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class RenderedWebPageReader(Reader):
    """Reader for dynamic web pages using Playwright rendering.

    Requires:
        pip install playwright
        playwright install
    """

    def _load_data(self, url: str, ext_info: Optional[Dict] = None) -> List[Document]:
        print(f"debugging: RenderedWebPageReader start load url={url}")
        if not isinstance(url, str) or not url:
            raise ValueError("RenderedWebPageReader._load_data requires a non-empty url string")

        html = self._render_and_get_html(url)
        print(f"debugging: RenderedWebPageReader rendered html length={len(html)}")

        # Reuse extraction logic from WebPageReader by importing on demand
        from .web_page_reader import WebPageReader
        text, metadata_extra = WebPageReader()._extract_main_text(html, url)

        metadata: Dict = {"source": "web", "url": url, "rendered": True}
        metadata.update(metadata_extra)
        if ext_info:
            metadata.update(ext_info)

        return [Document(text=text, metadata=metadata)]

    def _render_and_get_html(self, url: str) -> str:
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except Exception as e:
            raise ImportError(
                "playwright is required for RenderedWebPageReader. "
                "Install with `pip install playwright` and run `playwright install`"
            )

        print("debugging: RenderedWebPageReader using playwright")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context()
                page = context.new_page()
                page.set_default_timeout(20000)
                page.set_default_navigation_timeout(20000)
                page.goto(url)
                page.wait_for_load_state("networkidle")
                html = page.content()
                return html
            finally:
                browser.close()
