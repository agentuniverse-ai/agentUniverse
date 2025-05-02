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
import urllib.parse
import requests
from pydantic import ConfigDict
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
from typing import List, Any, Optional

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


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
        retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500,502,503,504])
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
            print("The document download failed. The page may have been deleted.", book_id, slug)
            return ''
        data = resp.json().get('data', {})
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
        except Exception as e:
            print(f"Request failed: {e}")
            return []

        book_title = self._fetch_url_title(url)
        # sanitize titles for metadata keys if needed
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
                'sanitized_title': item['title'].translate(trans)
            }
            documents.append(Document(text=md, metadata=metadata))
            # Respectful delay
            time.sleep(random.uniform(1, 3))
        return documents

    def __del__(self):
        """Close HTTP session"""
        try:
            self.session.close()
        except:
            pass

# if __name__ == '__main__':
#     # Example usage
#     reader = YuqueReader(cookies=None)
#     test_url = "Fill in the publicly accessible Yuque document link"
#     docs = reader.load_data(test_url)
#     for doc in docs:
#         print(f"Title: {doc.metadata['doc_title']}")
#         print(doc.text)
