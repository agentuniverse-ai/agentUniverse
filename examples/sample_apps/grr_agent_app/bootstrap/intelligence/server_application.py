# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2/17/25
# @Author  : quesheng
# @Email   : huiyi.why@antgroup.com
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
