# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: duckduckgo_search_tool.py

from typing import Optional

from duckduckgo_search import DDGS

from agentuniverse.agent.action.tool.tool import Tool


class DuckDuckGoSearchTool(Tool):
    """Search the web using DuckDuckGo and return results."""

    backend: str = "text"
    max_results: int = 4

    def execute(self, input: str, **kwargs) -> str:
        with DDGS() as ddgs:
            if self.backend == "news":
                results = list(ddgs.news(input, max_results=self.max_results))
            else:
                results = list(ddgs.text(input, max_results=self.max_results))
        if not results:
            return "No results found."
        return str(results)
