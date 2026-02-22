# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: google_search_tool.py
from typing import Optional

import httpx
from pydantic import Field
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.util.env_util import get_from_env

SERPER_API_URL = "https://google.serper.dev/search"


class GoogleSearchTool(Tool):
    """The demo google search tool.

    Implement the execute method of demo google search tool, using the Google Serper API to implement a simple Google search.

    Note:
        You need to sign up for a free account at https://serper.dev and get the serper api key (2500 free queries).
    """

    serper_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SERPER_API_KEY"))

    def _build_request(self, query: str) -> tuple:
        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "q": query,
            "num": 10,
            "gl": "us",
            "hl": "en",
        }
        return headers, payload

    def _parse_results(self, response_json: dict) -> str:
        snippets = []
        if "answerBox" in response_json:
            box = response_json["answerBox"]
            answer = box.get("answer") or box.get("snippet") or box.get("snippetHighlighted")
            if answer:
                snippets.append(str(answer))

        if "knowledgeGraph" in response_json:
            kg = response_json["knowledgeGraph"]
            title = kg.get("title", "")
            description = kg.get("description", "")
            if title:
                snippets.append(f"{title}: {description}")

        for result in response_json.get("organic", []):
            snippet = result.get("snippet")
            if snippet:
                snippets.append(snippet)

        if not snippets:
            return "No good Google Search Result was found"
        return "\n\n".join(snippets)

    def execute(self, input: str):
        # get top10 results from Google search.
        headers, payload = self._build_request(input)
        response = httpx.post(SERPER_API_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        return self._parse_results(response.json())
