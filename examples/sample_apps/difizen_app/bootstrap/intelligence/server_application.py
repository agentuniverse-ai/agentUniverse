# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: server_application.py
from agentuniverse.agent_serve.web.web_booster import start_web_server
from agentuniverse.base.agentuniverse import AgentUniverse


class ServerApplication:
    """
    Server application.
    """

    @classmethod
    def start(cls):
        """Start the agentUniverse core and the web server.

        Boots agentUniverse and launches the web server that exposes
        the agent services over HTTP.
        """
        AgentUniverse().start()
        start_web_server()


if __name__ == "__main__":
    ServerApplication.start()
