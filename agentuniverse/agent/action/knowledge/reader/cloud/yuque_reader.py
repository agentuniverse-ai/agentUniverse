#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/2 17:40
# @Author  : KiteSoar
# @Email   : hushihao2020x@163.com
# @FileName: yuque_reader.py

import re
import time
import random
import json
import logging
import urllib.parse
from typing import List, Any, Optional

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderLoadError,
    ReaderDependencyError,
    ReaderConfigError,
)
from agentuniverse.agent.action.knowledge.store.document import Document

logger = logging.getLogger(__name__)


class YuqueReader(Reader):
    """YuqueReader is a specialized reader designed to fetch and parse content from Yuque.

    Attributes:
        cookies: Cookies for authentication with Yuque.
        session: HTTP session with retry support.
    """

    def __init__(self, cookies: str = None, **data: Any):
        """Initialize HTTP session with retry support and optional cookies"""
        super().__init__(**data)
        self.cookies = cookies
        try:
            from requests.adapters import HTTPAdapter, Retry  # type: ignore
            import requests  # type: ignore
        except ImportError:
            raise ReaderDependencyError(
                "requests is required for YuqueReader",
                reader_name="YuqueReader",
                dependency="requests",
                install_hint="pip install requests",
            )
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _fetch_url_title(self, url: str) -> str:
        """Fetch page title and clean illegal filename characters"""
        headers = {'Cookie': self.cookies} if self.cookies else {}
        try:
            from bs4 import BeautifulSoup  # type: ignore
            resp = self.session.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            tag = soup.title
            if not tag or not tag.string:
                return "Untitled"
            title = tag.string.strip()
            title = re.sub(r'[\\/:*?"<>|]', '-', title)
            return title.replace(' · 语雀', '')
        except Exception as e:
            logger.debug("YuqueReader failed to fetch title for %s: %s", url, e)
            return "Untitled"

    def _fetch_page_markdown(self, book_id: str, slug: str) -> str:
        """Fetch markdown source for a single document"""
        headers = {'Cookie': self.cookies} if self.cookies else {}
        url = f'https://www.yuque.com/api/docs/{slug}?book_id={book_id}&merge_dynamic_data=false&mode=markdown'
        try:
            resp = self.session.get(url, headers=headers, timeout=20)
            if resp.status_code != 200:
                logger.warning("YuqueReader document download failed (status=%d): book_id=%s slug=%s",
                               resp.status_code, book_id, slug)
                return ''
            data = resp.json().get('data', {})
            md = data.get('sourcecode', '')

            def repl(m):
                src = m.group(1)
                return f'![]({src})'

            return re.sub(r'!\[.*?\]\((.*?)\)', repl, md)
        except Exception as e:
            logger.warning("YuqueReader failed to fetch markdown for book_id=%s slug=%s: %s", book_id, slug, e)
            return ''

    def _load_data(self, url: str, ext_info: Optional[dict] = None) -> List[Document]:
        """Fetch all docs in a Yuque book and return as List[Document]"""
        if not isinstance(url, str) or not url:
            raise ReaderLoadError(
                "YuqueReader._load_data requires a non-empty url string",
                reader_name="YuqueReader",
            )

        logger.info("YuqueReader start load url=%s", url)
        headers = {'Cookie': self.cookies} if self.cookies else {}
        try:
            resp = self.session.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            encoded = re.findall(r'decodeURIComponent\("(.+)"\)\);', resp.text)[0]
            docs = json.loads(urllib.parse.unquote(encoded))
        except Exception as e:
            raise ReaderLoadError(
                f"Failed to fetch Yuque book: {url}. Error: {e}",
                reader_name="YuqueReader",
                source=url,
            )

        book_title = self._fetch_url_title(url)
        chars = '/:*?"<>|\n\r'
        trans = str.maketrans({c: '_' for c in chars})

        documents: List[Document] = []
        for item in docs['book']['toc']:
            if item['title'] != book_title:
                continue
            md = self._fetch_page_markdown(str(docs['book']['id']), item['url'])
            if not md:
                continue
            metadata = {
                'source': url,
                'doc_title': item['title'],
                'sanitized_title': item['title'].translate(trans),
            }
            if ext_info:
                metadata.update(ext_info)
            documents.append(Document(text=md, metadata=metadata))
            time.sleep(random.uniform(1, 3))

        logger.info("YuqueReader extracted %d documents from %s", len(documents), url)
        return documents

    def __del__(self):
        """Close HTTP session"""
        try:
            if hasattr(self, 'session') and self.session:
                self.session.close()
        except Exception:
            pass