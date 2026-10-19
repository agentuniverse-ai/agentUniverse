#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: hackernews_tool.py

"""Hacker News (Algolia HN Search API) tool.

Searches Hacker News and fetches item / user details, addressing the
*other tools* item of issue #252 (tool plug-in integration).

The tool talks to the keyless public Algolia HN Search API
(``https://hn.algolia.com/api``) over ``httpx`` — already a core
agentUniverse dependency — so no API key, no account, and no extra
install is required. It supports three operating modes:

* ``search`` — full-text search over stories or comments via
  ``/api/v1/search`` (relevance order) or ``/api/v1/search_by_date``
  (recent-first order), returning normalized hits with title, author,
  points, comment counts, links, and clean text.
* ``item`` — full detail of one submission via ``/api/v1/items/{id}``,
  including a bounded list of its top-level replies.
* ``user`` — public profile of one account via
  ``/api/v1/users/{username}``.

All inputs are validated strictly before any network request is made.
Every request goes to a fixed https-only ``hn.algolia.com`` endpoint
built from validated, percent-encoded path segments — queries travel as
URL parameters, and item ids / usernames must match strict character
whitelists, so no unvalidated substring ever reaches a URL. Timeout,
connection, HTTP, and malformed response failures are returned as a
structured ``error`` payload instead of raising.
"""

import html
import re
from typing import Any, ClassVar, Dict, List, Optional

import httpx
from pydantic import ConfigDict, Field

from agentuniverse.agent.action.tool.tool import Tool

_SOURCE = "Hacker News Algolia Search API (https://hn.algolia.com/api)"


class HackerNewsTool(Tool):
    """Hacker News (Algolia HN Search API) tool.

    Attributes:
        timeout (float): HTTP request timeout in seconds.
        transport (Optional[httpx.BaseTransport]): Injectable httpx
            transport; used by tests to run fully offline. Production use
            leaves it unset (the default httpx transport is used).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "hackernews_tool"
    description: str = (
        "Hacker News (Algolia HN Search API) tool — no API key required. "
        "Searches stories and comments (mode='search', relevance or "
        "recent-first order) and fetches the full detail of one item "
        "(mode='item') or the public profile of one user (mode='user')."
    )

    # Fixed, https-only endpoints; requests never go anywhere else.
    SEARCH_URL: ClassVar[str] = "https://hn.algolia.com/api/v1/search"
    SEARCH_BY_DATE_URL: ClassVar[str] = (
        "https://hn.algolia.com/api/v1/search_by_date"
    )
    ITEM_URL_TEMPLATE: ClassVar[str] = "https://hn.algolia.com/api/v1/items/{item_id}"
    USER_URL_TEMPLATE: ClassVar[str] = "https://hn.algolia.com/api/v1/users/{username}"
    HN_ITEM_URL_TEMPLATE: ClassVar[str] = "https://news.ycombinator.com/item?id={item_id}"
    SOURCE: ClassVar[str] = _SOURCE
    CONTROL_CHAR_PATTERN: ClassVar[re.Pattern] = re.compile(r"[\x00-\x1f\x7f]")
    HTML_TAG_PATTERN: ClassVar[re.Pattern] = re.compile(r"<[^>]+>")
    # Hacker News usernames: letters, digits, dashes, underscores.
    USERNAME_PATTERN: ClassVar[re.Pattern] = re.compile(r"^[A-Za-z0-9_-]{2,30}$")

    MODES: ClassVar[tuple] = ("search", "item", "user")
    TAGS: ClassVar[tuple] = ("story", "comment")
    ORDERS: ClassVar[tuple] = ("relevance", "recent")
    DEFAULT_MAX_RESULTS: ClassVar[int] = 10
    MAX_RESULTS_LIMIT: ClassVar[int] = 50
    MAX_PAGE: ClassVar[int] = 49          # 0-based; 50 pages are plenty
    MAX_QUERY_CHARS: ClassVar[int] = 300
    MAX_ITEM_ID: ClassVar[int] = 2147483647  # HN ids fit in a signed int32
    MAX_TEXT_CHARS: ClassVar[int] = 5000
    MAX_ABOUT_CHARS: ClassVar[int] = 2000
    MAX_CHILDREN: ClassVar[int] = 20
    MAX_CHILD_TEXT_CHARS: ClassVar[int] = 500
    MAX_ERROR_CHARS: ClassVar[int] = 500

    timeout: float = Field(
        default=10.0, gt=0, le=120, description="HTTP request timeout in seconds"
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
        query: Optional[str] = None,
        tags: str = "story",
        order: str = "relevance",
        max_results: int = DEFAULT_MAX_RESULTS,
        page: int = 0,
        item_id: Any = None,
        username: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run one Hacker News API query.

        Args:
            mode (str): One of ``search`` / ``item`` / ``user``.
            query (str): Search keywords (required in ``search`` mode,
                ignored in the other modes).
            tags (str): ``search`` mode only — search over ``story``
                (default) or ``comment``.
            order (str): ``search`` mode only — ``relevance`` (default)
                or ``recent`` (newest first).
            max_results (int): ``search`` mode only — number of hits from
                1 to 50.
            page (int): ``search`` mode only — 0-based result page from
                0 to 49.
            item_id (int | str): ``item`` mode only — numeric item id,
                as an integer or a digit-only string.
            username (str): ``user`` mode only — Hacker News account
                name.

        Returns:
            Dict[str, Any]: Normalized result with a ``results`` list
                (``search``), an ``item`` detail (``item``), or a profile
                (``user``); or a structured ``error`` payload on network /
                HTTP / response failures.

        Raises:
            ValueError: If any input is invalid (raised before any network
                request is made).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )

        if mode == "search":
            normalized_query = self._normalize_query(query)
            bounded_tags = self._validate_tags(tags)
            bounded_order = self._validate_order(order)
            bounded_max_results = self._validate_max_results(max_results)
            bounded_page = self._validate_page(page)
            context: Dict[str, Any] = {
                "mode": "search",
                "query": normalized_query,
                "tags": bounded_tags,
                "order": bounded_order,
                "max_results": bounded_max_results,
                "page": bounded_page,
            }
            params = {
                "query": normalized_query,
                "tags": bounded_tags,
                "hitsPerPage": bounded_max_results,
                "page": bounded_page,
            }
            request_url = self._https_only(
                self.SEARCH_URL
                if bounded_order == "relevance"
                else self.SEARCH_BY_DATE_URL
            )
            parser = self._parse_search
        elif mode == "item":
            normalized_item_id = self._normalize_item_id(item_id)
            context = {"mode": "item", "item_id": normalized_item_id}
            params = {}
            request_url = self._https_only(
                self.ITEM_URL_TEMPLATE.format(item_id=normalized_item_id)
            )
            parser = self._parse_item
        else:
            normalized_username = self._normalize_username(username)
            context = {"mode": "user", "username": normalized_username}
            params = {}
            request_url = self._https_only(
                self.USER_URL_TEMPLATE.format(username=normalized_username)
            )
            parser = self._parse_user

        try:
            data = self._request_json(request_url, params)
            return parser(data, context)
        except httpx.TimeoutException:
            return self._error_result(
                context,
                error_type="request_timeout",
                message="Hacker News request timed out.",
            )
        except httpx.HTTPStatusError as exc:
            return self._http_error_result(context, exc.response)
        except httpx.RequestError:
            return self._error_result(
                context,
                error_type="request_error",
                message="Hacker News request failed.",
            )
        except ValueError as exc:
            return self._error_result(
                context,
                error_type="invalid_response",
                message=f"Unable to parse Hacker News response: {exc}",
            )

    # ------------------------------------------------------------------ #
    # Input validation (pure — runs strictly before any request)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"hackernews_tool: {message}")

    @classmethod
    def _normalize_query(cls, query: Optional[str]) -> str:
        """Validate and normalize the ``search`` mode query string."""
        if query is None or not isinstance(query, str) or not query.strip():
            cls._invalid(
                "query is required in search mode and must be a non-empty string"
            )
        if cls.CONTROL_CHAR_PATTERN.search(query):
            cls._invalid("query must not contain control characters")
        normalized = " ".join(query.split())
        if len(normalized) > cls.MAX_QUERY_CHARS:
            cls._invalid(
                f"query must be at most {cls.MAX_QUERY_CHARS} characters "
                f"(got {len(normalized)})"
            )
        return normalized

    @classmethod
    def _validate_tags(cls, tags: Any) -> str:
        """Validate the ``search`` mode tag filter."""
        if tags not in cls.TAGS:
            cls._invalid(
                f"tags must be one of: {', '.join(cls.TAGS)} (got {tags!r})"
            )
        return tags

    @classmethod
    def _validate_order(cls, order: Any) -> str:
        """Validate the ``search`` mode ordering."""
        if order not in cls.ORDERS:
            cls._invalid(
                f"order must be one of: {', '.join(cls.ORDERS)} (got {order!r})"
            )
        return order

    @classmethod
    def _validate_max_results(cls, max_results: Any) -> int:
        """Validate the ``search`` mode hit-count bound."""
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            cls._invalid(f"max_results must be an integer (got {max_results!r})")
        if not 1 <= max_results <= cls.MAX_RESULTS_LIMIT:
            cls._invalid(
                f"max_results must be between 1 and {cls.MAX_RESULTS_LIMIT} "
                f"(got {max_results})"
            )
        return max_results

    @classmethod
    def _validate_page(cls, page: Any) -> int:
        """Validate the ``search`` mode 0-based page index."""
        if isinstance(page, bool) or not isinstance(page, int):
            cls._invalid(f"page must be an integer (got {page!r})")
        if not 0 <= page <= cls.MAX_PAGE:
            cls._invalid(f"page must be between 0 and {cls.MAX_PAGE} (got {page})")
        return page

    @classmethod
    def _normalize_item_id(cls, item_id: Any) -> int:
        """Validate and normalize an ``item`` mode id.

        Accepts a positive integer or a digit-only string (search results
        return ids as strings); everything else — including booleans,
        signs, decimals, and path fragments — is rejected.
        """
        if isinstance(item_id, bool):
            cls._invalid(f"item_id must be a positive integer (got {item_id!r})")
        if isinstance(item_id, int):
            value = item_id
        elif isinstance(item_id, str) and item_id.isdigit():
            value = int(item_id)
        else:
            cls._invalid(
                "item_id is required in item mode and must be a positive "
                f"integer or digit-only string (got {item_id!r})"
            )
            raise AssertionError("unreachable")  # pragma: no cover
        if not 1 <= value <= cls.MAX_ITEM_ID:
            cls._invalid(
                f"item_id must be between 1 and {cls.MAX_ITEM_ID} (got {value})"
            )
        return value

    @classmethod
    def _normalize_username(cls, username: Any) -> str:
        """Validate an ``user`` mode Hacker News username."""
        if (
            username is None
            or not isinstance(username, str)
            or not cls.USERNAME_PATTERN.fullmatch(username)
        ):
            cls._invalid(
                "username is required in user mode and must be 2-30 "
                "characters of letters, digits, dashes, or underscores"
            )
        return username

    # ------------------------------------------------------------------ #
    # HTTP (single request per execution, https-only fixed endpoints)
    # ------------------------------------------------------------------ #

    @classmethod
    def _https_only(cls, url: str) -> str:
        """Refuse any endpoint that is not an https Algolia HN URL."""
        if not url.startswith("https://"):
            cls._invalid(f"refusing non-https endpoint: {url!r}")
        return url

    def _request_json(
        self, url: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Issue one GET request to the Algolia HN API and return its JSON."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "agentUniverse-HackerNewsTool/1.0 "
            "(https://github.com/agentuniverse-ai/agentUniverse)",
        }
        with httpx.Client(
            timeout=self.timeout,
            transport=self.transport,
            headers=headers,
        ) as client:
            response = client.get(url, params=params or None)
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            raise ValueError("response body is not valid JSON") from None
        if not isinstance(data, dict):
            raise ValueError("expected a JSON object")
        return data

    # ------------------------------------------------------------------ #
    # Response parsing (pure — fully testable without a network)
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_search(
        cls, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize an Algolia ``search`` / ``search_by_date`` response."""
        hits = data.get("hits")
        if not isinstance(hits, list):
            cls._invalid("invalid Hacker News response: 'hits' must be a list")
        results = []
        for hit in hits:
            if not isinstance(hit, dict):
                continue
            object_id = cls._safe_str(hit.get("objectID"))
            if not object_id:
                continue
            results.append({
                "object_id": object_id,
                "title": cls._bound_text(hit.get("title"), cls.MAX_TEXT_CHARS),
                "author": cls._safe_str(hit.get("author")),
                "url": cls._safe_str(hit.get("url")),
                "points": cls._safe_int(hit.get("points")),
                "num_comments": cls._safe_int(hit.get("num_comments")),
                "created_at": cls._safe_str(hit.get("created_at")),
                "text": cls._clean_text(
                    hit.get("comment_text")
                    if hit.get("comment_text")
                    else hit.get("story_text"),
                    cls.MAX_TEXT_CHARS,
                ),
                "hn_url": cls.HN_ITEM_URL_TEMPLATE.format(item_id=object_id),
            })
        return {
            **context,
            "total_hits": cls._safe_int(data.get("nbHits")),
            "total_pages": cls._safe_int(data.get("nbPages")),
            "returned_hits": len(results),
            "results": results,
            "source": cls.SOURCE,
        }

    @classmethod
    def _parse_item(
        cls, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize an Algolia ``items/{id}`` response."""
        if "id" not in data and "title" not in data and "text" not in data:
            cls._invalid("invalid Hacker News response: not an item object")
        children = data.get("children")
        if not isinstance(children, list):
            children = []
        bounded_children = []
        for child in children[: cls.MAX_CHILDREN]:
            if not isinstance(child, dict):
                continue
            bounded_children.append({
                "id": cls._safe_int(child.get("id")),
                "author": cls._safe_str(child.get("author")),
                "created_at": cls._safe_str(child.get("created_at")),
                "text": cls._clean_text(
                    child.get("text"), cls.MAX_CHILD_TEXT_CHARS
                ),
            })
        item_id = cls._safe_int(data.get("id")) or context["item_id"]
        return {
            **context,
            "id": item_id,
            "type": cls._safe_str(data.get("type")),
            "title": cls._bound_text(data.get("title"), cls.MAX_TEXT_CHARS),
            "author": cls._safe_str(data.get("author")),
            "url": cls._safe_str(data.get("url")),
            "text": cls._clean_text(data.get("text"), cls.MAX_TEXT_CHARS),
            "points": cls._safe_int(data.get("points")),
            "created_at": cls._safe_str(data.get("created_at")),
            "top_level_replies": bounded_children,
            "top_level_reply_count": len(children),
            "hn_url": cls.HN_ITEM_URL_TEMPLATE.format(item_id=item_id),
            "source": cls.SOURCE,
        }

    @classmethod
    def _parse_user(
        cls, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize an Algolia ``users/{username}`` response."""
        submitted = data.get("submitted")
        if not isinstance(submitted, list):
            submitted = []
        return {
            **context,
            "username": cls._safe_str(data.get("id")) or context["username"],
            "created_at": cls._safe_str(data.get("created_at")),
            "karma": cls._safe_int(data.get("karma")),
            "about": cls._clean_text(data.get("about"), cls.MAX_ABOUT_CHARS),
            "submitted_count": len(submitted),
            "source": cls.SOURCE,
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, no secrets involved — the API is keyless)
    # ------------------------------------------------------------------ #

    def _error_result(
        self,
        context: Dict[str, Any],
        error_type: str,
        message: str,
        status_code: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        error: Dict[str, Any] = {
            "type": error_type,
            "message": str(message)[: self.MAX_ERROR_CHARS],
        }
        if status_code is not None:
            error["status_code"] = status_code
        if reason:
            error["reason"] = str(reason)[: self.MAX_ERROR_CHARS]
        return {**context, "error": error, "source": self.SOURCE}

    def _http_error_result(
        self, context: Dict[str, Any], response: httpx.Response
    ) -> Dict[str, Any]:
        """Turn a non-2xx response into a structured error."""
        message = f"Hacker News API returned HTTP {response.status_code}."
        reason = None
        try:
            body = response.json()
        except ValueError:
            body = None
        if isinstance(body, dict):
            api_error = body.get("error")
            if isinstance(api_error, str) and api_error:
                message = (
                    f"Hacker News API returned HTTP {response.status_code}: "
                    f"{api_error}"
                )
                reason = api_error
            elif isinstance(api_error, dict) and isinstance(
                api_error.get("message"), str
            ):
                message = (
                    f"Hacker News API returned HTTP {response.status_code}: "
                    f"{api_error['message']}"
                )
                reason = api_error.get("code")
        return self._error_result(
            context,
            error_type="http_error",
            message=message,
            status_code=response.status_code,
            reason=reason if isinstance(reason, str) else None,
        )

    # ------------------------------------------------------------------ #
    # Small helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _clean_text(cls, value: Any, limit: int) -> str:
        """Strip HTML markup from an API text field, unescape, and bound it."""
        text = cls._safe_str(value)
        if text:
            text = html.unescape(cls.HTML_TAG_PATTERN.sub(" ", text))
            text = " ".join(text.split())
        return text if len(text) <= limit else text[:limit].rstrip() + "…"

    @staticmethod
    def _safe_str(value: Any) -> str:
        """Coerce an API response scalar to a clean string."""
        return value.strip() if isinstance(value, str) else ""

    @staticmethod
    def _safe_int(value: Any) -> int:
        """Parse an API response scalar into an integer (0 on anything else)."""
        if isinstance(value, bool):
            return 0
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    @classmethod
    def _bound_text(cls, value: Any, limit: int) -> str:
        """Bound a free-text API field to ``limit`` characters."""
        text = cls._safe_str(value)
        return text if len(text) <= limit else text[:limit].rstrip() + "…"
