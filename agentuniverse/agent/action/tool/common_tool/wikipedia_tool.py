#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: wikipedia_tool.py

"""Wikipedia (MediaWiki web service API) tool.

Searches Wikipedia and fetches page summaries / extracts, addressing the
*other tools* item of issue #252 (tool plug-in integration).

The tool talks to the keyless public MediaWiki API of a configurable
Wikipedia language edition (``https://{language}.wikipedia.org``) over
``httpx`` — already a core agentUniverse dependency — so no API key, no
account, and no extra install is required. It supports three operating
modes:

* ``search`` — full-text title/page search via ``action=query&list=search``
  returning titles, snippets, and page URLs.
* ``summary`` — the compact REST ``page/summary`` card for one page:
  title, short description, lead extract, thumbnail, and page URL.
* ``details`` — the full plain-text extract of one page via
  ``action=query&prop=extracts``, with an optional sentence or character
  limit (the MediaWiki API bounds sentences to 10 and characters to 1200).

All inputs are validated strictly before any network request is made.
Every request goes to a fixed https-only ``wikipedia.org`` endpoint built
from a validated language code. Timeout, connection, HTTP, and malformed
response failures are returned as a structured ``error`` payload instead
of raising. A missing page in ``details`` mode is a regular ``found:
False`` result rather than an error.
"""

import html
import re
from typing import Any, ClassVar, Dict, List, Optional
from urllib.parse import quote

import httpx
from pydantic import ConfigDict, Field

from agentuniverse.agent.action.tool.tool import Tool

_SOURCE = "Wikipedia MediaWiki API (https://www.mediawiki.org/wiki/API:Main_page)"


class WikipediaTool(Tool):
    """Wikipedia (MediaWiki API) tool.

    Attributes:
        language (str): Wikipedia language edition to query, e.g. ``en``,
            ``zh``, or ``pt-br``. Used to build the fixed https-only
            endpoint ``https://{language}.wikipedia.org``.
        timeout (float): HTTP request timeout in seconds.
        transport (Optional[httpx.BaseTransport]): Injectable httpx
            transport; used by tests to run fully offline. Production use
            leaves it unset (the default httpx transport is used).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "wikipedia_tool"
    description: str = (
        "Wikipedia (MediaWiki API) tool — no API key required. Searches "
        "Wikipedia (mode='search') and fetches either the short summary "
        "card (mode='summary') or the full plain-text extract with an "
        "optional sentence/character limit (mode='details') of a page, "
        "from a configurable language edition (default en)."
    )

    # Fixed, https-only endpoint templates; requests never go anywhere else.
    API_URL_TEMPLATE: ClassVar[str] = "https://{language}.wikipedia.org/w/api.php"
    SUMMARY_URL_TEMPLATE: ClassVar[str] = (
        "https://{language}.wikipedia.org/api/rest_v1/page/summary/{title}"
    )
    PAGE_URL_TEMPLATE: ClassVar[str] = "https://{language}.wikipedia.org/wiki/{title}"
    SOURCE: ClassVar[str] = _SOURCE
    LANGUAGE_PATTERN: ClassVar[re.Pattern] = re.compile(r"^[a-z]{2,3}(-[a-z0-9]{2,8})?$")
    CONTROL_CHAR_PATTERN: ClassVar[re.Pattern] = re.compile(r"[\x00-\x1f\x7f]")
    # Characters a MediaWiki page title can never contain.
    TITLE_FORBIDDEN_PATTERN: ClassVar[re.Pattern] = re.compile(r"[#<>\[\]|{}]")
    SNIPPET_TAG_PATTERN: ClassVar[re.Pattern] = re.compile(r"<[^>]+>")

    MODES: ClassVar[tuple] = ("search", "summary", "details")
    DEFAULT_MAX_RESULTS: ClassVar[int] = 5
    MAX_RESULTS_LIMIT: ClassVar[int] = 25
    MAX_QUERY_CHARS: ClassVar[int] = 300
    MAX_TITLE_CHARS: ClassVar[int] = 300
    MAX_SENTENCES: ClassVar[int] = 10          # MediaWiki API hard limit
    MAX_CHARS_PARAM: ClassVar[int] = 1200      # MediaWiki API hard limit
    MAX_EXTRACT_CHARS: ClassVar[int] = 10000
    MAX_SNIPPET_CHARS: ClassVar[int] = 500
    MAX_DESCRIPTION_CHARS: ClassVar[int] = 500
    MAX_ERROR_CHARS: ClassVar[int] = 500

    language: str = Field(
        default="en",
        pattern=r"^[a-z]{2,3}(-[a-z0-9]{2,8})?$",
        description="Wikipedia language edition, e.g. 'en', 'zh', 'pt-br'.",
    )
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
        title: Optional[str] = None,
        max_results: int = DEFAULT_MAX_RESULTS,
        sentences: Optional[int] = None,
        chars: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Run a Wikipedia API query.

        Args:
            mode (str): One of ``search`` / ``summary`` / ``details``.
            query (str): Search keywords (required in ``search`` mode,
                ignored in the other modes).
            title (str): Page title (required in ``summary`` / ``details``
                modes, ignored in ``search`` mode).
            max_results (int): Number of results in ``search`` mode, from 1
                to 25. Ignored in the other modes.
            sentences (int): ``details`` mode only — return the first 1 to
                10 sentences of the extract. Cannot be combined with
                ``chars``.
            chars (int): ``details`` mode only — return the first 1 to 1200
                characters of the extract. Cannot be combined with
                ``sentences``.

        Returns:
            Dict[str, Any]: Normalized result with a ``results`` list
                (``search``), a ``summary`` card (``summary``), or an
                ``extract`` (``details``); or a structured ``error`` payload
                on network / HTTP / response failures.

        Raises:
            ValueError: If any input is invalid (raised before any network
                request is made).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )

        context: Dict[str, Any]
        if mode == "search":
            normalized_query = self._normalize_query(query)
            bounded_max_results = self._validate_max_results(max_results)
            context = {
                "mode": "search",
                "query": normalized_query,
                "max_results": bounded_max_results,
                "language": self.language,
            }
            params = {
                "action": "query",
                "list": "search",
                "srsearch": normalized_query,
                "srlimit": bounded_max_results,
                "srprop": "snippet|wordcount|timestamp",
                "format": "json",
                "formatversion": 2,
            }
            request_url = self._api_url()
        else:
            normalized_title = self._normalize_title(title)
            context = {
                "mode": mode,
                "title": normalized_title,
                "language": self.language,
            }
            if mode == "summary":
                request_url = self._summary_url(normalized_title)
                params = {}
            else:
                request_url = self._api_url()
                params = {
                    "action": "query",
                    "prop": "extracts|info",
                    "inprop": "url",
                    "explaintext": 1,
                    "redirects": 1,
                    "titles": normalized_title,
                    "format": "json",
                    "formatversion": 2,
                }
                extract_limit = self._validate_extract_limit(sentences, chars)
                if "sentences" in extract_limit:
                    params["exsentences"] = extract_limit["sentences"]
                elif "chars" in extract_limit:
                    params["exchars"] = extract_limit["chars"]

        try:
            if mode == "summary":
                data = self._request_json(request_url, params)
                return self._parse_summary(data, context)
            data = self._request_json(request_url, params)
            if mode == "search":
                return self._parse_search(data, context)
            return self._parse_details(data, context)
        except httpx.TimeoutException:
            return self._error_result(
                context,
                error_type="request_timeout",
                message="Wikipedia request timed out.",
            )
        except httpx.HTTPStatusError as exc:
            return self._http_error_result(context, exc.response)
        except httpx.RequestError:
            return self._error_result(
                context,
                error_type="request_error",
                message="Wikipedia request failed.",
            )
        except ValueError as exc:
            return self._error_result(
                context,
                error_type="invalid_response",
                message=f"Unable to parse Wikipedia response: {exc}",
            )

    # ------------------------------------------------------------------ #
    # Input validation (pure — runs strictly before any request)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"wikipedia_tool: {message}")

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
    def _normalize_title(cls, title: Optional[str]) -> str:
        """Validate and normalize a page title for ``summary``/``details``."""
        if title is None or not isinstance(title, str) or not title.strip():
            cls._invalid(
                "title is required in summary/details mode and must be a "
                "non-empty string"
            )
        if cls.CONTROL_CHAR_PATTERN.search(title):
            cls._invalid("title must not contain control characters")
        # MediaWiki titles use spaces; underscores are equivalent.
        normalized = " ".join(title.replace("_", " ").split())
        if not normalized:
            cls._invalid(
                "title is required in summary/details mode and must be a "
                "non-empty string"
            )
        if len(normalized) > cls.MAX_TITLE_CHARS:
            cls._invalid(
                f"title must be at most {cls.MAX_TITLE_CHARS} characters "
                f"(got {len(normalized)})"
            )
        if cls.TITLE_FORBIDDEN_PATTERN.search(normalized):
            cls._invalid(
                "title must not contain any of the characters # < > [ ] | { }"
            )
        return normalized

    @classmethod
    def _validate_max_results(cls, max_results: Any) -> int:
        """Validate the ``search`` mode result-count bound."""
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            cls._invalid(f"max_results must be an integer (got {max_results!r})")
        if not 1 <= max_results <= cls.MAX_RESULTS_LIMIT:
            cls._invalid(
                f"max_results must be between 1 and {cls.MAX_RESULTS_LIMIT} "
                f"(got {max_results})"
            )
        return max_results

    @classmethod
    def _validate_extract_limit(
        cls, sentences: Any, chars: Any
    ) -> Dict[str, int]:
        """Validate the ``details`` mode extract bound.

        At most one of ``sentences`` (1-10) / ``chars`` (1-1200) may be
        given; both default to unset (full extract, bounded locally).
        """
        if sentences is None and chars is None:
            return {}
        if sentences is not None and chars is not None:
            cls._invalid(
                "pass at most one of sentences and chars, not both"
            )
        if sentences is not None:
            if isinstance(sentences, bool) or not isinstance(sentences, int):
                cls._invalid(f"sentences must be an integer (got {sentences!r})")
            if not 1 <= sentences <= cls.MAX_SENTENCES:
                cls._invalid(
                    f"sentences must be between 1 and {cls.MAX_SENTENCES} "
                    f"(got {sentences})"
                )
            return {"sentences": sentences}
        if isinstance(chars, bool) or not isinstance(chars, int):
            cls._invalid(f"chars must be an integer (got {chars!r})")
        if not 1 <= chars <= cls.MAX_CHARS_PARAM:
            cls._invalid(
                f"chars must be between 1 and {cls.MAX_CHARS_PARAM} (got {chars})"
            )
        return {"chars": chars}

    # ------------------------------------------------------------------ #
    # HTTP (single request per execution, https-only fixed endpoints)
    # ------------------------------------------------------------------ #

    def _api_url(self) -> str:
        """Build the validated https-only MediaWiki API endpoint URL."""
        return self._https_only(
            self.API_URL_TEMPLATE.format(language=self.language)
        )

    def _summary_url(self, title: str) -> str:
        """Build the validated https-only REST summary endpoint URL."""
        return self._https_only(
            self.SUMMARY_URL_TEMPLATE.format(
                language=self.language,
                title=quote(title.replace(" ", "_"), safe=""),
            )
        )

    @classmethod
    def _https_only(cls, url: str) -> str:
        """Refuse any endpoint that is not an https Wikipedia URL."""
        if not url.startswith("https://"):
            cls._invalid(f"refusing non-https endpoint: {url!r}")
        return url

    def _request_json(
        self, url: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Issue one GET request to a Wikipedia endpoint and return its JSON."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "agentUniverse-WikipediaTool/1.0 "
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
        """Normalize an ``action=query&list=search`` response."""
        query = cls._safe_dict(data.get("query"))
        items = query.get("search")
        if not isinstance(items, list):
            cls._invalid("invalid Wikipedia response: 'search' must be a list")
        results = []
        for item in items:
            if not isinstance(item, dict):
                continue
            page_title = cls._safe_str(item.get("title"))
            if not page_title:
                continue
            results.append({
                "title": page_title,
                "pageid": cls._safe_int(item.get("pageid")),
                "snippet": cls._clean_snippet(item.get("snippet")),
                "wordcount": cls._safe_int(item.get("wordcount")),
                "timestamp": cls._safe_str(item.get("timestamp")),
                "url": cls._page_url(page_title, context["language"]),
            })
        search_info = cls._safe_dict(query.get("searchinfo"))
        return {
            **context,
            "total_hits": cls._safe_int(search_info.get("totalhits")),
            "returned_results": len(results),
            "results": results,
            "source": cls.SOURCE,
        }

    @classmethod
    def _parse_summary(
        cls, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize a REST ``page/summary`` response."""
        summary = {
            **context,
            "title": cls._safe_str(data.get("title")),
            "description": cls._bound_text(
                data.get("description"), cls.MAX_DESCRIPTION_CHARS
            ),
            "extract": cls._bound_text(
                data.get("extract"), cls.MAX_EXTRACT_CHARS
            ),
            "url": cls._safe_str(
                cls._safe_dict(
                    cls._safe_dict(data.get("content_urls")).get("desktop")
                ).get("page")
            ),
            "thumbnail_url": cls._safe_str(
                cls._safe_dict(data.get("thumbnail")).get("source")
            ),
            "pageid": cls._safe_int(data.get("pageid")),
            "page_type": cls._safe_str(data.get("type")),
            "source": cls.SOURCE,
        }
        if not summary["url"]:
            summary["url"] = cls._page_url(
                summary["title"] or context["title"], context["language"]
            )
        return summary

    @classmethod
    def _parse_details(
        cls, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize an ``action=query&prop=extracts|info`` response."""
        query = cls._safe_dict(data.get("query"))
        pages = query.get("pages")
        if not isinstance(pages, list) or not pages:
            cls._invalid(
                "invalid Wikipedia response: 'pages' must be a non-empty list"
            )
        page = cls._safe_dict(pages[0])
        page_title = cls._safe_str(page.get("title")) or context["title"]
        found = "missing" not in page
        redirects = query.get("redirects")
        redirected_from = (
            cls._safe_str(cls._safe_dict(redirects[0]).get("from"))
            if isinstance(redirects, list) and redirects
            else ""
        )
        return {
            **context,
            "found": found,
            "title": page_title,
            "pageid": cls._safe_int(page.get("pageid")),
            "extract": cls._bound_text(
                page.get("extract"), cls.MAX_EXTRACT_CHARS
            ),
            "url": cls._safe_str(page.get("fullurl"))
            or cls._page_url(page_title, context["language"]),
            "redirected_from": redirected_from,
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
        message = f"Wikipedia API returned HTTP {response.status_code}."
        reason = None
        try:
            body = response.json()
        except ValueError:
            body = None
        if isinstance(body, dict):
            api_error = body.get("error")
            if isinstance(api_error, dict):
                message = (
                    f"Wikipedia API returned HTTP {response.status_code}: "
                    f"{api_error.get('info', '')}"
                )
                reason = api_error.get("code")
            elif isinstance(body.get("detail"), str):
                # REST (HyperSwitch) error bodies carry a 'detail' message.
                message = (
                    f"Wikipedia API returned HTTP {response.status_code}: "
                    f"{body['detail']}"
                )
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
    def _page_url(cls, title: str, language: str) -> str:
        """Build the canonical https page URL for a title."""
        return cls.PAGE_URL_TEMPLATE.format(
            language=language, title=quote(title.replace(" ", "_"), safe="")
        )

    @classmethod
    def _clean_snippet(cls, value: Any) -> str:
        """Strip highlight markup from a search snippet and bound it."""
        text = cls._safe_str(value)
        if text:
            text = html.unescape(cls.SNIPPET_TAG_PATTERN.sub("", text))
        return text[: cls.MAX_SNIPPET_CHARS]

    @staticmethod
    def _safe_dict(value: Any) -> Dict[str, Any]:
        """Coerce an API response fragment to a dict (empty on anything else)."""
        return value if isinstance(value, dict) else {}

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
