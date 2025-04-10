#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/10 17:40
# @Author  : zhaoyifei
# @Email   : 2179709293@qq.com
# @FileName: feishu_reader.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from typing import Dict,List
from agentuniverse.agent.action.knowledge.store.document import Document

class PublicFeishuReader:
    """Feishu public document reader using Selenium

    Extracts content from public Feishu documents through web scraping with dynamic rendering support.

    Attributes:
        driver: Selenium WebDriver instance configured for headless browsing
    """

    def __init__(self):
        """Initialize Selenium WebDriver with headless configuration"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument(
            "User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.driver = webdriver.Chrome(options=chrome_options)

    def _fetch_document_content(self, url: str) -> str:
        """Fetch Feishu document content after dynamic rendering

        Args:
            url (str): URL of the public Feishu document

        Returns:
            str: Extracted document content or empty string on failure

        Raises:
            RuntimeError: If page loading fails
        """
        try:
            self.driver.get(url)
            # Wait for dynamic content loading
            time.sleep(5)
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            return self._parse_content(soup)
        except Exception as e:
            print(f"Error fetching document: {e}")
            return ""

    def _parse_content(self, soup: BeautifulSoup) -> str:
        """Parse document content and extract meaningful text

        Args:
            soup (BeautifulSoup): Parsed HTML document object

        Returns:
            str: Cleaned text content with deduplication

        Raises:
            ValueError: If document structure is invalid
        """
        # Find the body tag
        body = soup.find('body')
        if not body:
            return "Body tag not found"

        content = []

        # Extract document title
        title_tag = soup.find('h1')
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            if title_text:
                content.append(f"Title: {title_text}")

        # Define irrelevant class names for filtering
        irrelevant_classes = ['footer', 'nav', 'navigation', 'header', 'comment', 'help', 'login']

        # Try to locate main content container
        content_div = soup.find('div', class_='doc-content')  # Update class name as needed
        if content_div:
            # Extract text from content container
            for tag in content_div.find_all(['p', 'div', 'span'], recursive=True):
                if tag.get('class') and any(cls.lower() in irrelevant_classes for cls in tag.get('class')):
                    continue
                text = tag.get_text(strip=True)
                if text and text.strip() and not any(
                        keyword in text.lower() for keyword in ['login', 'sign up', 'comment', 'help']):
                    content.append(text)
        else:
            # Fallback extraction from body
            for div in body.find_all('div', recursive=True):
                if div.get('class') and any(cls.lower() in irrelevant_classes for cls in div.get('class')):
                    continue
                text = div.get_text(strip=True)
                if text and text.strip() and not any(
                        keyword in text.lower() for keyword in ['login', 'sign up', 'comment', 'help']):
                    content.append(text)

        # Deduplicate while preserving order
        unique_content = list(dict.fromkeys(content))
        return "\n".join(unique_content) if unique_content else "No meaningful content found"

    def load_data(self, url: str) -> List[Document]:
        """Load and process Feishu document data

        Args:
            url (str): URL of the target document

        Returns:
            List[Document]: List of documents containing feishu online file content
        """
        content = self._fetch_document_content(url)
        # If the content is empty, return an empty list
        if not content:
            return []
        # Construct metadata
        metadata = {"source": url}
        # Create a Document object
        document = Document(text=content, metadata=metadata)
        # Return a list containing a single Document
        return [document]

    def __del__(self):
        """Cleanup resources by closing browser instance"""
        if hasattr(self, 'driver'):
            self.driver.quit()

"""
if __name__ == "__main__":
    # Example usage
    test_url = "https://www.feishu.cn/docx/SV2JdR5P4odO8AxIhpBcVo1Xncg"
    reader = PublicFeishuReader()
    data = reader.load_data(test_url)
    print(data)
    print("Document Summary:", data[0].text)
"""