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
        """Start the AgentUniverse core and the web server.

        Initializes the framework and launches the web server serving the agents.
        """
        start_web_server()


if __name__ == "__main__":
    ServerApplication.start()
