# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/06 22:30
# @Author  : zhangxi
# @Email   : 1724585800@qq.com
# @FileName: legal_advice_rag_agent.py
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    """ Rag agent example.

    The rag agent in agentUniverse becomes a chatbot and can ask questions to get the answer.
    """

    instance: Agent = AgentManager().get_instance_obj('disease_rag_agent')
    output_object: OutputObject = instance.run(input=question)

    question = f"\nYour event is :\n"
    question += output_object.get_data('input')
    print(question)

    background_info = f"\nRetrieved background is :\n"
    background_info += output_object.get_data('background').replace("\n","")
    print(background_info)

    res_info = f"\nRag chat bot execution result is :\n"
    res_info += output_object.get_data('output')
    print(res_info)


if __name__ == '__main__':
    chat("小明最近出现了发热表现，伴有畏寒现象，精神状态萎靡，注意力难以集中，时常感到头晕目眩，"
         "整个人呈现出明显的虚弱状态，请推测小明的疾病类型，并为其推荐治疗方法和药物推荐")
