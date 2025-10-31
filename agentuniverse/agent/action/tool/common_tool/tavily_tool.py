#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/15 20:34
# @Author  : wangyapei
# @FileName: tavily_tool.py
# @Need install: pip install tavily-python

from typing import Any, Dict, Literal, Optional, List

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.agent.action.tool.enum import ToolTypeEnum
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.logging.logging_util import LOGGER

try:
    from tavily import TavilyClient
except ImportError:
    raise ImportError("`tavily-python` not installed. Please install using `pip install tavily-python`")


class TavilyTool(Tool):
    """Tavily search and extraction tool using the Tavily API.

    This tool supports two modes:
    1. Search: returns structured search results
    2. Extract: extracts web page content from one or more URLs

    Args:
        api_key (Optional[str]): Tavily API key. If not provided, it will be read from the environment variable.
        search_depth (Literal["basic", "advanced"]): Search depth, either "basic" or "advanced".
        max_results (int): Maximum number of results to return.
        include_answer (bool): Whether to include the AI-generated summary answer.
        mode (Literal["search", "extract"]): Operation mode, either "search" or "extract".
    """
    description: str = "Use Tavily API for web search and content extraction to get real-time information"

    # Basic configuration parameters
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("TAVILY_API_KEY"), description="Tavily API key")
    search_depth: Literal["basic", "advanced"] = Field(default="basic", description="Search depth")
    include_answer: bool = Field(default=False, description="Include AI-generated summary answer")
    mode: Literal["search", "extract"] = Field(default="search", description="Operation mode: search or extract")
    
    # Optional parameters for search mode
    topic: Optional[Literal["general", "news"]] = Field(default=None, description="Search topic: general or news")
    days: Optional[int] = Field(default=None, description="When topic=news, specify the number of days to search")
    time_range: Optional[Literal["day", "week", "month", "year"]] = Field(default=None, description="Search time range")
    max_results: int = Field(default=5, description="Maximum number of results")
    include_domains: Optional[List[str]] = Field(default=None, description="Domains to include")
    exclude_domains: Optional[List[str]] = Field(default=None, description="Domains to exclude")
    include_raw_content: bool = Field(default=False, description="Include raw content")
    include_images: bool = Field(default=False, description="Include images")
    include_image_descriptions: bool = Field(default=False, description="Include image descriptions")
    
    # Optional parameters for extraction mode
    extract_depth: Literal["basic", "advanced"] = Field(default="advanced", description="Extraction depth")

    def execute(self, input: str | list = None, **kwargs):
        """Execute the Tavily tool.
        
        Args:
            tool_input (ToolInput): Input containing query/URLs and optional configuration parameters
        
        Returns:
            Dict: Search results or extracted content
        """
        # Check API key
        if not self.api_key:
            return {"error": "Tavily API key not provided, please set TAVILY_API_KEY environment variable or provide api_key parameter"}
            
        # Update optional configuration if provided
        possible_params = [
            "api_key", "search_depth", "include_answer", "mode",
            "topic", "days", "time_range", "max_results", "include_domains", "exclude_domains",
            "include_raw_content", "include_images", "include_image_descriptions", "extract_depth"
        ]
        
        for param in possible_params:
            if kwargs.get(param) is not None:
                setattr(self, param, kwargs.get(param))

        try:
            # Initialize Tavily client
            client = TavilyClient(api_key=self.api_key)
            
            # Execute according to operation mode
            if self.mode == "extract":
                # Extraction mode
                urls = input
                if not urls:
                    return {"error": "No URLs provided for content extraction"}
                
                # Normalize single URL to list
                if isinstance(urls, str):
                    urls = [urls]
                
                # Build extraction params
                extract_params = {
                    "urls": urls,
                    "include_images": self.include_images,
                    "extract_depth": self.extract_depth
                }
                
                # Execute extraction
                result = client.extract(**extract_params)
                
                # Return API response
                return result
            else:
                # Search mode
                query = input
                if not query:
                    return {"error": "No search query provided"}
                
                # Build search params
                search_params = {
                    "query": query,
                    "search_depth": self.search_depth
                }
                
                # Add optional params if present
                for param_name, param_attr in {
                    "topic": self.topic,
                    "days": self.days,
                    "time_range": self.time_range,
                    "max_results": self.max_results,
                    "include_domains": self.include_domains,
                    "exclude_domains": self.exclude_domains,
                    "include_answer": self.include_answer,
                    "include_raw_content": self.include_raw_content,
                    "include_images": self.include_images,
                    "include_image_descriptions": self.include_image_descriptions
                }.items():
                    if param_attr is not None:
                        search_params[param_name] = param_attr
                
                # Execute search
                result = client.search(**search_params)
                
                # Return API response
                return result
                
        except Exception as e:
            LOGGER.error(f"Error while running Tavily tool: {e}")
            return {"error": f"Exception during Tavily operation: {str(e)}"}
