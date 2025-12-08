# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/5
# @Author  : liduowen
# @Email   : liduowen.ldw@antgroup.com
# @FileName: web_reader.py


from urllib.parse import urlparse
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class WebReader(Reader):
    """Web reader."""

    def _load_data(self, url: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse the Web page.

        Note:
            The web page cannot be process in pagination.
            `playwright` is required to read web page: `pip install playwright`
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ImportError(
                "web2txt is required to read web page: "
                "`pip install playwright`"
            )


        if not self.is_valid_http_url(url):
            raise ValueError(f"Invalid URL: {url}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle")  # 等网络空闲，保证 JS 跑完
                text = page.inner_text("body")  # 获取 <body> 里所有可见文本
                browser.close()
        except Exception as e:
            browser.close()
            raise Exception(f"Error loading web page: {e}")


        metadata = {"url": url}
        if ext_info is not None:
            metadata.update(ext_info)

        return [Document(text=text, metadata=metadata or {})]

    @staticmethod
    def is_valid_http_url(url) -> bool:
        """判断字符串 url 是否为合理的 HTTP/HTTPS URL。"""
        if not isinstance(url, str):
            return False
        try:
            result = urlparse(url)
            # 必须：scheme 正确、有 netloc（域名或 IP）、不含空格等非法字符
            return all([result.scheme in {'http', 'https'},
                        result.netloc,  # 非空
                        not any(ch.isspace() for ch in url)])
        except Exception:
            return False