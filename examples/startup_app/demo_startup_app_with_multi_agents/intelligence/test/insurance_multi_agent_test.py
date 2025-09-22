# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/11/28 17:17
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: insurance_multi_agent_test.py
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    instance: Agent = AgentManager().get_instance_obj('insurance_consult_agent')
    output_object: OutputObject = instance.run(input=question)
    print("The result of the multi-agent execution is: \n" + output_object.get_data('output'))


if __name__ == '__main__':
    chat("保险产品A怎么升级")
