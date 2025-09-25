# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2/17/25
# @Author  : quesheng
# @Email   : huiyi.why@antgroup.com
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    """ Grr agents example.

    The grr agents in agentUniverse become a chatbot and can ask questions to get the answer.
    """
    instance: Agent = AgentManager().get_instance_obj('demo_grr_agent')
    instance.run(input=question)


if __name__ == '__main__':
    chat("帮我分析下2023年巴菲特减持比亚迪原因")
