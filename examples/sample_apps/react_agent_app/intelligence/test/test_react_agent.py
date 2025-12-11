# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/4 21:27
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_react_agent.py
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


class ReActAgentTest(unittest.TestCase):

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_react_agent(self):
        """Test demo reAct agent."""
        instance: Agent = AgentManager().get_instance_obj('demo_react_agent')
        query = '请给出一段python代码，可以判断数字是否为素数，给出之前必须验证代码是否可以运行，最少验证1次'
        instance.run(input=query)

    def test_react_agent_with_long_term_memory_extract(self):
        """Test demo reAct agent."""
        instance: Agent = AgentManager().get_instance_obj('demo_react_agent')
        query = '请给出一段python代码，可以判断数字是否为素数，给出之前必须验证代码是否可以运行，最少验证1次。我喜欢简洁的代码'
        instance.run(input=query, session_id='test_session_id')
        query = '请给出一段python代码，可以判断数字是否为偶数'
        instance.run(input=query, session_id='test_session_id')
        query = '请给出一段python代码，可以判断数字是否为整数，我不喜欢简洁的代码'
        instance.run(input=query, session_id='test_session_id')

    def test_react_agent_with_context_toolkit(self):
        """Test demo reAct agent."""
        instance: Agent = AgentManager().get_instance_obj('demo_react_agent')
        query = '帮我写一个 html 文件，展示各种经济数据。要美观、好看'
        instance.run(input=query, session_id='test_session_id')

if __name__ == '__main__':
    unittest.main()
