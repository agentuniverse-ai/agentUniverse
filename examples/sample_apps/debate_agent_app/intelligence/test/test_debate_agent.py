#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for Debate agent

@Time    : 2026/10/18
@Author  : lljjcc426
"""

import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


class TestDebateAgent(unittest.TestCase):
    """Test cases for Debate agent."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Initialize AgentUniverse
        # Path is relative to where the test is run from (debate_agent_app/)
        AgentUniverse().start(config_path='config/config.toml')

    def test_debate_agent_basic(self):
        """Test basic Debate agent execution."""
        agent: Agent = AgentManager().get_instance_obj('demo_debate_agent')
        self.assertIsNotNone(agent)

        result = agent.run(
            input='判断一个字符串是否为回文串，并说明你的思路',
            debate_rounds=2,
            consensus_threshold=60
        )

        self.assertIsNotNone(result)
        result_dict = result.to_dict()
        output = result_dict.get('output', '')
        self.assertTrue(len(output) > 0)
        print(f"\n=== Test Basic Debate Agent ===\n{output}\n")

    def test_debate_agent_multi_round(self):
        """Test Debate agent with multiple rounds and a strict threshold."""
        agent: Agent = AgentManager().get_instance_obj('demo_debate_agent')
        self.assertIsNotNone(agent)

        result = agent.run(
            input='为一个图书馆管理系统设计核心数据模型，并说明主要实体之间的关系',
            debate_rounds=3,
            consensus_threshold=80
        )

        self.assertIsNotNone(result)
        result_dict = result.to_dict()
        output = result_dict.get('output', '')
        full_output = result_dict.get('full_output', '')
        self.assertTrue(len(output) > 0)
        self.assertTrue(len(full_output) > 0)
        print(f"\n=== Test Multi-Round Debate ===\n{output}\n")

    def test_debate_agent_architecture_design(self):
        """Test Debate agent for an architecture design task."""
        agent: Agent = AgentManager().get_instance_obj('demo_debate_agent')
        self.assertIsNotNone(agent)

        result = agent.run(
            input='设计一个高并发场景下的短链接生成服务，要求给出核心架构、关键数据结构与容错方案',
            debate_rounds=2,
            consensus_threshold=70
        )

        self.assertIsNotNone(result)
        result_dict = result.to_dict()
        output = result_dict.get('output', '')
        self.assertTrue(len(output) > 0)
        print(f"\n=== Test Architecture Design ===\n{output}\n")


if __name__ == '__main__':
    unittest.main()
