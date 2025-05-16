# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/4/15 11:19
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_peer_agent.py
import queue
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


class PeerAgentTest(unittest.TestCase):
    """Test cases for the peer agent"""

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_peer_agent(self):
        """Test demo peer agent.

        The overall process of peer agents (demo_planning_agent/demo_executing_agent/demo_expressing_agent/demo_reviewing_agent).
        """
        instance: Agent = AgentManager().get_instance_obj(
            'openai_protocol_peer_agent')
        messages = [
            {"role": "user", "content": '分析下巴菲特减持比亚迪的原因'},
        ]
        instance.run(messages=messages, stream=queue.Queue())


if __name__ == '__main__':
    unittest.main()
