#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/02/28 18:10
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: debate_agent.py
import os
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.abspath(
    os.path.join(current_dir, '../../config/config.toml'))
AgentUniverse().start(config_path=config_path, core_mode=True)


def chat(question: str):
    instance: Agent = AgentManager().get_instance_obj('debate_agent')
    instance.run(input=question)


if __name__ == '__main__':
    chat("《亮剑》中的李云龙该不该向城楼上的秀芹开炮？")
