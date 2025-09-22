# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/8 11:44
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
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

    instance: Agent = AgentManager().get_instance_obj('law_rag_agent')
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
    chat("张三在景区拍摄景区风景，李四闯入了镜头并被拍下。李四能否起诉张三侵犯肖像权，能否要求删除照片")
