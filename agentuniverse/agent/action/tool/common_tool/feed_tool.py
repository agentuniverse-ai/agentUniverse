#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: feed_tool.py

"""RSS / Atom syndication feed tool.

Reads RSS 2.0 (and RSS 1.0 / RDF) and Atom feeds from a user-supplied
feed URL, addressing the *other tools* item of issue #252 (tool plug-in
integration).

Feeds are fetched over ``httpx`` — already a core agentUniverse
dependency — so no extra install is required, and parsed with the
standard-library ``xml.etree.ElementTree``. Two operating modes are
supported:

* ``headlines`` — fetch the feed and return the channel/feed title plus
  each item's title, link, publication date, and guid (bounded by
  ``limit``, default 10, maximum 50).
* ``item`` — fetch the feed and return the full record (title, link,
  date, guid, plain-text summary and content) of one item selected by
  its 1-based ``index`` or its ``guid``.

Security guards, applied before and during every fetch:

* **https-only** — plain ``http://`` (and every other scheme) is
  rejected, credentials in the URL are rejected, and every redirect
  hop is re-validated (a redirect that downgrades to ``http://`` or
  introduces credentials is refused).
* **bounded redirects** — redirects are followed manually, at most
  ``max_redirects`` (default 3) hops.
* **bounded response** — the body is streamed and aborted as soon as
  it exceeds ``max_bytes`` (default 2 MiB).
* **DTD/entity guard** — any body containing ``<!DOCTYPE`` or
  ``<!ENTITY`` (case-insensitive, even inside comments — fail closed)
  is rejected *before* parsing, blocking XXE and entity-expansion
  (billion laughs) attacks. Only well-formed, DTD-free XML reaches
  the parser.

Invalid inputs raise ``ValueError`` strictly before any network
request is made. Timeout, connection, HTTP, redirect, size-limit,
DTD-rejected, and malformed-response failures are returned as
structured ``error`` payloads instead of raising. An unknown item
index or guid is a regular ``found: False`` result rather than an
error.
"""

import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any, ClassVar, Dict, List, Optional
from urllib.parse import urljoin, urlsplit

import httpx
from pydantic import ConfigDict, Field

from agentuniverse.agent.action.tool.tool import Tool

_SOURCE = (
    "RSS 2.0 / Atom syndication feeds "
    "(https://www.rssboard.org/rss-2-0-1, "
    "https://validator.w3.org/feed/docs/atom.html)"
)


class _DtdRejected(Exception):
    """Internal marker: the body contains DTD/entity markup."""


class _ResponseTooLarge(Exception):
    """Internal marker: the streamed body exceeded ``max_bytes``."""


class _UnsafeRedirect(Exception):
    """Internal marker: a redirect hop failed the https-only rules."""


class FeedTool(Tool):
    """RSS / Atom feed reading tool.

    Attributes:
        timeout (float): HTTP request timeout in seconds.
        max_bytes (int): Maximum accepted response body size in bytes;
            the download is aborted as soon as it is exceeded.
        max_redirects (int): Maximum number of redirect hops followed
            (each hop re-validated as an https URL without credentials).
        transport (Optional[httpx.BaseTransport]): Injectable httpx
            transport; used by tests to run fully offline. Production
            use leaves it unset (the default httpx transport is used).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "feed_tool"
    description: str = (
        "RSS/Atom feed reading tool — reads any public https feed URL. "
        "mode='headlines' returns the feed title plus item titles, links, "
        "dates and guids (limit, default 10, max 50); mode='item' returns "
        "the full record of one item selected by 1-based index or guid. "
        "DTDs and XML entities are rejected; responses are size- and "
        "redirect-bounded."
    )

    MODES: ClassVar[tuple] = ("headlines", "item")
    REDIRECT_STATUSES: ClassVar[frozenset] = frozenset(
        {301, 302, 303, 307, 308}
    )
    SOURCE: ClassVar[str] = _SOURCE
    CONTROL_CHAR_PATTERN: ClassVar[re.Pattern] = re.compile(r"[\x00-\x1f\x7f]")
    TAG_PATTERN: ClassVar[re.Pattern] = re.compile(r"<[^>]+>")
    # Fail-closed pre-parse guard: reject DTDs / entity declarations.
    DOCTYPE_PATTERN: ClassVar[re.Pattern] = re.compile(rb"<!doctype", re.I)
    ENTITY_PATTERN: ClassVar[re.Pattern] = re.compile(rb"<!entity", re.I)

    DEFAULT_LIMIT: ClassVar[int] = 10
    MAX_ITEMS: ClassVar[int] = 50
    DEFAULT_MAX_BYTES: ClassVar[int] = 2 * 1024 * 1024  # 2 MiB
    MIN_MAX_BYTES: ClassVar[int] = 1024
    MAX_MAX_BYTES: ClassVar[int] = 32 * 1024 * 1024  # 32 MiB
    DEFAULT_MAX_REDIRECTS: ClassVar[int] = 3
    MAX_URL_CHARS: ClassVar[int] = 2048
    MAX_TITLE_CHARS: ClassVar[int] = 500
    MAX_DESCRIPTION_CHARS: ClassVar[int] = 500
    MAX_GUID_CHARS: ClassVar[int] = 512
    MAX_DATE_CHARS: ClassVar[int] = 100
    MAX_SUMMARY_CHARS: ClassVar[int] = 5000
    MAX_CONTENT_CHARS: ClassVar[int] = 20000
    MAX_ERROR_CHARS: ClassVar[int] = 500

    timeout: float = Field(
        default=10.0, gt=0, le=120, description="HTTP request timeout in seconds"
    )
    max_bytes: int = Field(
        default=DEFAULT_MAX_BYTES,
        ge=MIN_MAX_BYTES,
        le=MAX_MAX_BYTES,
        description="Maximum accepted response body size in bytes.",
    )
    max_redirects: int = Field(
        default=DEFAULT_MAX_REDIRECTS,
        ge=1,
        le=10,
        description="Maximum number of redirect hops followed.",
    )
    transport: Optional[httpx.BaseTransport] = Field(
        default=None,
        exclude=True,
        repr=False,
        description="Injectable httpx transport for offline testing.",
    )

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        feed_url: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
        index: Optional[int] = None,
        guid: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Read an RSS/Atom feed.

        Args:
            mode (str): One of ``headlines`` / ``item``.
            feed_url (str): https URL of the feed. Credentials in the
                URL are rejected.
            limit (int): ``headlines`` mode only — number of items to
                return, from 1 to 50 (default 10).
            index (int): ``item`` mode only — 1-based position of the
                item in the feed (as shown by ``headlines``). Cannot be
                combined with ``guid``.
            guid (str): ``item`` mode only — guid (RSS) or id (Atom) of
                the item. Cannot be combined with ``index``.

        Returns:
            Dict[str, Any]: ``headlines`` mode — feed metadata plus a
                bounded ``items`` list; ``item`` mode — the full record
                of the selected item (``found: False`` when the index
                or guid matches nothing); or a structured ``error``
                payload on network / HTTP / redirect / size / DTD /
                parse failures.

        Raises:
            ValueError: If any input is invalid (raised before any
                network request is made).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        url = self._validate_feed_url(feed_url)

        context: Dict[str, Any]
        if mode == "headlines":
            bounded_limit = self._validate_limit(limit)
            context = {"mode": "headlines", "feed_url": url, "limit": bounded_limit}
        else:
            context = {
                "mode": "item",
                "feed_url": url,
                **self._validate_selector(index, guid),
            }

        try:
            body, content_type, final_url = self._fetch(url)
            context["final_url"] = final_url
            feed = self._parse_feed(body, content_type)
            if mode == "headlines":
                return self._headlines_result(feed, context)
            return self._item_result(feed, context, index, guid)
        except httpx.TimeoutException:
            return self._error_result(
                context,
                error_type="request_timeout",
                message="Feed request timed out.",
            )
        except httpx.TooManyRedirects as exc:
            return self._error_result(
                context,
                error_type="too_many_redirects",
                message=f"Feed URL exceeded {self.max_redirects} redirects "
                f"({exc}).",
            )
        except httpx.HTTPStatusError as exc:
            return self._error_result(
                context,
                error_type="http_error",
                message=f"Feed server returned HTTP "
                f"{exc.response.status_code}.",
                status_code=exc.response.status_code,
            )
        except _UnsafeRedirect as exc:
            return self._error_result(
                context,
                error_type="unsafe_redirect",
                message=str(exc),
            )
        except _ResponseTooLarge as exc:
            return self._error_result(
                context,
                error_type="response_too_large",
                message=str(exc),
            )
        except httpx.RequestError:
            return self._error_result(
                context,
                error_type="request_error",
                message="Feed request failed.",
            )
        except _DtdRejected as exc:
            return self._error_result(
                context,
                error_type="dtd_rejected",
                message=str(exc),
            )
        except ValueError as exc:
            return self._error_result(
                context,
                error_type="invalid_response",
                message=f"Unable to parse feed: {exc}",
            )

    # ------------------------------------------------------------------ #
    # Input validation (pure — runs strictly before any request)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"feed_tool: {message}")

    @classmethod
    def _validate_feed_url(cls, feed_url: Any) -> str:
        """Validate the feed URL: https-only, no credentials, sane host."""
        if feed_url is None or not isinstance(feed_url, str) or not feed_url.strip():
            cls._invalid("feed_url is required and must be a non-empty string")
        url = feed_url.strip()
        if len(url) > cls.MAX_URL_CHARS:
            cls._invalid(
                f"feed_url must be at most {cls.MAX_URL_CHARS} characters "
                f"(got {len(url)})"
            )
        if cls.CONTROL_CHAR_PATTERN.search(url):
            cls._invalid("feed_url must not contain control characters")
        parsed = urlsplit(url)
        if parsed.scheme != "https":
            cls._invalid(
                f"feed_url must use https (got scheme {parsed.scheme!r})"
            )
        if parsed.username is not None or parsed.password is not None:
            cls._invalid("feed_url must not contain credentials")
        hostname = parsed.hostname or ""
        if not hostname or any(ch.isspace() for ch in hostname):
            cls._invalid("feed_url must include a valid host")
        try:
            parsed.port
        except ValueError:
            cls._invalid("feed_url has an invalid port")
        return url

    @classmethod
    def _validate_limit(cls, limit: Any) -> int:
        """Validate the ``headlines`` mode item-count bound."""
        if isinstance(limit, bool) or not isinstance(limit, int):
            cls._invalid(f"limit must be an integer (got {limit!r})")
        if not 1 <= limit <= cls.MAX_ITEMS:
            cls._invalid(
                f"limit must be between 1 and {cls.MAX_ITEMS} (got {limit})"
            )
        return limit

    @classmethod
    def _validate_selector(
        cls, index: Any, guid: Any
    ) -> Dict[str, Any]:
        """Validate the ``item`` mode selector: index xor guid."""
        if index is not None and guid is not None:
            cls._invalid("pass at most one of index and guid, not both")
        if index is not None:
            if isinstance(index, bool) or not isinstance(index, int):
                cls._invalid(f"index must be an integer (got {index!r})")
            if index < 1:
                cls._invalid(f"index must be >= 1 (got {index})")
            return {"index": index}
        if guid is None or not isinstance(guid, str) or not guid.strip():
            cls._invalid(
                "item mode requires either a 1-based index or a non-empty guid"
            )
        normalized = " ".join(guid.split())
        if len(normalized) > cls.MAX_GUID_CHARS:
            cls._invalid(
                f"guid must be at most {cls.MAX_GUID_CHARS} characters "
                f"(got {len(normalized)})"
            )
        return {"guid": normalized}

    # ------------------------------------------------------------------ #
    # HTTP (streamed, byte-bounded, manually bounded https-only redirects)
    # ------------------------------------------------------------------ #

    def _fetch(self, url: str) -> tuple:
        """GET the feed, enforcing the byte cap and redirect rules.

        Returns a ``(body_bytes, content_type, final_url)`` tuple.

        Raises:
            _ResponseTooLarge: The streamed body exceeded ``max_bytes``.
            _UnsafeRedirect: A redirect hop violated the https-only
                rules (non-https target, credentials, missing target).
            httpx.TooManyRedirects: More than ``max_redirects`` hops.
            httpx.HTTPStatusError: Non-2xx final status.
            httpx.RequestError / httpx.TimeoutException: Transport
                failures.
        """
        headers = {
            "Accept": (
                "application/rss+xml, application/atom+xml, application/xml,"
                " text/xml;q=0.9, */*;q=0.1"
            ),
            "User-Agent": "agentUniverse-FeedTool/1.0 "
            "(https://github.com/agentuniverse-ai/agentUniverse)",
        }
        current = url
        with httpx.Client(
            timeout=self.timeout,
            transport=self.transport,
            headers=headers,
            follow_redirects=False,
        ) as client:
            for _ in range(self.max_redirects + 1):
                with client.stream("GET", current) as response:
                    if response.status_code in self.REDIRECT_STATUSES:
                        location = response.headers.get("location", "").strip()
                        if not location:
                            raise _UnsafeRedirect(
                                "feed server sent a redirect without a "
                                "Location header"
                            )
                        target = urljoin(current, location)
                        try:
                            target = self._validate_feed_url(target)
                        except ValueError as exc:
                            raise _UnsafeRedirect(
                                f"redirect target rejected: {exc}"
                            ) from None
                        current = target
                        continue
                    response.raise_for_status()
                    content_type = response.headers.get("content-type", "")
                    chunks: List[bytes] = []
                    received = 0
                    for chunk in response.iter_bytes():
                        received += len(chunk)
                        if received > self.max_bytes:
                            raise _ResponseTooLarge(
                                f"feed response exceeded the "
                                f"{self.max_bytes}-byte limit"
                            )
                        chunks.append(chunk)
                    return b"".join(chunks), content_type, current
        raise httpx.TooManyRedirects(
            f"feed URL exceeded {self.max_redirects} redirect hops"
        )

    # ------------------------------------------------------------------ #
    # Parsing (stdlib xml.etree with a fail-closed DTD/entity guard)
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_feed(cls, body: bytes, content_type: str) -> Dict[str, Any]:
        """Validate, guard, and parse the feed body into a normalized dict.

        Raises:
            ValueError: Non-XML content type, non-well-formed XML, or an
                unexpected root element.
            _DtdRejected: The body contains ``<!DOCTYPE`` or ``<!ENTITY``.
        """
        media_type = content_type.split(";", 1)[0].strip().lower()
        if media_type and "xml" not in media_type:
            raise ValueError(
                f"non-XML Content-Type {media_type!r} (expected an XML type)"
            )
        # Fail-closed pre-scan: reject DTDs and entity declarations
        # before anything reaches the XML parser. Matches inside
        # comments are rejected too — the guard errs on the side of
        # safety (XXE / billion-laughs defence).
        found_tokens = [
            token
            for token, pattern in (
                ("<!DOCTYPE", cls.DOCTYPE_PATTERN),
                ("<!ENTITY", cls.ENTITY_PATTERN),
            )
            if pattern.search(body)
        ]
        if found_tokens:
            raise _DtdRejected(
                f"feed contains {', '.join(found_tokens)}; DTDs and XML "
                f"entity declarations are rejected"
            )
        try:
            root = ET.fromstring(body)
        except ET.ParseError as exc:
            raise ValueError(f"feed is not well-formed XML: {exc}") from None
        root_name = cls._local_name(root.tag)
        if root_name in ("rss", "RDF"):
            return cls._build_feed(root, feed_type="rss")
        if root_name == "feed":
            return cls._build_feed(root, feed_type="atom")
        raise ValueError(
            f"unexpected root element {str(root.tag)!r}; expected "
            f"<rss> or <feed>"
        )

    @classmethod
    def _build_feed(
        cls, root: ET.Element, feed_type: str
    ) -> Dict[str, Any]:
        """Normalize an RSS or Atom document into the common feed dict."""
        if feed_type == "rss":
            channel = cls._child_by_name(root, "channel")
            source = channel if channel is not None else root
            description = cls._child_by_name(source, "description")
            if description is None:
                description = cls._child_by_name(source, "subtitle")
            feed = {
                "feed_type": "rss",
                "feed_title": cls._clean_text(
                    cls._child_by_name(source, "title"), cls.MAX_TITLE_CHARS
                ),
                "feed_link": cls._rss_link(source),
                "feed_description": cls._clean_text(
                    description, cls.MAX_DESCRIPTION_CHARS
                ),
            }
            item_name, parser = "item", cls._parse_rss_item
        else:
            feed = {
                "feed_type": "atom",
                "feed_title": cls._clean_text(
                    cls._child_by_name(root, "title"), cls.MAX_TITLE_CHARS
                ),
                "feed_link": cls._atom_link(root),
                "feed_description": cls._clean_text(
                    cls._child_by_name(root, "subtitle"),
                    cls.MAX_DESCRIPTION_CHARS,
                ),
            }
            item_name, parser = "entry", cls._parse_atom_entry

        elements = [
            element
            for element in root.iter()
            if cls._local_name(element.tag) == item_name
        ]
        items = [
            {"index": position, **parser(element)}
            for position, element in enumerate(elements[: cls.MAX_ITEMS], 1)
        ]
        return {
            **feed,
            "total_items": len(elements),
            "items_truncated": len(elements) > cls.MAX_ITEMS,
            "items": items,
        }

    @classmethod
    def _published_element(cls, element: ET.Element, *names: str):
        """Find the first present child element among ``names``.

        ElementTree elements are falsy when childless, so presence is
        checked against ``None`` explicitly.
        """
        for name in names:
            found = cls._child_by_name(element, name)
            if found is not None:
                return found
        return None

    @classmethod
    def _parse_rss_item(cls, element: ET.Element) -> Dict[str, Any]:
        """Normalize one RSS ``<item>`` (2.0, or RSS 1.0 item)."""
        published = cls._published_element(element, "pubDate", "date")
        return {
            "title": cls._clean_text(
                cls._child_by_name(element, "title"), cls.MAX_TITLE_CHARS
            ),
            "link": cls._rss_link(element)[: cls.MAX_URL_CHARS],
            "published": cls._normalize_date(
                cls._plain_text(published), cls.MAX_DATE_CHARS
            ),
            "guid": cls._clean_text(
                cls._child_by_name(element, "guid"), cls.MAX_GUID_CHARS
            ),
            "summary": cls._clean_text(
                cls._child_by_name(element, "description"),
                cls.MAX_SUMMARY_CHARS,
            ),
            "content": cls._clean_text(
                cls._child_by_name(element, "encoded"), cls.MAX_CONTENT_CHARS
            ),
        }

    @classmethod
    def _parse_atom_entry(cls, element: ET.Element) -> Dict[str, Any]:
        """Normalize one Atom ``<entry>``."""
        published = cls._published_element(element, "published", "updated")
        return {
            "title": cls._clean_text(
                cls._child_by_name(element, "title"), cls.MAX_TITLE_CHARS
            ),
            "link": cls._atom_link(element)[: cls.MAX_URL_CHARS],
            "published": cls._normalize_date(
                cls._plain_text(published), cls.MAX_DATE_CHARS
            ),
            "guid": cls._clean_text(
                cls._child_by_name(element, "id"), cls.MAX_GUID_CHARS
            ),
            "summary": cls._clean_text(
                cls._child_by_name(element, "summary"), cls.MAX_SUMMARY_CHARS
            ),
            "content": cls._clean_text(
                cls._child_by_name(element, "content"), cls.MAX_CONTENT_CHARS
            ),
        }

    # ------------------------------------------------------------------ #
    # Result builders
    # ------------------------------------------------------------------ #

    @classmethod
    def _headlines_result(
        cls, feed: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build the ``headlines`` mode payload."""
        visible = feed["items"][: context["limit"]]
        items = [
            {
                "index": item["index"],
                "title": item["title"],
                "link": item["link"],
                "published": item["published"],
                "guid": item["guid"],
            }
            for item in visible
        ]
        return {
            **context,
            "feed_type": feed["feed_type"],
            "feed_title": feed["feed_title"],
            "feed_link": feed["feed_link"],
            "total_items": feed["total_items"],
            "items_truncated": feed["items_truncated"],
            "returned_items": len(items),
            "items": items,
            "source": cls.SOURCE,
        }

    @classmethod
    def _item_result(
        cls,
        feed: Dict[str, Any],
        context: Dict[str, Any],
        index: Optional[int],
        guid: Optional[str],
    ) -> Dict[str, Any]:
        """Build the ``item`` mode payload (``found: False`` if no match)."""
        if guid is not None:
            match = next(
                (
                    item
                    for item in feed["items"]
                    if item["guid"] and item["guid"] == guid
                ),
                None,
            )
        else:
            match = next(
                (item for item in feed["items"] if item["index"] == index),
                None,
            )
        result: Dict[str, Any] = {
            **context,
            "feed_type": feed["feed_type"],
            "feed_title": feed["feed_title"],
            "found": match is not None,
            "source": cls.SOURCE,
        }
        if match is not None:
            result["item"] = match
        return result

    # ------------------------------------------------------------------ #
    # Error payloads (structured)
    # ------------------------------------------------------------------ #

    def _error_result(
        self,
        context: Dict[str, Any],
        error_type: str,
        message: str,
        status_code: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        error: Dict[str, Any] = {
            "type": error_type,
            "message": str(message)[: self.MAX_ERROR_CHARS],
        }
        if status_code is not None:
            error["status_code"] = status_code
        return {**context, "error": error, "source": self.SOURCE}

    # ------------------------------------------------------------------ #
    # Small helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _local_name(tag: Any) -> str:
        """Strip the XML namespace from an element tag."""
        if not isinstance(tag, str):
            return ""
        return tag.rsplit("}", 1)[-1]

    @classmethod
    def _child_by_name(
        cls, parent: Optional[ET.Element], name: str
    ) -> Optional[ET.Element]:
        """Find the first direct child element with the local ``name``."""
        if parent is None:
            return None
        for child in parent:
            if cls._local_name(child.tag) == name:
                return child
        return None

    @classmethod
    def _rss_link(cls, parent: Optional[ET.Element]) -> str:
        """Extract a link from an RSS channel/item.

        Prefers the plain, namespace-less ``<link>`` element; falls back
        to an ``atom:link`` with ``rel="alternate"`` or no ``rel``.
        """
        plain = fallback = ""
        for child in parent or ():
            if cls._local_name(child.tag) != "link":
                continue
            if child.tag == "link":
                if not plain:
                    plain = (child.text or "").strip()
            elif child.get("rel") in (None, "alternate"):
                if not fallback:
                    fallback = (child.get("href") or "").strip()
        return plain or fallback

    @classmethod
    def _atom_link(cls, parent: Optional[ET.Element]) -> str:
        """Extract the best link from an Atom feed/entry.

        Preference: ``rel="alternate"`` > no ``rel`` > first link.
        """
        alternate = no_rel = first = ""
        for child in parent or ():
            if cls._local_name(child.tag) != "link":
                continue
            href = (child.get("href") or "").strip()
            rel = child.get("rel")
            if rel == "alternate":
                if not alternate:
                    alternate = href
            elif rel is None:
                if not no_rel:
                    no_rel = href
            elif not first:
                first = href
        return alternate or no_rel or first

    @classmethod
    def _plain_text(cls, element: Optional[ET.Element]) -> str:
        """Raw text content of an element (no cleaning, just stripped)."""
        if element is None:
            return ""
        return "".join(element.itertext()).strip()

    @classmethod
    def _clean_text(cls, element: Optional[ET.Element], limit: int) -> str:
        """Turn an element's content into bounded, plain, unescaped text.

        Handles HTML carried inside descriptions / encoded content:
        nested markup text is joined, leftover HTML tags are stripped,
        entities are unescaped, and whitespace is collapsed.
        """
        if element is None:
            return ""
        text = "".join(element.itertext())
        text = html.unescape(cls.TAG_PATTERN.sub("", text))
        text = " ".join(text.split())
        return text if len(text) <= limit else text[:limit].rstrip() + "…"

    @classmethod
    def _normalize_date(cls, raw: str, limit: int) -> str:
        """Best-effort date normalization to ISO 8601 (raw kept on failure).

        RSS ``pubDate`` values are RFC 822 dates; Atom dates are ISO
        8601. Both parse paths are stdlib-only.
        """
        text = (raw or "").strip()
        if not text:
            return ""
        parsed = None
        try:
            parsed = parsedate_to_datetime(text)
        except (TypeError, ValueError):
            try:
                parsed = datetime.fromisoformat(
                    text.replace("Z", "+00:00")
                )
            except ValueError:
                parsed = None
        if parsed is not None:
            try:
                return parsed.isoformat()
            except ValueError:
                pass
        return text[:limit]
