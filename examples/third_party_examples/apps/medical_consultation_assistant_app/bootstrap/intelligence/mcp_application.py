# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/02 11:26
# @Author  : zhangxi
# @Email   : 1724585800@qq.com
# @FileName: mcp_application.py
from agentuniverse.agent_serve.web.mcp.mcp_server_manager import MCPServerManager
from agentuniverse.base.agentuniverse import AgentUniverse


class ServerApplication:
    """
    Server application.
    """

    @classmethod
    def start(cls):
        AgentUniverse().start(core_mode=True)
        MCPServerManager().start_server()


if __name__ == "__main__":
    ServerApplication.start()
