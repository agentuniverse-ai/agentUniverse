#!/usr/bin/env python3

"""First-class DuckDuckGo search tool for agentUniverse.

The project already demonstrates DuckDuckGo through the generic LangChain tool
adapter. This component provides a native agentUniverse implementation with a
stable, structured response contract, runtime validation, text/news modes,
proxy support, and an asynchronous entry point that does not block the event
loop.
"""

import asyncio
from typing import Any, Literal

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env

try:
    from duckduckgo_search import DDGS
except ImportError as import_error:
    DDGS = None
    _DDGS_IMPORT_ERROR = import_error
else:
    _DDGS_IMPORT_ERROR = None


SearchType = Literal["text", "news"]
SafeSearch = Literal["on", "moderate", "off"]
TimeLimit = Literal["d", "w", "m", "y"]

_ALLOWED_SEARCH_TYPES = {"text", "news"}
_ALLOWED_SAFESEARCH = {"on", "moderate", "off"}
_ALLOWED_TIMELIMITS = {"d", "w", "m", "y"}


class DuckDuckGoSearchTool(Tool):
    """Search DuckDuckGo without an API key.

    Attributes:
        max_results: Default maximum result count, from 1 through 20.
        region: Optional DuckDuckGo region such as ``us-en`` or ``cn-zh``.
        safesearch: Default safe-search policy.
        search_type: Default operation, either ``text`` or ``news``.
        timelimit: Optional recency window: day, week, month, or year.
        backend: DuckDuckGo text-search backend. News search ignores it.
        proxy: Optional HTTP/SOCKS proxy URL.
        timeout: Client timeout in seconds.
    """

    description: str = (
        "Search DuckDuckGo without an API key. Supports web and news search and returns structured result metadata."
    )
    max_results: int = Field(default=5, ge=1, le=20)
    region: str | None = None
    safesearch: SafeSearch = "moderate"
    search_type: SearchType = "text"
    timelimit: TimeLimit | None = None
    backend: str = "auto"
    proxy: str | None = Field(default_factory=lambda: get_from_env("DUCKDUCKGO_PROXY"))
    timeout: int = Field(default=10, ge=1, le=120)

    def execute(
        self,
        input: str,  # noqa: A002
        search_type: str | None = None,
        max_results: int | None = None,
        region: str | None = None,
        safesearch: str | None = None,
        timelimit: str | None = None,
        backend: str | None = None,
    ) -> dict[str, Any]:
        """Run a text or news search.

        Args:
            input: Non-empty search query.
            search_type: ``text`` or ``news``. Uses the configured default when
                omitted.
            max_results: Maximum number of results, from 1 through 20.
            region: DuckDuckGo region code. An empty value uses the library
                default.
            safesearch: ``on``, ``moderate``, or ``off``.
            timelimit: Optional recency filter: ``d``, ``w``, ``m``, or ``y``.
            backend: Text-search backend. Ignored by news search.

        Returns:
            A dictionary with ``status``, request context, ``count``, and a
            normalized ``results`` list. Failures return the same stable shape
            with ``status=error`` and no fabricated search results.
        """
        try:
            options = self._validate_options(
                query=input,
                search_type=search_type,
                max_results=max_results,
                region=region,
                safesearch=safesearch,
                timelimit=timelimit,
                backend=backend,
            )
        except (TypeError, ValueError) as error:
            return self._error_response(input, "validation_error", str(error))

        if DDGS is None:
            message = (
                "The 'duckduckgo-search' dependency is unavailable. Install "
                "the project dependencies or run 'pip install duckduckgo-search'."
            )
            if _DDGS_IMPORT_ERROR:
                message = f"{message} Import error: {_DDGS_IMPORT_ERROR}"
            return self._error_response(options["query"], "dependency_error", message, options)

        try:
            raw_results = self._perform_search(options)
        except Exception as error:  # third-party network/client exceptions vary
            return self._error_response(options["query"], "search_error", str(error), options)

        results = [self._normalize_result(result, options["search_type"]) for result in raw_results]
        return {
            "status": "success",
            "query": options["query"],
            "search_type": options["search_type"],
            "region": options["region"],
            "safesearch": options["safesearch"],
            "timelimit": options["timelimit"],
            "count": len(results),
            "results": results,
        }

    async def async_execute(
        self,
        input: str,  # noqa: A002
        search_type: str | None = None,
        max_results: int | None = None,
        region: str | None = None,
        safesearch: str | None = None,
        timelimit: str | None = None,
        backend: str | None = None,
    ) -> dict[str, Any]:
        """Run :meth:`execute` in a worker thread."""
        return await asyncio.to_thread(
            self.execute,
            input,
            search_type,
            max_results,
            region,
            safesearch,
            timelimit,
            backend,
        )

    def _validate_options(  # noqa: C901
        self,
        query: str,
        search_type: str | None,
        max_results: int | None,
        region: str | None,
        safesearch: str | None,
        timelimit: str | None,
        backend: str | None,
    ) -> dict[str, Any]:
        """Resolve call overrides and validate the complete request."""
        if not isinstance(query, str):
            raise TypeError("input must be a string")  # noqa: TRY003
        query = query.strip()
        if not query:
            raise ValueError("input must not be empty")  # noqa: TRY003

        resolved_type = search_type or self.search_type
        if resolved_type not in _ALLOWED_SEARCH_TYPES:
            raise ValueError("search_type must be one of: text, news")  # noqa: TRY003

        resolved_safesearch = safesearch or self.safesearch
        if resolved_safesearch not in _ALLOWED_SAFESEARCH:
            raise ValueError("safesearch must be one of: on, moderate, off")  # noqa: TRY003

        resolved_timelimit = timelimit if timelimit is not None else self.timelimit
        if resolved_timelimit not in _ALLOWED_TIMELIMITS | {None}:
            raise ValueError("timelimit must be one of: d, w, m, y")  # noqa: TRY003

        resolved_max = self.max_results if max_results is None else max_results
        if isinstance(resolved_max, bool) or not isinstance(resolved_max, int):
            raise TypeError("max_results must be an integer")  # noqa: TRY003
        if not 1 <= resolved_max <= 20:
            raise ValueError("max_results must be between 1 and 20")  # noqa: TRY003

        resolved_region = self.region if region is None else region
        if resolved_region is not None:
            if not isinstance(resolved_region, str):
                raise TypeError("region must be a string")  # noqa: TRY003
            resolved_region = resolved_region.strip() or None

        resolved_backend = self.backend if backend is None else backend
        if not isinstance(resolved_backend, str) or not resolved_backend.strip():
            raise ValueError("backend must be a non-empty string")  # noqa: TRY003

        return {
            "query": query,
            "search_type": resolved_type,
            "max_results": resolved_max,
            "region": resolved_region,
            "safesearch": resolved_safesearch,
            "timelimit": resolved_timelimit,
            "backend": resolved_backend.strip(),
        }

    def _perform_search(self, options: dict[str, Any]) -> list[dict[str, Any]]:
        """Invoke the installed DuckDuckGo client."""
        client_kwargs: dict[str, Any] = {"timeout": self.timeout}
        if self.proxy:
            client_kwargs["proxy"] = self.proxy

        method_kwargs: dict[str, Any] = {
            "keywords": options["query"],
            "safesearch": options["safesearch"],
            "max_results": options["max_results"],
        }
        if options["region"]:
            method_kwargs["region"] = options["region"]
        if options["timelimit"]:
            method_kwargs["timelimit"] = options["timelimit"]

        with DDGS(**client_kwargs) as client:
            if options["search_type"] == "news":
                raw_results = client.news(**method_kwargs)
            else:
                method_kwargs["backend"] = options["backend"]
                raw_results = client.text(**method_kwargs)
        return list(raw_results or [])

    @staticmethod
    def _normalize_result(result: dict[str, Any], search_type: str) -> dict[str, Any]:
        """Normalize version- and mode-specific result field names."""
        normalized = {
            "title": result.get("title", ""),
            "url": (result.get("url") or result.get("href") or result.get("link") or ""),
            "snippet": result.get("body") or result.get("snippet") or "",
        }
        if search_type == "news":
            normalized.update(
                {
                    "date": result.get("date", ""),
                    "source": result.get("source", ""),
                    "image": result.get("image", ""),
                }
            )
        return normalized

    @staticmethod
    def _error_response(
        query: Any,
        error_type: str,
        message: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a predictable, non-fabricated error result."""
        return {
            "status": "error",
            "query": query if isinstance(query, str) else "",
            "search_type": (options or {}).get("search_type"),
            "region": (options or {}).get("region"),
            "safesearch": (options or {}).get("safesearch"),
            "timelimit": (options or {}).get("timelimit"),
            "count": 0,
            "results": [],
            "error": {"type": error_type, "message": message},
        }
