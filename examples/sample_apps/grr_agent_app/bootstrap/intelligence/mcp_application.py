# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/01 00:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: mcp_application.py
from agentuniverse.agent_serve.mcp.mcp_booster import start_mcp_server
from agentuniverse.base.agentuniverse import AgentUniverse


class MCPApplication:
    """
    MCP application.
    """

    @classmethod
    def start(cls):
        AgentUniverse().start()
        start_mcp_server()


if __name__ == "__main__":
    MCPApplication.start()

