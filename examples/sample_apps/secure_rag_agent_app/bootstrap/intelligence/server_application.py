# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from agentuniverse.base.agentuniverse import AgentUniverse


class ServerApplication:
    """Server application for secure_rag_agent_app demo."""

    @classmethod
    def start(cls):
        AgentUniverse().start()


if __name__ == "__main__":
    ServerApplication.start()
