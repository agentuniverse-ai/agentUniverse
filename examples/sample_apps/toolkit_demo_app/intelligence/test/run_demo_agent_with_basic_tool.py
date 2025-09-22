# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/8 11:41
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: run_demo_agent_with_basic_tool.py
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    instance: Agent = AgentManager().get_instance_obj('demo_agent_with_basic_tool')
    instance.run(input=question)


if __name__ == '__main__':
    chat("请给出一段python代码，可以判断数字是否为素数，给出之前必须验证代码是否可以运行，最少验证1次")
