#!/usr/bin/env python3
"""Reader for publicly accessible Feishu documents."""

from contextlib import suppress
from typing import Any

from bs4 import BeautifulSoup
from pydantic import PrivateAttr

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document

_SELENIUM_DEPENDENCY_ERROR = (
    "selenium is required to read public Feishu documents; " "please run `pip install selenium`"
)
_WEBDRIVER_INIT_ERROR = (
    "Failed to initialize Chrome WebDriver for the Feishu reader. "
    "Ensure Chrome or Chromium is installed and compatible with Selenium."
)
_RENDERED_DOCUMENT_SCRIPT = (
    "return document.readyState === 'complete' && "
    "document.body !== null && "
    "document.body.innerText.trim().length > 0;"
)
_IRRELEVANT_CLASSES = {
    "comment",
    "footer",
    "header",
    "help",
    "login",
    "nav",
    "navigation",
}
_IRRELEVANT_KEYWORDS = ("comment", "help", "login", "sign up")


class PublicFeishuReader(Reader):
    """Load a public Feishu document through a lazily created WebDriver.

    Constructing and registering this component does not import Selenium or
    launch a browser. The optional dependency and Chrome WebDriver are only
    needed when :meth:`load_data` performs the first read.
    """

    wait_timeout: float = 10.0
    _driver: Any = PrivateAttr(default=None)

    @property
    def driver(self) -> Any:
        """Return the active WebDriver, if one has been initialized."""
        return self._driver

    @staticmethod
    def _create_driver() -> Any:
        """Create a headless Chrome WebDriver on first use."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
        except ImportError as exc:
            raise ImportError(_SELENIUM_DEPENDENCY_ERROR) from exc

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument(
            "User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        try:
            return webdriver.Chrome(options=chrome_options)
        except Exception as exc:
            raise RuntimeError(_WEBDRIVER_INIT_ERROR) from exc

    def _ensure_driver(self) -> Any:
        """Return the current driver, creating it lazily when necessary."""
        if self._driver is None:
            self._driver = self._create_driver()
        return self._driver

    def _wait_for_document(self, driver: Any) -> None:
        """Wait until the page is complete and its body contains rendered text."""
        try:
            from selenium.webdriver.support.ui import WebDriverWait
        except ImportError as exc:
            raise ImportError(_SELENIUM_DEPENDENCY_ERROR) from exc

        WebDriverWait(driver, self.wait_timeout).until(
            lambda current_driver: current_driver.execute_script(_RENDERED_DOCUMENT_SCRIPT)
        )

    def _fetch_document_content(self, url: str) -> str:
        """Fetch and parse Feishu content after dynamic rendering."""
        driver = self._ensure_driver()
        try:
            driver.get(url)
            self._wait_for_document(driver)
            page_source = driver.page_source
        except ImportError:
            raise
        except Exception as exc:
            print(f"Error fetching document: {exc}")
            return ""

        return self._parse_content(BeautifulSoup(page_source, "html.parser"))

    @staticmethod
    def _is_irrelevant(tag: Any) -> bool:
        classes = tag.get("class") or []
        return any(str(class_name).lower() in _IRRELEVANT_CLASSES for class_name in classes)

    @staticmethod
    def _meaningful_text(tag: Any) -> str | None:
        text = tag.get_text(strip=True)
        if not text:
            return None
        lowered = text.lower()
        if any(keyword in lowered for keyword in _IRRELEVANT_KEYWORDS):
            return None
        return text

    def _parse_content(self, soup: BeautifulSoup) -> str:
        """Extract meaningful text from a rendered Feishu document."""
        body = soup.find("body")
        if body is None:
            return "Body tag not found"

        content: list[str] = []
        title_tag = soup.find("h1")
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            if title_text:
                content.append(f"Title: {title_text}")

        content_div = soup.find("div", class_="doc-content")
        tags = (
            content_div.find_all(["p", "div", "span"], recursive=True)
            if content_div
            else body.find_all("div", recursive=True)
        )
        for tag in tags:
            if self._is_irrelevant(tag):
                continue
            text = self._meaningful_text(tag)
            if text:
                content.append(text)

        unique_content = list(dict.fromkeys(content))
        return "\n".join(unique_content) if unique_content else "No meaningful content found"

    def _load_data(self, url: str) -> list[Document]:
        """Load one public Feishu document."""
        content = self._fetch_document_content(url)
        if not content:
            return []
        return [Document(text=content, metadata={"source": url})]

    def close(self) -> None:
        """Close the WebDriver once; repeated calls are safe."""
        driver = self._driver
        self._driver = None
        if driver is not None:
            driver.quit()

    def __del__(self) -> None:
        """Best-effort cleanup for callers that did not close explicitly."""
        with suppress(Exception):
            self.close()
