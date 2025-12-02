# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/25 17:19
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: perp_agent.py
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    """ Perp agents example.

    The perp agents in agentUniverse become a chatbot and can ask questions to get the answer.
    """
    instance: Agent = AgentManager().get_instance_obj('demo_perp_agent')
    instance.run(input=question)


if __name__ == '__main__':
    chat("分析最新的国内CPI数据，然后绘制一份精美的可视化报告给我")
