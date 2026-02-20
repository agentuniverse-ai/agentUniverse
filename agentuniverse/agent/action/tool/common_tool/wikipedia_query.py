# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: wikipedia_query.py

from typing import Optional

import wikipedia

from agentuniverse.agent.action.tool.tool import Tool


class WikipediaTool(Tool):
    """Query Wikipedia and return page summaries."""

    top_k_results: int = 3
    max_chars: int = 4000
    lang: Optional[str] = "en"

    def execute(self, input: str, **kwargs) -> str:
        if self.lang:
            wikipedia.set_lang(self.lang)
        search_results = wikipedia.search(input)
        summaries = []
        for title in search_results[:self.top_k_results]:
            try:
                page = wikipedia.page(title, auto_suggest=False)
                summary = page.summary
                if len(summary) > self.max_chars:
                    summary = summary[:self.max_chars]
                summaries.append(f"Page: {title}\nSummary: {summary}")
            except (wikipedia.exceptions.PageError,
                    wikipedia.exceptions.DisambiguationError):
                continue
        if not summaries:
            return "No good Wikipedia Search Result was found"
        return "\n\n".join(summaries)
