# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/26 17:18
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: insurance_agent_test.py
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
import uuid

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str, session_id: str):
    instance: Agent = AgentManager().get_instance_obj('insurance_agent')
    output_object: OutputObject = instance.run(input=question, session_id=session_id)
    print(output_object.get_data('output') + '\n')


if __name__ == '__main__':
    s_id = str(uuid.uuid4())
    chat("保险产品A怎么续保", s_id)
    chat("我刚才问了什么问题", s_id)
