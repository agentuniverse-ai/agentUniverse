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

    def execute(self, input: str):
        """Run a Google search for the given query.

        Uses the `GoogleSerperAPIWrapper` to fetch the top results from
        Google search and returns the raw result.

        Args:
            input (str): The search query to run against Google.

        Returns:
            The search results returned by the serper API wrapper.
        """
        # get top10 results from Google search.
        search_api = GoogleSerperAPIWrapper(serper_api_key=self.serper_api_key, k=10, gl="us", hl="en", type="search")
        res = search_api.run(query=input)
        return res
