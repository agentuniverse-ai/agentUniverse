# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/25 17:19
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: test_perp_agent.py
import unittest
import asyncio

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


class PerpAgentTest(unittest.TestCase):
    """Test cases for the peer agent"""

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_perp_agent_with_direct_answer(self):
        """Test demo perp agent with direct answer.

        The overall process of perp agents (demo_dynamic_planning_agent/demo_analysis_agent/demo_reporter_agent).
        """

        instance: Agent = AgentManager().get_instance_obj('demo_perp_agent')
        result = instance.run(input='100+100=？')
        self.assertIsNotNone(result)

    def test_perp_agent_sync(self):
        """Test demo perp agent with sync.

        The overall process of perp agents (demo_dynamic_planning_agent/demo_analysis_agent/demo_reporter_agent).
        """

        instance: Agent = AgentManager().get_instance_obj('demo_perp_agent')
        result = instance.run(input="分析最新的国内CPI数据，然后绘制一份精美的可视化报告给我")
        self.assertIsNotNone(result)

    def test_perp_agent_async(self):
        """Test demo perp agent with async.

        The overall process of perp agents (demo_dynamic_planning_agent/demo_analysis_agent/demo_reporter_agent).
        """

        instance: Agent = AgentManager().get_instance_obj('demo_perp_agent')
        
        async def run_async_test():
            return await instance.async_run(input="分析最新的国内CPI数据，然后绘制一份精美的可视化报告给我")
        
        # Run the async function using asyncio.run()
        result = asyncio.run(run_async_test())
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
