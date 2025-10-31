# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    instance: Agent = AgentManager().get_instance_obj('primary_chinese_teacher_agent')
    output_object: OutputObject = instance.run(input=question)
    print(output_object.get_data('output'))


if __name__ == '__main__':
    chat("我是刚刚幼儿园毕业的小朋友，请问一年级上册要预习哪些课文？")
