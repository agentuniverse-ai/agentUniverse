# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/12/12 23:03
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: insurance_consult_pro_agent_test.py
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    instance: Agent = AgentManager().get_instance_obj('insurance_consult_pro_agent')
    output = instance.run(input=question)
    return output.get_data('output')


if __name__ == '__main__':
    res = chat("保险产品A怎么升级")
    print("The result of the multi-agent execution is: \n" + res)
