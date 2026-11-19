# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/1 14:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_rag_agent.py
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse


class RagAgentTest(unittest.TestCase):
    """
    Test cases for the rag agent
    """

    def setUp(self) -> None:
        """Set up the test fixture before each test.
        """
        AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)

    def test_rag_agent(self):
        """Test demo rag agent."""
        instance: Agent = AgentManager().get_instance_obj('law_rag_agent')
        query = '张三在景区拍摄景区风景，李四闯入了镜头并被拍下。李四能否起诉张三侵犯肖像权，能否要求删除照片'
        output_object: OutputObject = instance.run(input=query)
        res_info = f"\nRag agent execution result is :\n"
        res_info += output_object.get_data('output')
        print(res_info)


if __name__ == '__main__':
    unittest.main()
