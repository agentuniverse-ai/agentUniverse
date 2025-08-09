# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/7 11:22
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: discussion_agents.py
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    instance: Agent = AgentManager().get_instance_obj('discussion_group_agent')
    instance.run(input=question)


if __name__ == '__main__':
    chat("甜粽子好吃还是咸粽子好吃")
