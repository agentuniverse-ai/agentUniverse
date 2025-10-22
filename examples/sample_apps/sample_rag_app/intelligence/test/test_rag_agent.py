# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/06 22:55
# @Author  : zhangxi
# @Email   : 1724585800@qq.com
# @FileName: test_rag_agent.py
import unittest
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager

class RagAgentTest(unittest.TestCase):
    """
    Test cases for the rag agent
    """

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)

    def test_rag_agent(self):
        """Test demo rag agent."""
        instance: Agent = AgentManager().get_instance_obj('disease_rag_agent')
        query = '小明最近出现了发热表现，伴有畏寒现象，精神状态萎靡，注意力难以集中，时常感到头晕目眩，整个人呈现出明显的虚弱状态，请推测小明的疾病类型，并为其推荐治疗方法'
        output_object: OutputObject = instance.run(input=query)
        res_info = f"\nRag agent execution result is :\n"
        res_info += output_object.get_data('output')
        print(res_info)


if __name__ == '__main__':
    unittest.main()