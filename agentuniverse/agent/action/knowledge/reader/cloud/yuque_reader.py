# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/2 17:40
# @Author  : KiteSoar
# @Email   : hushihao2020x@163.com
# @FileName: yuque_reader.py

import re
import time
import random
import json
import urllib.parse
from typing import List, Any, Optional

from pydantic import ConfigDict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderConfigError,
    ReaderDependencyError,
    ReaderLoadError,
    ReaderParseError,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.util.logging.logging_util import LOGGER

try:
    import requests
    from requests.adapters import HTTPAdapter, Retry
except ImportError:
    requests = None
    HTTPAdapter = None
    Retry = None


class YuqueReader(Reader):
    """Reader designed to fetch and parse content from Yuque.

    Attributes:
        cookies: Cookies for authentication with Yuque (optional for public docs).
        session: HTTP session with retry support.
        request_timeout: Default timeout (seconds) for HTTP requests.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    cookies: Optional[str] = None
    session: Optional[Any] = None
    request_timeout: int = 20

    def __init__(self, cookies: str = None, request_timeout: int = 20, **data: Any):
        """Initialize HTTP session with retry support and optional cookies.

        Args:
            cookies (str): Optional cookies string for authenticated access.
            request_timeout (int): Default HTTP request timeout in seconds.
            **data: Additional keyword arguments forwarded to ``Reader``.
        """
        super().__init__(**data)
        self.cookies = cookies
        self.request_timeout = request_timeout
        if requests is None:
            self.session = None
        else:
            self.session = requests.Session()
            retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
            self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _ensure_session(self):
        """Ensure an HTTP session is available.

        Raises:
            ReaderDependencyError: If the ``requests`` package is missing.
        """
        if self.session is None:
            raise ReaderDependencyError(
                "Install requests to use YuqueReader: `pip install requests`",
                reader_name=self.__class__.__name__,
            )
        return self.session

    def _headers(self):
        """Build request headers including cookies when available."""
        return {'Cookie': self.cookies} if self.cookies else {}

    def _fetch_url_title(self, url: str) -> str:
        """Fetch page title and clean illegal filename characters."""
        session = self._ensure_session()
        try:
            resp = session.get(url, headers=self._headers(), timeout=self.request_timeout)
            resp.raise_for_status()
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            tag = soup.title
            if not tag or not tag.string:
                return "Untitled"
            title = tag.string.strip()
            title = re.sub(r'[\\/:*?"<>|]', '-', title)
            return title.replace(' · 语雀', '')
        except Exception as e:
            LOGGER.warning(f"YuqueReader failed to fetch title for {url}: {e}")
            return "Untitled"

    def _fetch_page_markdown(self, book_id: str, slug: str) -> str:
        """Fetch markdown source for a single document."""
        session = self._ensure_session()
        url = f'https://www.yuque.com/api/docs/{slug}?book_id={book_id}&merge_dynamic_data=false&mode=markdown'
        try:
            resp = session.get(url, headers=self._headers(), timeout=self.request_timeout)
        except Exception as e:
            LOGGER.error(f"YuqueReader request failed for {book_id}/{slug}: {e}")
            raise ReaderLoadError(
                f"Yuque document download request failed for {book_id}/{slug}: {e}",
                reader_name=self.__class__.__name__,
            ) from e
        if resp.status_code != 200:
            LOGGER.warning(f"YuqueReader document download failed (status {resp.status_code}) "
                           f"for {book_id}/{slug}; the page may have been deleted.")
            return ''
        data = resp.json().get('data', {})
        md = data.get('sourcecode', '')

        def repl(m):
            src = m.group(1)
            return f'![]({src})'

        return re.sub(r'!\[.*?\]\((.*?)\)', repl, md)

    def _load_data(self, url: str, ext_info: Optional[dict] = None) -> List[Document]:
        """Fetch all docs in a Yuque book and return as List[Document].

        Args:
            url (str): URL of the Yuque book.
            ext_info (Optional[dict]): Optional runtime configuration, supports:
                - cookies (str): override authentication cookies.
                - request_timeout (int): override HTTP timeout.

        Returns:
            List[Document]: Parsed documents from the Yuque book.

        Raises:
            ReaderConfigError: If no url is provided.
            ReaderParseError: If the page structure cannot be parsed.
        """
        if not url:
            raise ReaderConfigError(
                "YuqueReader requires a valid document url.",
                reader_name=self.__class__.__name__,
            )
        ext_info = ext_info or {}
        if 'cookies' in ext_info:
            self.cookies = ext_info['cookies']
        if 'request_timeout' in ext_info:
            self.request_timeout = ext_info['request_timeout']

        LOGGER.debug(f"YuqueReader start load url={url}")
        session = self._ensure_session()
        try:
            resp = session.get(url, headers=self._headers(), timeout=self.request_timeout)
            resp.raise_for_status()
            encoded = re.findall(r'decodeURIComponent\("(.+)"\)\);', resp.text)[0]
            docs = json.loads(urllib.parse.unquote(encoded))
        except IndexError as e:
            raise ReaderParseError(
                f"Failed to locate Yuque toc data in {url}: {e}",
                reader_name=self.__class__.__name__,
            ) from e
        except Exception as e:
            LOGGER.error(f"YuqueReader request failed for {url}: {e}")
            raise ReaderLoadError(
                f"YuqueReader request failed for {url}: {e}",
                reader_name=self.__class__.__name__,
            ) from e

        book_title = self._fetch_url_title(url)
        chars = '/:*?"<>|\n\r'
        trans = str.maketrans({c: '_' for c in chars})

        documents: List[Document] = []
        toc = docs.get('book', {}).get('toc', [])
        book_id = docs.get('book', {}).get('id')
        for item in toc:
            if item.get('title') != book_title:
                continue
            md = self._fetch_page_markdown(str(book_id), item.get('url', ''))
            if not md:
                continue
            metadata = {
                'source': url,
                'doc_title': item.get('title'),
                'sanitized_title': item.get('title', '').translate(trans),
            }
            documents.append(Document(text=md, metadata=metadata))
            time.sleep(random.uniform(1, 3))
        return documents

    def close(self):
        """Close the HTTP session if it was created."""
        if self.session is not None:
            try:
                self.session.close()
            except Exception:
                pass
            finally:
                self.session = None

    def __del__(self):
        """Close HTTP session."""
        self.close()
