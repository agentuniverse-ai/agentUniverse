# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/02 11:44
# @Author  : zhangxi
# @Email   : 1724585800@qq.com
# @FileName: server_application.py
from agentuniverse.agent_serve.web.web_booster import start_web_server
from agentuniverse.base.agentuniverse import AgentUniverse


class ServerApplication:
    """
    Server application.
    """

    @classmethod
    def start(cls):
        AgentUniverse().start()
        start_web_server()


if __name__ == "__main__":
    ServerApplication.start()
