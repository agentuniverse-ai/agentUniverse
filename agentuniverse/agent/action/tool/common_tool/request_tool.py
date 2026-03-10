# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: request_tool.py

import json
import re
from typing import Optional

import httpx

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.util.logging.logging_util import LOGGER


def parse_json_markdown(text: str) -> dict:
    """Parse JSON from markdown-formatted text (```json ... ``` blocks)."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text.strip())
    if match:
        json_str = match.group(1).strip()
    else:
        json_str = text.strip()
    return json.loads(json_str)


class RequestTool(Tool):
    method: Optional[str] = 'GET'
    headers: Optional[dict] = {}
    response_content_type: Optional[str] = 'text'
    json_parser: Optional[bool] = False

    @staticmethod
    def _clean_url(url: str) -> str:
        """Strips quotes from the url."""
        return url.strip("\"'")

    def _get_response_content(self, response: httpx.Response) -> str:
        if self.response_content_type == 'json':
            return json.dumps(response.json())
        return response.text

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

    async def async_execute(self, input: str):
        input_params: str = input
        if self.json_parser:
            try:
                parse_data = parse_json_markdown(input_params)
                return await self.async_execute_by_method(**parse_data)
            except Exception as e:
                LOGGER.error(f'async_execute request error input{input_params} error{e}')
                return str(e)
        else:
            return await self.async_execute_by_method(input_params)

    async def async_execute_by_method(self, url: str, data: dict = None, **kwargs):
        url = self._clean_url(url)
        async with httpx.AsyncClient(headers=self.headers, timeout=20) as client:
            if self.method == 'GET':
                response = await client.get(url)
            elif self.method == 'POST':
                response = await client.post(url, json=data)
            elif self.method == 'PUT':
                response = await client.put(url, json=data)
            elif self.method == 'DELETE':
                response = await client.delete(url)
            else:
                raise ValueError(f"Unsupported method: {self.method}")
            response.raise_for_status()
            return self._get_response_content(response)

    def execute_by_method(self, url: str, data: dict = None, **kwargs):
        url = self._clean_url(url)
        if self.method == 'GET':
            response = httpx.get(url, headers=self.headers, timeout=20)
        elif self.method == 'POST':
            response = httpx.post(url, headers=self.headers, json=data, timeout=20)
        elif self.method == 'PUT':
            response = httpx.put(url, headers=self.headers, json=data, timeout=20)
        elif self.method == 'DELETE':
            response = httpx.delete(url, headers=self.headers, timeout=20)
        else:
            raise ValueError(f"Unsupported method: {self.method}")
        response.raise_for_status()
        return self._get_response_content(response)

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
        return super().initialize_by_component_configer(component_configer)
