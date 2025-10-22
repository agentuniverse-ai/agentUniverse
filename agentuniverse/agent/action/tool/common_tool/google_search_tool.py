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
    """Google search tool implementation.

    Implements the execute method for Google search functionality using the `GoogleSerperAPIWrapper`.
    Provides both synchronous and asynchronous search capabilities.

    Note:
        You need to sign up for a free account at https://serper.dev and get the serper api key (2500 free queries).
        
    Attributes:
        serper_api_key: Serper API key from environment variable
    """

    serper_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SERPER_API_KEY"))

    def execute(self, input: str):
        """Execute Google search query.
        
        Args:
            input (str): Search query string
            
        Returns:
            str: Top 10 search results from Google
        """
        # Get top 10 results from Google search
        search = GoogleSerperAPIWrapper(serper_api_key=self.serper_api_key, k=10, gl="us", hl="en", type="search")
        return search.run(query=input)

    async def async_execute(self, input: str):
        """Execute Google search query asynchronously.
        
        Args:
            input (str): Search query string
            
        Returns:
            str: Top 10 search results from Google
        """
        # Get top 10 results from Google search
        search = GoogleSerperAPIWrapper(serper_api_key=self.serper_api_key, k=10, gl="us", hl="en", type="search")
        return await search.arun(query=input)
