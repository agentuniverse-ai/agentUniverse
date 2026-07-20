#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/2 17:40
# @Author  : KiteSoar
# @Email   : hushihao2020x@163.com
# @FileName: yuque_reader.py
"""Original ``YuqueReader`` implementation restored for backward
compatibility.

This is the **verbatim** code that lived in
``cloud_file_reader/yuque_reader.py`` before the directory was removed
in PR #634.  It is intentionally kept separate from the new
``cloud/yuque_reader.py`` because the two classes have different
interfaces:

* Old ``YuqueReader`` — ``_load_data(self, url: str)`` (no *ext_info*),
  top-level ``import requests``, ``print()`` errors.
* New ``YuqueReader`` — ``_load_data(self, url, ext_info=None)``,
  lazy ``import requests``, semantic exceptions, logging.

Existing user code that imports ``YuqueReader`` from this module will
continue to work unchanged.  New code should use
``cloud.yuque_reader.YuqueReader``.
"""

import re
import time
import random
import json
import logging
import urllib.parse
import requests
from pydantic import ConfigDict
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
from typing import List, Any, Optional

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document

logger = logging.getLogger(__name__)


class YuqueReader(Reader):
    """
    YuqueReader is a specialized reader designed to fetch and parse content from Yuque

    Attributes:
        cookies: Cookies for authentication with Yuque.
        session: HTTP session with retry support.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    cookies: Optional[str] = None
    session: Optional[requests.Session] = None

    def __init__(self, cookies: str = None, **data: Any):
        """Initialize HTTP session with retry support and optional cookies"""
        super().__init__(**data)
        self.cookies = cookies
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _fetch_url_title(self, url: str) -> str:
        """Fetch page title and clean illegal filename characters"""
        headers = {'Cookie': self.cookies} if self.cookies else {}
        try:
            resp = self.session.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            tag = soup.title
            if not tag or not tag.string:
                return "Untitled"
            title = tag.string.strip()
            title = re.sub(r'[\\/:*?"<>|]', '-', title)
            return title.replace(' · 语雀', '')
        except requests.exceptions.RequestException:
            return "Request Error"

    def _fetch_page_markdown(self, book_id: str, slug: str) -> str:
        """Fetch markdown source for a single document"""
        headers = {'Cookie': self.cookies} if self.cookies else {}
        url = f'https://www.yuque.com/api/docs/{slug}?book_id={book_id}&merge_dynamic_data=false&mode=markdown'
        resp = self.session.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            logger.warning(
                "Yuque document download failed (HTTP %s) for book_id=%s "
                "slug=%s; the page may have been deleted.",
                resp.status_code, book_id, slug)
            return ''
        try:
            payload = resp.json()
        except ValueError:
            logger.warning(
                "Yuque document download failed: response was not valid JSON "
                "for book_id=%s slug=%s.", book_id, slug)
            return ''
        # A valid JSON list/string (e.g. from an error gateway) has no .get();
        # only a JSON object carries the 'data' field we need.
        if not isinstance(payload, dict):
            logger.warning(
                "Yuque document response for book_id=%s slug=%s was JSON %s, "
                "expected an object.", book_id, slug, type(payload).__name__)
            return ''
        data = payload.get('data')
        if not isinstance(data, dict):
            logger.warning(
                "Yuque document response for book_id=%s slug=%s has no 'data' "
                "object.", book_id, slug)
            return ''
        md = data.get('sourcecode', '')
        # Process image references inline

        def repl(m):
            src = m.group(1)
            return f'![]({src})'

        return re.sub(r'!\[.*?\]\((.*?)\)', repl, md)

    def _load_data(self, url: str) -> List[Document]:
        """Fetch all docs in a Yuque book and return as List[Document]"""
        headers = {'Cookie': self.cookies} if self.cookies else {}
        try:
            resp = self.session.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            encoded = re.findall(r'decodeURIComponent\("(.+)"\)\);', resp.text)[0]
            docs = json.loads(urllib.parse.unquote(encoded))
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"YuqueReader: failed to fetch book page {url}: {e}") from e
        except (IndexError, ValueError) as e:
            raise RuntimeError(
                f"YuqueReader: could not parse book metadata from {url}: {e}") from e

        # Validate the full decoded shape so a deleted / private / auth-failed
        # book surfaces a clear error instead of a silent, successful-looking
        # empty ingestion.
        if not isinstance(docs, dict):
            raise RuntimeError(
                f"YuqueReader: decoded payload from {url} is "
                f"{type(docs).__name__}, expected an object (the book may be "
                f"private, deleted, or require authentication).")
        book = docs.get('book')
        if not isinstance(book, dict):
            raise RuntimeError(
                f"YuqueReader: payload from {url} has no 'book' object (the "
                f"book may be private, deleted, or require authentication).")
        book_id = book.get('id')
        if not book_id:
            raise RuntimeError(
                f"YuqueReader: book parsed from {url} has no id; cannot fetch "
                f"its pages.")
        toc = book.get('toc')
        if not isinstance(toc, list):
            logger.warning(
                "YuqueReader: book %s from %s has no 'toc' list; no pages to "
                "read.", book_id, url)
            toc = []

        book_title = self._fetch_url_title(url)
        # sanitize titles for metadata keys if needed
        chars = '/:*?"<>|\n\r'
        trans = str.maketrans({c: '_' for c in chars})

        documents: List[Document] = []
        for item in toc:
            if not isinstance(item, dict) or item.get('title') != book_title:
                continue
            item_url = item.get('url')
            if not item_url:
                logger.warning(
                    "YuqueReader: toc entry in book %s is missing 'url'; "
                    "skipping: %r", book_id, item)
                continue
            md = self._fetch_page_markdown(str(book_id), item_url)
            if not md:
                continue
            metadata = {
                'source': url,
                'doc_title': item.get('title'),
                'sanitized_title': item.get('title', '').translate(trans)
            }
            documents.append(Document(text=md, metadata=metadata))
            # Respectful delay
            time.sleep(random.uniform(1, 3))
        return documents

    def __del__(self):
        """Close HTTP session"""
        try:
            self.session.close()
        except Exception:
            pass
