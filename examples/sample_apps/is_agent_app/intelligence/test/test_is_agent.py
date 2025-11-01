# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2025/11/01 00:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: test_is_agent.py
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


class TestISAgent(unittest.TestCase):
    """Test cases for the IS agent"""

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)

    def test_is_agent(self):
        """Test demo IS agent.

        The overall process of IS agents (demo_implementation_agent/demo_supervision_agent).
        """

        instance: Agent = AgentManager().get_instance_obj('demo_is_agent')
        result = instance.run(input="Create a hello world function.")
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()

