# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: request_tool.py


from typing import Optional

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.util.logging.logging_util import LOGGER
from langchain_community.utilities.requests import GenericRequestsWrapper
from langchain_core.utils.json import parse_json_markdown


class RequestTool(Tool):
    """HTTP request tool for making various HTTP requests.

    This tool provides functionality to make HTTP requests (GET, POST, PUT, DELETE)
    with configurable headers and response handling. It supports both JSON parsing
    and raw response handling.
    
    Attributes:
        method: HTTP method to use (default: GET)
        headers: HTTP headers to include in requests
        response_content_type: Expected response content type
        requests_wrapper: LangChain requests wrapper instance
        json_parser: Whether to parse JSON input parameters
    """
    method: Optional[str] = 'GET'
    headers: Optional[dict] = {}
    response_content_type: Optional[str] = 'text'
    requests_wrapper: Optional[GenericRequestsWrapper] = None
    json_parser: Optional[bool] = False

    @staticmethod
    def _clean_url(url: str) -> str:
        """Clean URL by removing surrounding quotes.
        
        Args:
            url: URL string that may have surrounding quotes
            
        Returns:
            str: Cleaned URL string
        """
        return url.strip("\"'")

    def execute(self, input: str):
        """Execute HTTP request based on configured method and parameters.
        
        Args:
            input (str): Input string containing URL and optional parameters
            
        Returns:
            str: HTTP response content or error message
        """
        input_params: str = input
        if self.json_parser:
            try:
                parse_data = parse_json_markdown(input_params)
                return self.execute_by_method(**parse_data)
            except Exception as e:
                LOGGER.error(f'execute request error input{input_params} error{e}')
                return str(e)
        else:
            return self.execute_by_method(input_params)

    async def async_execute_by_method(self, url: str, data: dict = None, **kwargs):
        """Execute HTTP request asynchronously based on configured method.
        
        Args:
            url: Target URL for the request
            data: Request data for POST/PUT requests
            **kwargs: Additional parameters
            
        Returns:
            str: HTTP response content
            
        Raises:
            ValueError: If unsupported HTTP method is specified
        """
        url = self._clean_url(url)
        if self.method == 'GET':
            return await self.requests_wrapper.aget(url)
        elif self.method == 'POST':
            return await self.requests_wrapper.apost(url, data=data)
        elif self.method == 'PUT':
            return await self.requests_wrapper.aput(url, data=data)
        elif self.method == 'DELETE':
            return await self.requests_wrapper.adelete(url)
        else:
            raise ValueError(f"Unsupported method: {self.method}")

    def execute_by_method(self, url: str, data: dict = None, **kwargs):
        """Execute HTTP request synchronously based on configured method.
        
        Args:
            url: Target URL for the request
            data: Request data for POST/PUT requests
            **kwargs: Additional parameters
            
        Returns:
            str: HTTP response content
            
        Raises:
            ValueError: If unsupported HTTP method is specified
        """
        url = self._clean_url(url)
        if self.method == 'GET':
            return self.requests_wrapper.get(url)
        elif self.method == 'POST':
            return self.requests_wrapper.post(url, data=data)
        elif self.method == 'PUT':
            return self.requests_wrapper.put(url, data=data)
        elif self.method == 'DELETE':
            return self.requests_wrapper.delete(url)
        else:
            raise ValueError(f"Unsupported method: {self.method}")

    def initialize_by_component_configer(self, component_configer: ToolConfiger) -> 'Tool':
        """Initialize the tool using component configer.
        
        Args:
            component_configer: Tool configuration object
            
        Returns:
            Tool: Initialized tool instance
        """
        self.headers = component_configer.configer.value.get('headers')
        self.method = component_configer.configer.value.get('method')
        self.response_content_type = component_configer.configer.value.get('response_content_type')
        if 'json_parser' in component_configer.configer.value:
            self.json_parser = component_configer.configer.value.get('json_parser')
        self.requests_wrapper = GenericRequestsWrapper(
            headers=self.headers,
            response_content_type=self.response_content_type
        )
        return super().initialize_by_component_configer(component_configer)
