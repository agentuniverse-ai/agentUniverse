# !/usr/bin/env python3

# This legacy reader uses optional imports and layered fallbacks by design.
# ruff: noqa: B904, PGH003, TRY003, TRY300, TRY301

# @Time    : 2025/9/29
# @FileName: web_page_reader.py
import logging
from urllib.parse import urljoin

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.tool.utils.url_safety import validate_public_http_url

logger = logging.getLogger(__name__)


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

    def _load_data(self, url: str, ext_info: dict | None = None) -> list[Document]:
        if not isinstance(url, str) or not url:
            raise ValueError("WebPageReader._load_data requires a non-empty url string")

        html = self._fetch_html(url)
        text, metadata_extra = self._extract_main_text(html, url)

        metadata: dict = {"source": "web", "url": url}
        metadata.update(metadata_extra)
        if ext_info:
            metadata.update(ext_info)

        return [Document(text=text, metadata=metadata)]

    def _fetch_html(self, url: str) -> str:
        validate_public_http_url(url)
        try:
            import httpx  # type: ignore
            with httpx.Client(timeout=20.0, headers={
                "User-Agent": "agentUniverse/1.0 (+https://github.com/)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }) as client:
                current_url = url
                for _ in range(11):
                    validate_public_http_url(current_url)
                    resp = client.get(current_url, follow_redirects=False)
                    if resp.is_redirect:
                        location = resp.headers.get("location")
                        if not location:
                            raise RuntimeError("redirect response has no Location header")
                        current_url = urljoin(current_url, location)
                        continue
                    resp.raise_for_status()
                    return resp.text
                raise RuntimeError("URL exceeded 10 redirects")
        except ValueError:
            raise
        except Exception as e_httpx:
            logger.debug(
                "httpx fetch failed for %s, falling back to requests: %s",
                url,
                e_httpx,
                exc_info=True,
            )
            try:
                import requests  # type: ignore
                current_url = url
                for _ in range(11):
                    validate_public_http_url(current_url)
                    resp = requests.get(current_url, timeout=20, allow_redirects=False, headers={
                        "User-Agent": "agentUniverse/1.0 (+https://github.com/)",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    })
                    if resp.is_redirect:
                        location = resp.headers.get("location")
                        if not location:
                            raise RuntimeError("redirect response has no Location header")
                        current_url = urljoin(current_url, location)
                        continue
                    resp.raise_for_status()
                    return resp.text
                raise RuntimeError("URL exceeded 10 redirects")
            except Exception as e_requests:
                raise RuntimeError(f"Failed to fetch url: {url}. httpx_error={e_httpx}, requests_error={e_requests}")

    def _extract_main_text(self, html: str, url: str) -> (str, dict):
        # Try trafilatura
        try:
            import trafilatura  # type: ignore
            extracted = trafilatura.extract(html, include_links=False, include_images=False)
            if extracted and extracted.strip():
                return extracted.strip(), {"extractor": "trafilatura"}
            logger.debug("trafilatura returned no content for %s; trying next extractor", url)
        except Exception as exc:
            logger.debug(
                "trafilatura extraction failed for %s, trying next extractor: %s",
                url,
                exc,
                exc_info=True,
            )

        # Fallback to readability
        try:
            from bs4 import BeautifulSoup  # type: ignore
            from readability import Document as ReadabilityDocument  # type: ignore
            article_html = ReadabilityDocument(html).summary(html_partial=True)
            soup = BeautifulSoup(article_html, "lxml")
            text = soup.get_text("\n")
            text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            if text:
                return text, {"extractor": "readability"}
            logger.debug("readability returned no content for %s; trying next extractor", url)
        except Exception as exc:
            logger.debug(
                "readability extraction failed for %s, trying next extractor: %s",
                url,
                exc,
                exc_info=True,
            )

        # Last resort: BeautifulSoup plain text
        try:
            from bs4 import BeautifulSoup  # type: ignore
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style", "noscript"]):
                tag.extract()
            text = soup.get_text("\n")
            text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            return text, {"extractor": "bs4"}
        except Exception as exc:
            raise RuntimeError(
                "Install one of the extractors: `pip install trafilatura` or "
                "`pip install readability-lxml beautifulsoup4 lxml`"
            ) from exc
