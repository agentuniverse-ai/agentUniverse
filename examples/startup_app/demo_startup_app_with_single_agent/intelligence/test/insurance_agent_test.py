# # !/usr/bin/env python3
# # -*- coding:utf-8 -*-

# # @Time    : 2024/12/26 17:18
# # @Author  : wangchongshi
# # @Email   : wangchongshi.wcs@antgroup.com
# # @FileName: insurance_agent_test.py

# --- fix: map "import genai" -> official google.generativeai ---
import sys
import google.generativeai as _gemini_sdk
sys.modules['genai'] = _gemini_sdk
# ---------------------------------------------------------------


from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    instance: Agent = AgentManager().get_instance_obj('insurance_agent')
    output_object: OutputObject = instance.run(input=question)
    print(output_object.get_data('output'))


if __name__ == '__main__':
    chat("保险产品A怎么升级")
