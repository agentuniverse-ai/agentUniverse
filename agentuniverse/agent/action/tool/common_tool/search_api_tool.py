# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: search_api_tool.py

from typing import Optional

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.util.env_util import get_from_env
from langchain_community.utilities import SearchApiAPIWrapper
from pydantic import Field


class SearchAPITool(Tool):
    """
    The demo search tool.

    Implement the execute method of demo google search tool, using the `SearchApiAPIWrapper` to implement a simple search.

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
    search_api_wrapper: Optional[SearchApiAPIWrapper] = None
    search_type: str = "common"

    def _load_api_wapper(self):
        if not self.search_api_key:
            raise ValueError("Please set the SEARCHAPI_API_KEY environment variable.")
        if not self.search_api_wrapper:
            self.search_api_wrapper = SearchApiAPIWrapper(searchapi_api_key=self.search_api_key, engine=self.engine)
        return self.search_api_wrapper

    def execute(self, input: str, **kwargs):
        self._load_api_wapper()
        search_params = {}
        for k, v in self.search_params.items():
            if k in kwargs:
                search_params[k] = kwargs.get(k)
                continue
            search_params[k] = v
        if self.search_type == "json":
            return self.search_api_wrapper.results(query=input, **search_params)
        return self.search_api_wrapper.run(query=input, **search_params)

    async def async_execute(self, tool_input: ToolInput):
        self._load_api_wapper()
        search_params = {}
        for k, v in self.search_params.items():
            if k in tool_input.to_dict():
                search_params[k] = tool_input.get_data(k)
                continue
            search_params[k] = v
        input = tool_input.get_data("input")
        if self.search_type == "json":
            return await self.search_api_wrapper.aresults(query=input, **search_params)
        return await self.search_api_wrapper.arun(query=input, **search_params)

    def initialize_by_component_configer(self, component_configer: ToolConfiger) -> 'Tool':
        """Initialize the tool by the component configer."""
        super().initialize_by_component_configer(component_configer)
        self.engine = component_configer.configer.value.get('engine', 'google')
        self.search_params = component_configer.configer.value.get('search_params', {})
        self.search_type = component_configer.configer.value.get('search_type', 'common')
        return self
