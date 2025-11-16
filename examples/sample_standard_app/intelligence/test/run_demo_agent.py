# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: run_demo_agent.py

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)
#examples/sample_standard_app/config/config.toml

def chat(question: str, session_id=None):
    """ Peer agents example.

    The peer agents in agentUniverse become a chatbot and can ask questions to get the answer.
    """
    instance: Agent = AgentManager().get_instance_obj('demo_agent')
    output_object = instance.run(input=question, session_id=session_id)
    res_info = f"\nDemo agent execution result is :\n"
    res_info += output_object.get_data('output').get('text')
    print(res_info)


if __name__ == '__main__':
    chat(question="分析下巴菲特减持比亚迪的原因", session_id="test-01")
    print('testtest')
    chat(question="我刚才问了什么问题", session_id="test-01")
