# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2/17/25
# @Author  : quesheng
# @Email   : huiyi.why@antgroup.com
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


class GrrAgentTest(unittest.TestCase):
    """Test cases for the grr agent"""

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_grr_agent(self):
        """Test demo grr agent.

        The overall process of grr agents (demo_rag_agent/demo_reviewing_agent/demo_rewriting_agent).
        """

        instance: Agent = AgentManager().get_instance_obj('demo_grr_agent')
        instance.run(input='帮我分析下2023年巴菲特减持比亚迪原因')


if __name__ == '__main__':
    unittest.main()
