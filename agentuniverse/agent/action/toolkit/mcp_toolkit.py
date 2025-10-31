# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio
# @Time    : 2024/3/13 14:29
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: mcp_toolkit.py
from typing import List, Literal, Optional

from agentuniverse.agent.action.tool.mcp_tool import MCPTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.action.toolkit.toolkit import Toolkit
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.context.mcp_session_manager import MCPTempClient
from agentuniverse.base.util.async_util import run_async_from_sync


class MCPToolkit(Toolkit):
    transport: Literal["stdio", "sse", "websocket", "streamable_http"] = "stdio"
    url: str = ''
    command: str = ''
    args: List[str] = []
    env: Optional[dict] = None
    server_name: str = ''
    always_refresh: bool = False
    connection_kwargs: Optional[dict] = None


    def get_mcp_server_connect_args(self) -> dict:
        if self.transport == "sse":
            connect_args = {
                'transport': self.transport,
                'url': self.url
            }
        elif self.transport == "stdio":
            return {
                'transport': self.transport,
                "command": self.command,
                "args": self.args,
                'env': self.env
            }
        elif self.transport == "streamable_http":
            connect_args = {
                'transport': self.transport,
                'url': self.url
            }
        elif self.transport == "websocket":
            connect_args = {
                'transport': self.transport,
                'url': self.url
            }
        else:
            raise Exception(
                f'Unsupported mcp server type: {self.transport}')
        if self.connection_kwargs and isinstance(self.connection_kwargs, dict):
            connect_args.update(self.connection_kwargs)
        return connect_args

    def _refresh_tool_info(self):
        pass

    @property
    def tool_names(self) -> list:
        if self.always_refresh:
            self._refresh_tool_info()
        return [f'{self.name}@{tool_name}' for tool_name in self.include]


    @property
    def tool_descriptions(self) -> list:
        if self.always_refresh:
            self._refresh_tool_info()
        tools = [ToolManager().get_instance_obj(f'{self.name}@{tool_name}', new_instance=False) for tool_name in self.include]
        tool_descriptions = [f'tool name:{tool.name}\ntool description:{tool.description}\n' for tool in tools]
        return tool_descriptions

    @property
    def func_call_list(self) -> list:
        raise NotImplementedError


    async def get_all_tools(self):
        async with MCPTempClient(
            self.get_mcp_server_connect_args()
        ) as client:
            tools_list = await client.session.list_tools()
        tools = tools_list.tools
        if not self.include:
            self.include = [tool.name for tool in tools]

        for tool in tools:
            if tool.name not in self.include:
                continue
            tool_name = f'{self.name}@{tool.name}'
            tool_instance = MCPTool(
                name=tool_name,
                description=f'{tool.description}\n{str(tool.inputSchema)}',
                server_name=self.server_name,
                origin_tool_name=tool.name,
                args_model_schema=tool.inputSchema,
                input_keys=tool.inputSchema['required'],
                transport=self.transport,
                url=self.url,
                command=self.command,
                args=self.args,
                env=self.env,
                connection_kwargs=self.connection_kwargs
            )
            ToolManager().register(tool_instance.get_instance_code(), tool_instance)

    def _initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'MCPToolkit':
        if not self.server_name:
            self.server_name = self.name
        coro = self.get_all_tools()
        run_async_from_sync(coro, 60)
        return self


