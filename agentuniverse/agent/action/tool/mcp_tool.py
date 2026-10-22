# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio
from typing import Any, Optional, Literal, List

from mcp.types import CallToolResult

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import \
    ToolConfiger
from agentuniverse.base.context.mcp_session_manager import MCPSessionManager, \
    MCPTempClient
from agentuniverse.base.util.async_util import run_async_from_sync


# @Time    : 2025/4/14 18:11
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: mcp_tool.py


class MCPTool(Tool):

    server_name: str = ''
    transport: Literal["stdio", "sse", "websocket", "streamable_http"] = "stdio"
    url: str = ''
    command: str = ''
    args: List[str] = []
    env: Optional[dict] = None
    connection_kwargs: Optional[dict] = None
    # You can use origin_tool_name while you want another name for this aU tool
    origin_tool_name: str = ''

    @property
    def tool_name(self) -> str:
        return self.origin_tool_name if self.origin_tool_name else self.name

    def execute(self, **kwargs) -> CallToolResult:
        session = MCPSessionManager().get_mcp_server_session_sync(
            server_name=self.server_name,
            **self.get_mcp_server_connect_args()
        )
        result = MCPSessionManager().run_async(session.call_tool, self.tool_name, kwargs)
        return result

    async def async_execute(self, **kwargs) -> CallToolResult:
        session = await MCPSessionManager().get_mcp_server_session(
            server_name=self.server_name,
            **self.get_mcp_server_connect_args()
        )
        result = await session.call_tool(self.tool_name, kwargs)
        return result


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

    def initialize_by_component_configer(self, component_configer: ToolConfiger) -> 'MCPTool':
        """Initialize the agent model by component configer."""
        super().initialize_by_component_configer(component_configer)
        self._initialize_by_component_configer(component_configer)
        return self

    async def get_tool_info(self):
        async with MCPTempClient(
            self.get_mcp_server_connect_args()
        ) as client:
            tools_list = await client.session.list_tools()
        tools = tools_list.tools
        tool_info = None
        for _tool in tools:
            if _tool.name == self.tool_name:
                tool_info = _tool
                break
        if not tool_info:
            raise Exception(f'No tool named {self.tool_name} in mcp server {self.server_name}')
        self.input_keys = tool_info.inputSchema['required']
        self.args_model_schema = tool_info.inputSchema
        if not self.description:
            self.description = f'{tool_info.description}\n{str(tool_info.inputSchema)}'

    def _initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'MCPTool':
        if not self.server_name:
            # use an unique name to manage session
            self.server_name = self.name
        coro = self.get_tool_info()
        run_async_from_sync(coro, timeout=10)
        return self
