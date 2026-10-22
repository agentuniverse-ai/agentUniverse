# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/11/28 17:17
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: recommend_sop_agent_test.py
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    """Ask the recommend SOP agent a question and return its response.

    Args:
        question (str): The user question to send to the agent.

    Returns:
        The agent output produced by the recommend SOP agent.
    """
    instance: Agent = AgentManager().get_instance_obj('recommend_sop_agent')
    return instance.run(input=question)


if __name__ == '__main__':
    print(chat("为我想要买医疗类保险").get_data('output'))
