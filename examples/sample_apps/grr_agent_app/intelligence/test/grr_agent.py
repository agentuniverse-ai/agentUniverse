# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/01 00:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: grr_agent.py
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    instance: Agent = AgentManager().get_instance_obj('demo_grr_agent')
    instance.run(input=question)


if __name__ == '__main__':
    chat("Write a short article about artificial intelligence.")

