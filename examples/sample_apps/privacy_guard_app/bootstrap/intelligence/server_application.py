# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from agentuniverse.agent_serve.web.web_booster import start_web_server
from agentuniverse.base.agentuniverse import AgentUniverse


class ServerApplication:
    """Start the privacy guard app: `python bootstrap/intelligence/server_application.py`."""

    @classmethod
    def start(cls):
        AgentUniverse().start()
        start_web_server()


if __name__ == "__main__":
    ServerApplication.start()
