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
    method: Optional[str] = 'GET'
    headers: Optional[dict] = {}
    response_content_type: Optional[str] = 'text'
    requests_wrapper: Optional[GenericRequestsWrapper] = None
    json_parser: Optional[bool] = False

    @staticmethod
    def _clean_url(url: str) -> str:
        """Strips quotes from the url."""
        return url.strip("\"'")

    def execute(self, input: str):
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
        """
        :param component_configer:
        :return:
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
