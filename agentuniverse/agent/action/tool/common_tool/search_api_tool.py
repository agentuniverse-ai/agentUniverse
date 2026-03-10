# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: search_api_tool.py

from typing import Optional

import httpx

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.util.env_util import get_from_env
from pydantic import Field

SEARCHAPI_BASE_URL = "https://www.searchapi.io/api/v1/search"


class SearchAPITool(Tool):
    """
    The demo search tool.

    Implement the execute method of demo google search tool, using the SearchAPI.io API to implement a simple search.

    Note:
        You need to sign up for a free account at https://www.searchapi.io/ and get the SEARCHAPI_API_KEY api key (100 free queries).

    Args:
        search_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SEARCHAPI_API_KEY")),
        engine: str = "google" engine type you want to use
        search_params: dict = {} engine search parameters
        search_type: str = "common" result type you want to get ,common string or json
    """

    search_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SEARCHAPI_API_KEY"))
    engine: str = "google"
    search_params: dict = {}
    search_type: str = "common"

    def _build_params(self, query: str, extra_params: dict) -> dict:
        params = {
            "api_key": self.search_api_key,
            "engine": self.engine,
            "q": query,
        }
        params.update(extra_params)
        return params

    def _parse_results_to_string(self, response_json: dict) -> str:
        snippets = []
        if "answer_box" in response_json:
            box = response_json["answer_box"]
            answer = box.get("answer") or box.get("snippet") or box.get("result")
            if answer:
                snippets.append(str(answer))

        if "knowledge_graph" in response_json:
            kg = response_json["knowledge_graph"]
            title = kg.get("title", "")
            description = kg.get("description", "")
            if title:
                snippets.append(f"{title}: {description}")

        for result in response_json.get("organic_results", []):
            snippet = result.get("snippet")
            if snippet:
                snippets.append(snippet)

        if not snippets:
            return "No good search results found"
        return "\n\n".join(snippets)

    def _resolve_search_params(self, kwargs: dict) -> dict:
        search_params = {}
        for k, v in self.search_params.items():
            if k in kwargs:
                search_params[k] = kwargs.get(k)
                continue
            search_params[k] = v
        return search_params

    def execute(self, input: str, **kwargs):
        if not self.search_api_key:
            raise ValueError("Please set the SEARCHAPI_API_KEY environment variable.")
        search_params = self._resolve_search_params(kwargs)
        params = self._build_params(input, search_params)
        response = httpx.get(SEARCHAPI_BASE_URL, params=params, timeout=20)
        response.raise_for_status()
        response_json = response.json()
        if self.search_type == "json":
            return response_json
        return self._parse_results_to_string(response_json)

    async def async_execute(self, input: str, **kwargs):
        if not self.search_api_key:
            raise ValueError("Please set the SEARCHAPI_API_KEY environment variable.")
        search_params = self._resolve_search_params(kwargs)
        params = self._build_params(input, search_params)
        async with httpx.AsyncClient() as client:
            response = await client.get(SEARCHAPI_BASE_URL, params=params, timeout=20)
            response.raise_for_status()
            response_json = response.json()
        if self.search_type == "json":
            return response_json
        return self._parse_results_to_string(response_json)

    def initialize_by_component_configer(self, component_configer: ToolConfiger) -> 'Tool':
        """Initialize the tool by the component configer."""
        super().initialize_by_component_configer(component_configer)
        self.engine = component_configer.configer.value.get('engine', 'google')
        self.search_params = component_configer.configer.value.get('search_params', {})
        self.search_type = component_configer.configer.value.get('search_type', 'common')
        return self
