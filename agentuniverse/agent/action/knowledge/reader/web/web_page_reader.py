# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: web_page_reader.py
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


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
        print(f"debugging: WebPageReader start load url={url}")
        if not isinstance(url, str) or not url:
            raise ValueError("WebPageReader._load_data requires a non-empty url string")

        html = self._fetch_html(url)
        print(f"debugging: WebPageReader fetched html length={len(html)}")

        text, metadata_extra = self._extract_main_text(html, url)
        print(f"debugging: WebPageReader extracted text length={len(text)}")

        metadata: Dict = {"source": "web", "url": url}
        metadata.update(metadata_extra)
        if ext_info:
            metadata.update(ext_info)

        return [Document(text=text, metadata=metadata)]

    def _fetch_html(self, url: str) -> str:
        try:
            import httpx  # type: ignore
            print("debugging: WebPageReader using httpx")
            with httpx.Client(timeout=20.0, headers={
                "User-Agent": "agentUniverse/1.0 (+https://github.com/)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }) as client:
                resp = client.get(url, follow_redirects=True)
                resp.raise_for_status()
                return resp.text
        except Exception as e_httpx:
            print(f"debugging: WebPageReader httpx failed: {e_httpx}")
            try:
                import requests  # type: ignore
                print("debugging: WebPageReader using requests fallback")
                resp = requests.get(url, timeout=20, headers={
                    "User-Agent": "agentUniverse/1.0 (+https://github.com/)",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                })
                resp.raise_for_status()
                return resp.text
            except Exception as e_requests:
                raise RuntimeError(f"Failed to fetch url: {url}. httpx_error={e_httpx}, requests_error={e_requests}")

    def _extract_main_text(self, html: str, url: str) -> (str, Dict):
        # Try trafilatura
        try:
            import trafilatura  # type: ignore
            print("debugging: WebPageReader using trafilatura")
            extracted = trafilatura.extract(html, include_links=False, include_images=False)
            if extracted and extracted.strip():
                return extracted.strip(), {"extractor": "trafilatura"}
        except Exception as e_traf:
            print(f"debugging: WebPageReader trafilatura failed: {e_traf}")

        # Fallback to readability
        try:
            from readability import Document as ReadabilityDocument  # type: ignore
            from bs4 import BeautifulSoup  # type: ignore
            print("debugging: WebPageReader using readability-lxml")
            article_html = ReadabilityDocument(html).summary(html_partial=True)
            soup = BeautifulSoup(article_html, "lxml")
            text = soup.get_text("\n")
            text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            if text:
                return text, {"extractor": "readability"}
        except Exception as e_read:
            print(f"debugging: WebPageReader readability failed: {e_read}")

        # Last resort: BeautifulSoup plain text
        try:
            from bs4 import BeautifulSoup  # type: ignore
            print("debugging: WebPageReader using BeautifulSoup fallback")
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style", "noscript"]):
                tag.extract()
            text = soup.get_text("\n")
            text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            return text, {"extractor": "bs4"}
        except Exception as e_bs:
            raise RuntimeError(
                "Install one of the extractors: `pip install trafilatura` or "
                "`pip install readability-lxml beautifulsoup4 lxml`"
            )
