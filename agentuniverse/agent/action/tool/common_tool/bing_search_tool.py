# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: bing_search_tool.py
from typing import Optional

import httpx
from pydantic import Field

from agentuniverse.agent.action.tool.common_tool.mock_search_tool import MockSearchTool
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.util.env_util import get_from_env


class BingSearchTool(Tool):
    """The demo bing search tool.

    Implement the execute method of demo bing search tool, using the Bing Web Search API to implement a simple Bing search.
    """

    bing_subscription_key: Optional[str] = Field(default_factory=lambda: get_from_env("BING_SUBSCRIPTION_KEY"))
    bing_search_url: Optional[str] = Field(default='https://api.bing.microsoft.com/v7.0/search')
    k: int = Field(default=5, description="Number of results to return")

    def _search(self, query: str) -> str:
        headers = {"Ocp-Apim-Subscription-Key": self.bing_subscription_key}
        params = {"q": query, "count": self.k, "textDecorations": True, "textFormat": "HTML"}
        response = httpx.get(self.bing_search_url, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        return self._parse_results(response.json())

    async def _async_search(self, query: str) -> str:
        headers = {"Ocp-Apim-Subscription-Key": self.bing_subscription_key}
        params = {"q": query, "count": self.k, "textDecorations": True, "textFormat": "HTML"}
        async with httpx.AsyncClient() as client:
            response = await client.get(self.bing_search_url, headers=headers, params=params, timeout=20)
            response.raise_for_status()
            return self._parse_results(response.json())

    @staticmethod
    def _parse_results(response_json: dict) -> str:
        snippets = []
        if "webPages" in response_json:
            for page in response_json["webPages"].get("value", []):
                snippet = page.get("snippet")
                if snippet:
                    snippets.append(snippet)
        if not snippets:
            return "No good Bing Search Result was found"
        return " ".join(snippets)

    def execute(self, input: str):
        if self.bing_subscription_key is None:
            return MockSearchTool().execute(input)
        return self._search(input)

    async def async_execute(self, input: str):
        if self.bing_subscription_key is None:
            return MockSearchTool().execute(input)
        return await self._async_search(input)
