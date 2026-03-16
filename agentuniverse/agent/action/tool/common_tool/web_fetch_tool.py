# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/15 10:00
# @FileName: web_fetch_tool.py

"""Web fetch tool — fetch a URL and extract readable content.

Replicates the openclaw web_fetch logic:
  1. HTTP GET with browser-like User-Agent (via httpx)
  2. SSRF guard: reject private/loopback IPs
  3. Manual redirect following (max 3) with cross-origin header filtering
  4. Content extraction chain:
     - text/markdown → use as-is
     - text/html    → readability-lxml → fallback to bs4 tag-stripping
     - application/json → pretty-print
     - other        → raw text
  5. In-memory TTL cache (15 min, max 100 entries)
  6. Character-level truncation
"""

from __future__ import annotations

import ipaddress
import json
import re
import socket
import time
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

import httpx
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_2) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_REDIRECTS = 3
DEFAULT_MAX_RESPONSE_BYTES = 2 * 1024 * 1024  # 2 MB
DEFAULT_MAX_CHARS = 60_000
DEFAULT_CACHE_TTL_SECONDS = 900  # 15 min
MAX_CACHE_ENTRIES = 100

# Headers safe to forward on cross-origin redirects
_CROSS_ORIGIN_SAFE_HEADERS = {
    "accept", "accept-encoding", "accept-language", "cache-control",
    "content-language", "content-type", "user-agent",
}

# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------

_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}


def _cache_get(key: str) -> Optional[Dict[str, Any]]:
    entry = _cache.get(key)
    if entry is None:
        return None
    ts, value = entry
    if time.monotonic() - ts > DEFAULT_CACHE_TTL_SECONDS:
        _cache.pop(key, None)
        return None
    return value


def _cache_put(key: str, value: Dict[str, Any]) -> None:
    # Evict oldest if full
    if len(_cache) >= MAX_CACHE_ENTRIES:
        oldest_key = min(_cache, key=lambda k: _cache[k][0])
        _cache.pop(oldest_key, None)
    _cache[key] = (time.monotonic(), value)


# ---------------------------------------------------------------------------
# SSRF guard
# ---------------------------------------------------------------------------

def _is_private_ip(hostname: str) -> bool:
    """Resolve hostname and reject private/loopback/link-local addresses."""
    try:
        infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror:
        return False
    for family, _, _, _, sockaddr in infos:
        ip = ipaddress.ip_address(sockaddr[0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return True
    return False


# ---------------------------------------------------------------------------
# Content extraction helpers
# ---------------------------------------------------------------------------

_INVISIBLE_RE = re.compile(
    "[\u00ad\u034f\u061c\u200b-\u200f\u2028-\u202f"
    "\u2060-\u2069\u206a-\u206f\ufeff\ufff9-\ufffb]"
)


def _strip_invisible(text: str) -> str:
    return _INVISIBLE_RE.sub("", text)


def _normalize_ws(text: str) -> str:
    text = text.replace("\r", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _html_to_markdown(html: str) -> Tuple[str, Optional[str]]:
    """Lightweight HTML→Markdown without external Markdown libs."""
    title_m = re.search(r"<title[^>]*>([\s\S]*?)</title>", html, re.I)
    title = _normalize_ws(re.sub(r"<[^>]+>", "", title_m.group(1))) if title_m else None

    text = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.I)
    text = re.sub(r"<noscript[\s\S]*?</noscript>", "", text, flags=re.I)

    # links → [label](href)
    def _link(m: re.Match) -> str:
        href, body = m.group(1), m.group(2)
        label = _normalize_ws(re.sub(r"<[^>]+>", "", body))
        return f"[{label}]({href})" if label else href

    text = re.sub(
        r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',
        _link, text, flags=re.I,
    )
    # headings
    text = re.sub(
        r"<h([1-6])[^>]*>([\s\S]*?)</h\1>",
        lambda m: "\n{} {}\n".format(
            "#" * max(1, min(6, int(m.group(1)))),
            _normalize_ws(re.sub(r"<[^>]+>", "", m.group(2))),
        ),
        text, flags=re.I,
    )
    # list items
    text = re.sub(
        r"<li[^>]*>([\s\S]*?)</li>",
        lambda m: "\n- " + _normalize_ws(re.sub(r"<[^>]+>", "", m.group(1))),
        text, flags=re.I,
    )
    text = re.sub(r"<(br|hr)\s*/?>", "\n", text, flags=re.I)
    text = re.sub(
        r"</(p|div|section|article|header|footer|table|tr|ul|ol)>",
        "\n", text, flags=re.I,
    )
    text = re.sub(r"<[^>]+>", "", text)
    text = _normalize_ws(text)
    return text, title


def _markdown_to_text(md: str) -> str:
    text = re.sub(r"!\[[^\]]*]\([^)]+\)", "", md)
    text = re.sub(r"\[([^\]]+)]\([^)]+\)", r"\1", text)
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.M)
    return _normalize_ws(text)


def _extract_with_readability(html: str, url: str) -> Tuple[Optional[str], Optional[str]]:
    """Use readability-lxml to extract article content. Returns (text, title) or (None, None)."""
    try:
        from readability import Document
        doc = Document(html, url=url)
        title = doc.short_title() or None
        summary_html = doc.summary()
        if not summary_html:
            return None, title
        content, _ = _html_to_markdown(summary_html)
        content = _strip_invisible(content)
        return (content, title) if content else (None, title)
    except Exception:
        return None, None


def _extract_content(
    body: str,
    content_type: str,
    url: str,
    extract_mode: str,
) -> Tuple[str, Optional[str], str]:
    """Extract readable content. Returns (text, title, extractor_name)."""
    if "text/markdown" in content_type:
        if extract_mode == "text":
            return _strip_invisible(_markdown_to_text(body)), None, "cf-markdown"
        return _strip_invisible(body), None, "cf-markdown"

    if "text/html" in content_type:
        # Try readability first
        text, title = _extract_with_readability(body, url)
        if text:
            if extract_mode == "text":
                text = _markdown_to_text(text)
            return _strip_invisible(text), title, "readability"
        # Fallback: regex-based tag stripping
        md_text, title = _html_to_markdown(body)
        if extract_mode == "text":
            md_text = _markdown_to_text(md_text)
        return _strip_invisible(md_text), title, "html-fallback"

    if "application/json" in content_type:
        try:
            pretty = json.dumps(json.loads(body), indent=2, ensure_ascii=False)
            return pretty, None, "json"
        except (json.JSONDecodeError, ValueError):
            return body, None, "raw"

    return _strip_invisible(body), None, "raw"


def _truncate(text: str, max_chars: int) -> Tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars], True


# ---------------------------------------------------------------------------
# HTTP fetch with redirect tracking & SSRF guard
# ---------------------------------------------------------------------------

async def _guarded_fetch(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    max_redirects: int = DEFAULT_MAX_REDIRECTS,
    user_agent: str = DEFAULT_USER_AGENT,
) -> Tuple[httpx.Response, str]:
    """Fetch *url* with SSRF guard and manual redirect following.

    Returns (response, final_url).
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Invalid URL: must be http or https")
    if _is_private_ip(parsed.hostname or ""):
        raise PermissionError(f"SSRF blocked: {parsed.hostname} resolves to a private address")

    headers = {
        "Accept": "text/markdown, text/html;q=0.9, */*;q=0.1",
        "User-Agent": user_agent,
        "Accept-Language": "en-US,en;q=0.9",
    }

    visited: set[str] = set()
    current_url = url
    redirect_count = 0

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
        while True:
            resp = await client.get(current_url, headers=headers)

            if resp.status_code not in (301, 302, 303, 307, 308):
                return resp, current_url

            location = resp.headers.get("location")
            if not location:
                raise RuntimeError(f"Redirect missing Location header ({resp.status_code})")

            redirect_count += 1
            if redirect_count > max_redirects:
                raise RuntimeError(f"Too many redirects (limit: {max_redirects})")

            # Resolve relative redirects
            next_parsed = urlparse(location)
            if not next_parsed.scheme:
                from urllib.parse import urljoin
                location = urljoin(current_url, location)
                next_parsed = urlparse(location)

            if location in visited:
                raise RuntimeError("Redirect loop detected")
            visited.add(location)

            # SSRF check on redirect target
            if _is_private_ip(next_parsed.hostname or ""):
                raise PermissionError(
                    f"SSRF blocked on redirect: {next_parsed.hostname} is private"
                )

            # Strip sensitive headers on cross-origin redirect
            cur_origin = urlparse(current_url)
            if next_parsed.netloc != cur_origin.netloc:
                headers = {
                    k: v for k, v in headers.items()
                    if k.lower() in _CROSS_ORIGIN_SAFE_HEADERS
                }

            current_url = location


def _guarded_fetch_sync(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    max_redirects: int = DEFAULT_MAX_REDIRECTS,
    user_agent: str = DEFAULT_USER_AGENT,
) -> Tuple[httpx.Response, str]:
    """Synchronous version of :func:`_guarded_fetch`."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Invalid URL: must be http or https")
    if _is_private_ip(parsed.hostname or ""):
        raise PermissionError(f"SSRF blocked: {parsed.hostname} resolves to a private address")

    headers = {
        "Accept": "text/markdown, text/html;q=0.9, */*;q=0.1",
        "User-Agent": user_agent,
        "Accept-Language": "en-US,en;q=0.9",
    }

    visited: set[str] = set()
    current_url = url
    redirect_count = 0

    with httpx.Client(timeout=timeout, follow_redirects=False) as client:
        while True:
            resp = client.get(current_url, headers=headers)

            if resp.status_code not in (301, 302, 303, 307, 308):
                return resp, current_url

            location = resp.headers.get("location")
            if not location:
                raise RuntimeError(f"Redirect missing Location header ({resp.status_code})")

            redirect_count += 1
            if redirect_count > max_redirects:
                raise RuntimeError(f"Too many redirects (limit: {max_redirects})")

            next_parsed = urlparse(location)
            if not next_parsed.scheme:
                from urllib.parse import urljoin
                location = urljoin(current_url, location)
                next_parsed = urlparse(location)

            if location in visited:
                raise RuntimeError("Redirect loop detected")
            visited.add(location)

            if _is_private_ip(next_parsed.hostname or ""):
                raise PermissionError(
                    f"SSRF blocked on redirect: {next_parsed.hostname} is private"
                )

            cur_origin = urlparse(current_url)
            if next_parsed.netloc != cur_origin.netloc:
                headers = {
                    k: v for k, v in headers.items()
                    if k.lower() in _CROSS_ORIGIN_SAFE_HEADERS
                }

            current_url = location


# ---------------------------------------------------------------------------
# Shared result builder
# ---------------------------------------------------------------------------

def _build_result(
    url: str,
    final_url: str,
    resp: httpx.Response,
    extract_mode: str,
    effective_max_chars: int,
    max_response_bytes: int,
    start: float,
) -> str:
    """Shared logic for both sync and async paths."""
    if not resp.is_success:
        return f"Error: HTTP {resp.status_code} for {url}"

    body = resp.text
    if len(body.encode("utf-8", errors="replace")) > max_response_bytes:
        body = body[:max_response_bytes]

    content_type = resp.headers.get("content-type", "application/octet-stream")
    text, title, extractor = _extract_content(body, content_type, final_url, extract_mode)
    text, truncated = _truncate(text, effective_max_chars)
    elapsed_ms = int((time.monotonic() - start) * 1000)

    parts = []
    if title:
        parts.append(f"Title: {title}")
    parts.append(f"URL: {final_url}")
    parts.append(f"Extractor: {extractor} | Chars: {len(text)} | Time: {elapsed_ms}ms")
    if truncated:
        parts.append(f"(truncated to {effective_max_chars} chars)")
    parts.append("")
    parts.append(text)
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Tool class
# ---------------------------------------------------------------------------

class WebFetchTool(Tool):
    """Fetch a web page and return its readable content.

    Extraction chain: Readability → HTML regex fallback → raw text.
    Includes SSRF protection, redirect following, and in-memory caching.
    """

    timeout_seconds: int = Field(default=DEFAULT_TIMEOUT_SECONDS)
    max_redirects: int = Field(default=DEFAULT_MAX_REDIRECTS)
    max_response_bytes: int = Field(default=DEFAULT_MAX_RESPONSE_BYTES)
    max_chars: int = Field(default=DEFAULT_MAX_CHARS)
    user_agent: str = Field(default=DEFAULT_USER_AGENT)

    def execute(
        self,
        url: str,
        extract_mode: str = "markdown",
        max_chars: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Synchronous fetch — same logic as :meth:`async_execute`."""
        effective_max_chars = int(max_chars) if max_chars is not None else self.max_chars
        cache_key = f"fetch:{url}:{extract_mode}:{effective_max_chars}"

        cached = _cache_get(cache_key)
        if cached is not None:
            return cached["text"]

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return "Error: URL must use http or https scheme."

        start = time.monotonic()
        try:
            resp, final_url = _guarded_fetch_sync(
                url,
                timeout=self.timeout_seconds,
                max_redirects=self.max_redirects,
                user_agent=self.user_agent,
            )
        except PermissionError as exc:
            return f"Error (SSRF blocked): {exc}"
        except Exception as exc:
            return f"Error fetching URL: {exc}"

        result_text = _build_result(
            url, final_url, resp, extract_mode,
            effective_max_chars, self.max_response_bytes, start,
        )
        _cache_put(cache_key, {"text": result_text})
        return result_text

    async def async_execute(
        self,
        url: str,
        extract_mode: str = "markdown",
        max_chars: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Asynchronous fetch — same logic as :meth:`execute`."""
        effective_max_chars = int(max_chars) if max_chars is not None else self.max_chars
        cache_key = f"fetch:{url}:{extract_mode}:{effective_max_chars}"

        cached = _cache_get(cache_key)
        if cached is not None:
            return cached["text"]

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return "Error: URL must use http or https scheme."

        start = time.monotonic()
        try:
            resp, final_url = await _guarded_fetch(
                url,
                timeout=self.timeout_seconds,
                max_redirects=self.max_redirects,
                user_agent=self.user_agent,
            )
        except PermissionError as exc:
            return f"Error (SSRF blocked): {exc}"
        except Exception as exc:
            return f"Error fetching URL: {exc}"

        result_text = _build_result(
            url, final_url, resp, extract_mode,
            effective_max_chars, self.max_response_bytes, start,
        )
        _cache_put(cache_key, {"text": result_text})
        return result_text

