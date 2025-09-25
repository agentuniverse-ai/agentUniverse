#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/7 10:00
# @Author  : wangyapei
# @FileName: website_bs4_reader.py

from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import random
import time

from bs4 import BeautifulSoup
import httpx

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.reader.reader import Reader
from pydantic import Field


class WebsiteBs4Reader(Reader):
    """Website content reader based on BeautifulSoup

    Crawls website content and extracts main text, with support for limiting crawl depth and max links.

    Note:
        Required packages:
            - beautifulsoup4: `pip install beautifulsoup4`
            - httpx: `pip install httpx`

    Attributes:
        max_depth: Maximum crawl depth, defaults to 1
        max_links: Maximum number of links to crawl, defaults to 1
    """

    max_depth: int = Field(default=1, description="Maximum crawl depth")
    max_links: int = Field(default=1, description="Maximum number of links to crawl")

    def __init__(self, **data):
        super().__init__(**data)
        self._visited = set()  # Track visited URLs
        self._urls_to_crawl = []  # Queue of URLs to crawl

    def _load_data(self, url: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Crawl website content and return list of documents

        Args:
            url: Website URL to crawl
            ext_info: Optional metadata dict. Can contain max_depth and max_links to override defaults

        Returns:
            List[Document]: List of documents containing webpage content

        Raises:
            ValueError: If URL is invalid or empty
            ConnectionError: If network connection fails
            RuntimeError: If content parsing fails
        """
        # Validate URL
        if not url or not isinstance(url, str):
            return []

        if not url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL format")

        # Update config from ext_info if provided
        if ext_info:
            if "max_depth" in ext_info:
                self.max_depth = ext_info["max_depth"]
            if "max_links" in ext_info:
                self.max_links = ext_info["max_links"]

        try:
            # Crawl website and create documents
            crawler_result = self._crawl_website(url)
            documents = []

            for crawled_url, content in crawler_result.items():
                metadata = {"source": crawled_url}
                if ext_info:
                    metadata.update(ext_info)
                documents.append(Document(text=content, metadata=metadata))
            return documents

        except httpx.RequestError as e:
            raise ConnectionError(f"Network connection failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Content parsing failed: {str(e)}")

    def _get_primary_domain(self, url: str) -> str:
        """Extract primary domain from URL

        Args:
            url: Full URL

        Returns:
            str: Primary domain
        """
        domain_parts = urlparse(url).netloc.split(".")
        return ".".join(domain_parts[-2:])

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from webpage

        Args:
            soup: BeautifulSoup object

        Returns:
            str: Extracted text content
        """
        # Generic content extraction strategy
        content_selectors = [
            ("article", None),
            ("main", None),
            ("div", "content"),
            ("div", "main-content"),
            ("div", "post-content"),
            ("div", "article-content"),
            ("div", lambda x: x and "content" in x),
        ]

        # Try each selector pattern
        for tag, class_name in content_selectors:
            element = soup.find(tag, class_=class_name)
            if element:
                text = element.get_text(strip=True, separator=" ")
                if len(text) > 200:  # Only return if substantial content found
                    return text

        # Fallback: Extract largest text block
        all_elements = soup.find_all(["div", "section"])
        if all_elements:
            return max([e.get_text(strip=True, separator=" ") for e in all_elements], key=len, default="")

        return ""

    def _crawl_website(self, url: str) -> Dict[str, str]:
        """Execute website crawling

        Args:
            url: Starting URL

        Returns:
            Dict[str, str]: Mapping of URLs to their content
        """
        num_links = 0
        crawler_result: Dict[str, str] = {}

        # Initialize crawl with starting URL
        primary_domain = self._get_primary_domain(url)
        self._urls_to_crawl.append((url, 1))

        while self._urls_to_crawl:
            current_url, current_depth = self._urls_to_crawl.pop(0)

            # Skip if URL meets any exclusion criteria
            if (
                current_url in self._visited
                or not urlparse(current_url).netloc.endswith(primary_domain)
                or current_depth > self.max_depth
                or num_links >= self.max_links
            ):
                continue

            self._visited.add(current_url)
            time.sleep(random.uniform(1, 3))  # Rate limiting

            try:
                # Fetch and parse page content
                response = httpx.get(current_url, timeout=20)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                main_content = self._extract_main_content(soup)
                if main_content:
                    crawler_result[current_url] = main_content
                    num_links += 1

                # Find and queue additional links if not at max depth
                if current_depth < self.max_depth:
                    for link in soup.find_all("a", href=True):
                        full_url = urljoin(current_url, link["href"])
                        parsed_url = urlparse(full_url)
                        if (
                            parsed_url.netloc.endswith(primary_domain)
                            and not any(parsed_url.path.endswith(ext) for ext in [".pdf", ".jpg", ".png"])
                            and full_url not in self._visited
                            and (full_url, current_depth + 1) not in self._urls_to_crawl
                        ):
                            self._urls_to_crawl.append((full_url, current_depth + 1))

            except Exception as e:
                print(f"error:{e}")
                continue

        return crawler_result
