# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import Optional, Literal, List

from mcp.types import CallToolResult

from agentuniverse.agent.action.tool.tool import Tool, ToolConfigError
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import \
    ToolConfiger
from agentuniverse.base.context.mcp_session_manager import MCPSessionManager, \
    MCPTempClient


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
        session = MCPSessionManager().get_mcp_server_session(
            server_name=self.server_name,
            **self.get_mcp_server_connect_args()
        )
        result = MCPSessionManager().managed_stack.run_async(
            session.call_tool, self.tool_name, kwargs
        )
        return result

    async def async_execute(self, **kwargs) -> CallToolResult:
        session = await MCPSessionManager().get_mcp_server_session_async(
            server_name=self.server_name,
            **self.get_mcp_server_connect_args()
        )
        return await session.call_tool(self.tool_name, kwargs)

    def get_mcp_server_connect_args(self) -> dict:
        if self.transport == "stdio":
            connect_args = {
                'transport': self.transport,
                "command": self.command,
                "args": self.args,
                'env': self.env
            }
        elif self.transport == "sse":
            connect_args = {
                'transport': self.transport,
                'url': self.url
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

    def get_tool_info(self):
        if self.args_model_schema is not None:
            return

        with MCPTempClient(self.get_mcp_server_connect_args()) as client:
            tools_list = client.list_tools()

        tool_info = next(
            (t for t in tools_list.tools if t.name == self.tool_name),
            None,
        )

        if tool_info is None:
            raise ToolConfigError(
                f'No tool named "{self.tool_name}" in MCP server "{self.server_name}". '
                f'Available: {[t.name for t in tools_list.tools]}'
            )

        input_schema = tool_info.inputSchema or {}
        self.args_model_schema = input_schema
        self.input_keys = input_schema.get("required", [])
        if not self.name:
            self.name = tool_info.name

        if not self.description:
            self.description = tool_info.description or ""

    def _initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'MCPTool':
        if not self.server_name:
            # use an unique name to manage session
            self.server_name = self.name
        self.get_tool_info()
        return self
