# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    :
# @Author  :
# @Email   :
# @FileName: google_search_tool.py

from typing import Optional

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.util.env_util import get_from_env
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from pydantic import Field


class GoogleSearchTool(Tool):
    """The demo google search tool.

    Implement the execute method of demo google search tool, using the `GoogleSerperAPIWrapper` to implement a simple Google search.

    Note:
        You need to sign up for a free account at https://serper.dev and get the serper api key (2500 free queries).
    """

    serper_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SERPER_API_KEY"))

    def _ensure_api_key(self):
        if not self.serper_api_key:
            raise ValueError(
                "SERPER_API_KEY is not set. Configure it via the "
                "SERPER_API_KEY environment variable or the serper_api_key "
                "field on the GoogleSearchTool component.")

    def execute(self, input: str):
        # get top10 results from Google search.
        self._ensure_api_key()
        search = GoogleSerperAPIWrapper(serper_api_key=self.serper_api_key, k=10, gl="us", hl="en", type="search")
        return search.run(query=input)

    async def async_execute(self, input: str):
        # get top10 results from Google search.
        self._ensure_api_key()
        search = GoogleSerperAPIWrapper(serper_api_key=self.serper_api_key, k=10, gl="us", hl="en", type="search")
        return await search.arun(query=input)
