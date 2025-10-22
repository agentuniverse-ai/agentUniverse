# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: bing_search_tool.py
from typing import Optional

from pydantic import Field
from langchain_community.utilities import BingSearchAPIWrapper

from agentuniverse.agent.action.tool.common_tool.mock_search_tool import MockSearchTool
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.util.env_util import get_from_env



class BingSearchTool(Tool):
    """Bing search tool implementation.

    Implements the execute method for Bing search functionality using the `BingSearchAPIWrapper`.
    Falls back to mock search if Bing subscription key is not provided.
    
    Attributes:
        bing_subscription_key: Bing API subscription key from environment variable
        bing_search_url: Bing search API endpoint URL
    """

    bing_subscription_key: Optional[str] = Field(default_factory=lambda: get_from_env("BING_SUBSCRIPTION_KEY"))
    bing_search_url: Optional[str] = Field(default='https://api.bing.microsoft.com/v7.0/search')

    def execute(self, input: str):
        """Execute Bing search query.
        
        Args:
            input (str): Search query string
            
        Returns:
            str: Search results or mock results if API key is not available
        """
        if self.bing_subscription_key is None:
            return MockSearchTool().execute(input)
        query = input
        # Get top 5 results from Bing search
        search = BingSearchAPIWrapper(bing_subscription_key=self.bing_subscription_key, k=5,
                                      bing_search_url=self.bing_search_url)
        return search.run(query=query)
