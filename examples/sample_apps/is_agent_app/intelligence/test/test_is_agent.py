#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for IS (Implementation-Supervision) agent

@Time    : 2025/12/01
@Author  : Claude Code
"""

import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


class TestISAgent(unittest.TestCase):
    """Test cases for IS agent."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Initialize AgentUniverse
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_is_agent_basic(self):
        """Test basic IS agent execution."""
        agent: Agent = AgentManager().get_instance_obj('demo_is_agent')
        self.assertIsNotNone(agent)

        result = agent.run(
            input='编写一个简单的Python函数，计算列表中所有数字的平均值',
            checkpoint_count=2,
            max_corrections=1
        )

        self.assertIsNotNone(result)
        output = result.get('output', '')
        self.assertTrue(len(output) > 0)
        print(f"\n=== Test Basic IS Agent ===\n{output}\n")

    def test_is_agent_code_implementation(self):
        """Test IS agent for code implementation task."""
        agent: Agent = AgentManager().get_instance_obj('demo_is_agent')
        self.assertIsNotNone(agent)

        result = agent.run(
            input='实现一个Python类，表示银行账户，包括存款、取款和查询余额功能',
            checkpoint_count=3,
            max_corrections=2
        )

        self.assertIsNotNone(result)
        output = result.get('output', '')
        self.assertTrue(len(output) > 0)
        print(f"\n=== Test Code Implementation ===\n{output}\n")

    def test_is_agent_with_supervision(self):
        """Test IS agent with multiple checkpoints and supervision."""
        agent: Agent = AgentManager().get_instance_obj('demo_is_agent')
        self.assertIsNotNone(agent)

        result = agent.run(
            input='设计并实现一个简单的任务管理系统，支持添加、删除、查询和标记完成任务',
            checkpoint_count=4,
            max_corrections=2
        )

        self.assertIsNotNone(result)
        full_output = result.get('full_output', '')
        self.assertTrue(len(full_output) > 0)
        print(f"\n=== Test With Supervision ===\n{full_output}\n")


if __name__ == '__main__':
    unittest.main()
