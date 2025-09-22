# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/8 20:58
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
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
