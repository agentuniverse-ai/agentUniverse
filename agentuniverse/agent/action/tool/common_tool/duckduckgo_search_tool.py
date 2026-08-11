# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import Any, List, Optional

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.util.env_util import get_from_env

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None


class DuckDuckGoSearchTool(Tool):
    """DuckDuckGo web search tool that requires no API key.

    This tool uses the ``duckduckgo_search`` Python package to perform web
    searches via the DuckDuckGo search engine.  Because DuckDuckGo does not
    require an API key, this tool works out-of-the-box with zero configuration,
    making it ideal for quick prototyping and developers who do not yet have
    accounts with Google / Bing / Tavily.

    If the optional ``duckduckgo_search`` dependency is not installed the tool
    falls back to ``MockSearchTool`` so that the framework continues to
    function -- this mirrors the behaviour of the existing ``BingSearchTool``.
    """

    description: str = (
        "Perform a free DuckDuckGo web search without an API key. "
        "Returns the top search results with title, URL and snippet."
    )

    # ----- configurable attributes -----
    max_results: int = Field(default=5, description="Maximum number of results to return (1-20).")
    region: Optional[str] = Field(
        default=None,
        description="Region code for search results, e.g. 'us', 'cn', 'uk', 'jp'. "
                    "When None, DuckDuckGo's default region is used.",
    )
    safesearch: str = Field(
        default="moderate",
        description="Safe-search level: 'on', 'moderate', or 'off'.",
    )
    proxy: Optional[str] = Field(
        default_factory=lambda: get_from_env("DUCKDUCKGO_PROXY"),
        description="Proxy URL (e.g. 'http://127.0.0.1:7890'). "
                    "Reads from the DUCKDUCKGO_PROXY env var when available.",
    )

    def execute(self, input: Any, **kwargs: Any) -> str:
        """Execute a DuckDuckGo search.

        Args:
            input: The search query string, or a ``ToolInput`` whose ``input``
                   field contains the query.
            **kwargs: Optional overrides for ``max_results``, ``region`` and
                      ``safesearch``.

        Returns:
            A formatted string of search results, one per block, containing
            the title, URL and snippet of each result.
        """
        if isinstance(input, ToolInput):
            params = input.to_dict()
            query = params.get("input", "")
            max_results = params.get("max_results", self.max_results)
            region = params.get("region", self.region)
            safesearch = params.get("safesearch", self.safesearch)
        else:
            query = str(input)
            max_results = kwargs.get("max_results", self.max_results)
            region = kwargs.get("region", self.region)
            safesearch = kwargs.get("safesearch", self.safesearch)

        # Clamp max_results to a sensible range.
        max_results = max(1, min(int(max_results), 20))

        if DDGS is None:
            # Graceful fallback when the optional dependency is missing,
            # consistent with the BingSearchTool pattern.
            from agentuniverse.agent.action.tool.common_tool.mock_search_tool import MockSearchTool
            return MockSearchTool().execute(query)

        try:
            return self._search(query, max_results, region, safesearch)
        except Exception as e:
            # If the live search fails (network issues, rate-limit, etc.)
            # fall back to the mock so the agent pipeline is not broken.
            from agentuniverse.agent.action.tool.common_tool.mock_search_tool import MockSearchTool
            mock_result = MockSearchTool().execute(query)
            return (
                f"[DuckDuckGo search failed: {e}. "
                f"Falling back to mock results.]\n{mock_result}"
            )

    async def async_execute(self, tool_input: ToolInput) -> str:
        """Asynchronously execute a DuckDuckGo search.

        The ``duckduckgo_search`` library is synchronous, so this method
        runs the blocking search in a thread pool to avoid blocking the
        event loop.

        Args:
            tool_input: A ``ToolInput`` whose ``input`` field is the query.

        Returns:
            Same formatted string as :meth:`execute`.
        """
        import asyncio
        params = tool_input.to_dict()
        query = params.get("input", "")
        max_results = params.get("max_results", self.max_results)
        region = params.get("region", self.region)
        safesearch = params.get("safesearch", self.safesearch)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._search, query, max_results, region, safesearch
        )

    # ------------------------------------------------------------------
    #  Internal helpers
    # ------------------------------------------------------------------
    def _search(
        self,
        query: str,
        max_results: int,
        region: Optional[str],
        safesearch: str,
    ) -> str:
        """Perform the actual DuckDuckGo search and format results."""
        ddgs_kwargs: dict = {
            "max_results": max_results,
            "safesearch": safesearch,
        }
        if region:
            ddgs_kwargs["region"] = region
        if self.proxy:
            ddgs_kwargs["proxy"] = self.proxy

        with DDGS() as ddgs:
            results: List[dict] = list(ddgs.text(query, **ddgs_kwargs))

        if not results:
            return f"No results found for query: {query}"

        formatted_lines: List[str] = []
        for idx, res in enumerate(results, start=1):
            title = res.get("title", "")
            url = res.get("href") or res.get("link") or res.get("url", "")
            body = res.get("body") or res.get("snippet", "")
            formatted_lines.append(f"{idx}. {title}\n   URL: {url}\n   {body}")

        return "\n".join(formatted_lines)