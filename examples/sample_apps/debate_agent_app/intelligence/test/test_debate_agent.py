#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/02/28 18:10
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: test_debate_agent.py
import unittest
import os

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse


class DebateAgentTest(unittest.TestCase):

    def setUp(self) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.abspath(os.path.join(current_dir, '../../config/config.toml'))
        AgentUniverse().start(config_path=config_path)

    def test_debate_agent(self):   
        instance: Agent = AgentManager().get_instance_obj('debate_agent')
        output_object: OutputObject = instance.run(
            input='《亮剑》中的李云龙该不该向城楼上的秀芹开炮？')



if __name__ == '__main__':
    unittest.main()
