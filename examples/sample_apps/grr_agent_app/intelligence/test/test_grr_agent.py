# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @Author  : Claude Code
# @FileName: test_grr_agent.py
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


class GRRAgentTest(unittest.TestCase):
    """Test cases for the GRR (Generate-Review-Rewrite) agent"""

    def setUp(self) -> None:
        """Set up test environment by starting AgentUniverse."""
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_grr_agent_basic(self):
        """Test basic GRR agent functionality.

        Tests the overall process of GRR agents:
        - demo_generating_agent: Generates initial content
        - demo_reviewing_agent: Reviews and evaluates content
        - demo_rewriting_agent: Rewrites content based on feedback
        """
        instance: Agent = AgentManager().get_instance_obj('demo_grr_agent')
        result = instance.run(input='写一篇关于人工智能在医疗领域应用的短文，约200字')
        print("\n=== GRR Agent Test Result ===")
        print(result)
        self.assertIsNotNone(result)
        self.assertIn('output', result)

    def test_grr_agent_content_generation(self):
        """Test GRR agent for content generation tasks."""
        instance: Agent = AgentManager().get_instance_obj('demo_grr_agent')
        result = instance.run(input='为一家科技公司撰写一段产品介绍，突出创新性和用户体验')
        print("\n=== Content Generation Test ===")
        print(result)
        self.assertIsNotNone(result)
        self.assertIn('output', result)

    def test_grr_agent_creative_writing(self):
        """Test GRR agent for creative writing tasks."""
        instance: Agent = AgentManager().get_instance_obj('demo_grr_agent')
        result = instance.run(input='写一个关于未来城市生活的简短故事开头')
        print("\n=== Creative Writing Test ===")
        print(result)
        self.assertIsNotNone(result)
        self.assertIn('output', result)


if __name__ == '__main__':
    unittest.main()
