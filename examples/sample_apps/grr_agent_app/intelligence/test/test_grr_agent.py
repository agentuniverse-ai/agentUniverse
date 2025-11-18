# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2025/11/01 00:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: test_grr_agent.py
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


class TestGRRAgent(unittest.TestCase):
    """Test cases for the GRR agent"""

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)

    def test_grr_agent(self):
        """Test demo GRR agent.

        The overall process of GRR agents (demo_generating_agent/demo_reviewing_agent/demo_rewriting_agent).
        """

        instance: Agent = AgentManager().get_instance_obj('demo_grr_agent')
        result = instance.run(input="Write a short introduction about machine learning.")
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()

