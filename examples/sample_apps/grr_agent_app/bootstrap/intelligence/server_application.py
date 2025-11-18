# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/01 00:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
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

