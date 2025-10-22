# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: confluence_reader.py
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class ConfluenceReader(Reader):
    """Reader for Atlassian Confluence pages.

    Requires:
        pip install atlassian-python-api
    Credentials:
        site_url, username, token must be provided via ext_info or env.
    """

    def _load_data(self, page_id: str, ext_info: Optional[Dict] = None) -> List[Document]:
        print(f"debugging: ConfluenceReader start load page_id={page_id}")
        if not page_id:
            raise ValueError("ConfluenceReader requires page_id")

        site_url, username, token = self._resolve_cred(ext_info)
        try:
            from atlassian import Confluence  # type: ignore
        except Exception:
            raise ImportError("Install atlassian-python-api: `pip install atlassian-python-api`")

        conf = Confluence(url=site_url, username=username, password=token, cloud=True)
        page = conf.get_page_by_id(page_id, expand="body.view,version,metadata.labels")
        html = page.get("body", {}).get("view", {}).get("value", "")

        text = self._html_to_text(html)
        metadata: Dict = {
            "source": "confluence",
            "page_id": page_id,
            "title": page.get("title"),
            "version": page.get("version", {}).get("number")
        }
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text, metadata=metadata)]

    def _resolve_cred(self, ext_info: Optional[Dict]) -> (str, str, str):
        import os
        site_url = (ext_info or {}).get("site_url") or os.environ.get("CONFLUENCE_URL")
        username = (ext_info or {}).get("username") or os.environ.get("CONFLUENCE_USERNAME")
        token = (ext_info or {}).get("token") or os.environ.get("CONFLUENCE_TOKEN")
        if not site_url or not username or not token:
            raise EnvironmentError("Confluence credentials required: site_url, username, token")
        return site_url, username, token

    def _html_to_text(self, html: str) -> str:
        try:
            from bs4 import BeautifulSoup  # type: ignore
        except Exception:
            raise ImportError("Install beautifulsoup4 and lxml for ConfluenceReader")
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        text = soup.get_text("\n")
        return "\n".join([line.strip() for line in text.splitlines() if line.strip()])
