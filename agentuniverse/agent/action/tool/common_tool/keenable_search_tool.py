#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: keenable_search_tool.py

from typing import Optional

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.logging.logging_util import LOGGER

KEENABLE_PUBLIC_SEARCH_URL = "https://api.keenable.ai/v1/search/public"
KEENABLE_SEARCH_URL = "https://api.keenable.ai/v1/search"


class KeenableSearchTool(Tool):
    """Web search tool backed by the Keenable API (https://keenable.ai).

    No API key is required: without a key the free public endpoint is used.
    If KEENABLE_API_KEY is set (or api_key is passed), the keyed endpoint is
    used instead, which offers higher limits.

    Args:
        api_key (Optional[str]): Keenable API key, read from KEENABLE_API_KEY by default.
        max_results (int): Maximum number of results to return.
        timeout (int): Request timeout in seconds.
        max_snippet_length (int): Maximum characters kept from a snippet when a
            result has no description.
    """
    description: str = "Search the web with Keenable and return titles, URLs and short summaries."

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("KEENABLE_API_KEY"))
    max_results: int = Field(default=5, description="Maximum number of results")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_snippet_length: int = Field(default=1000, description="Snippet truncation length")

    def execute(self, input: str = None, max_results: int = None, api_key: str = None):
        query = input
        if not isinstance(query, str) or not query.strip():
            return {"error": "No search query provided"}

        key = api_key or self.api_key
        limit = max_results or self.max_results
        headers = {"Content-Type": "application/json", "X-Keenable-Title": "agentUniverse"}
        if key:
            headers["X-API-Key"] = key
        url = KEENABLE_SEARCH_URL if key else KEENABLE_PUBLIC_SEARCH_URL

        try:
            response = requests.post(
                url,
                json={"query": query, "max_results": limit},
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            LOGGER.error(f"Keenable search failed: {e}")
            return {"error": f"Keenable search failed: {str(e)}"}

        results = []
        for item in data.get("results") or []:
            if not item.get("url"):
                continue
            content = item.get("description") or (item.get("snippet") or "")[: self.max_snippet_length]
            results.append({"title": item.get("title") or "", "url": item["url"], "content": content})
        return {"query": query, "results": results[:limit]}
