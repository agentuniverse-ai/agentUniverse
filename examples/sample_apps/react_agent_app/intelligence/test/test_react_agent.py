# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio
# @Time    : 2024/6/4 21:27
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_react_agent.py
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse


class ReActAgentTest(unittest.TestCase):
    """Test cases for the demo react agent."""

    def setUp(self) -> None:
        """Start the agent universe with the app configuration before each test."""
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_react_agent(self):
        """Test demo reAct agent."""
        instance: Agent = AgentManager().get_instance_obj('demo_react_agent')
        query = '请给出一段python代码，可以判断数字是否为素数，给出之前必须验证代码是否可以运行，最少验证1次'
        instance.run(input=query)


if __name__ == '__main__':
    unittest.main()
