# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/15 10:00
# @FileName: web_search_tool.py

import json
from typing import List, Optional

from agentuniverse.agent.action.tool.tool import Tool


class WebSearchTool(Tool):
    """Search the web using DuckDuckGo and return structured results."""

    max_results: int = 8

    def execute(self, query: str, allowed_domains: Optional[List[str]] = None,
                blocked_domains: Optional[List[str]] = None) -> str:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return json.dumps({
                "error": "duckduckgo_search library is required. "
                         "Install with: pip install duckduckgo_search",
                "status": "error"
            })

        try:
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query, max_results=self.max_results))

            # Apply domain filtering
            filtered = []
            for r in raw_results:
                href = r.get('href', '')

                if allowed_domains:
                    if not any(domain in href for domain in allowed_domains):
                        continue

                if blocked_domains:
                    if any(domain in href for domain in blocked_domains):
                        continue

                filtered.append({
                    "title": r.get("title", ""),
                    "url": href,
                    "snippet": r.get("body", ""),
                })

            return json.dumps({
                "results": filtered,
                "query": query,
                "count": len(filtered),
                "status": "success"
            })

        except Exception as e:
            return json.dumps({
                "error": str(e),
                "query": query,
                "status": "error"
            })
