# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/30 15:53
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: rag_agent_case_test.py

import time
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
import uuid

from agentuniverse.base.context.framework_context_manager import FrameworkContextManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str, session_id: str):
    """Run a chat request against the rag agent case.

    Args:
        question: The user question to ask the agent.
        session_id: The session id used to keep the conversation context.
    """
    FrameworkContextManager().set_context('trace_id',uuid.uuid4().hex)
    instance: Agent = AgentManager().get_instance_obj('rag_agent_case')
    output_object: OutputObject = instance.run(input=question, session_id=session_id)
    # print(output_object.get_data('output') + '\n')


if __name__ == '__main__':
    s_id = "d369ff14-1ad4-4192-b624-18c8cf1a0c15"
    FrameworkContextManager().set_context('session_id', s_id)
    chat("我想去东京旅游，你知道东京天气预报么", s_id)
    chat("这种天气我应该穿什么衣服", s_id)
    chat("有什么推荐的景点么", s_id)
    chat("可以帮我规划一个三天的旅行路线么", s_id)
    chat("我从上海出发，乘坐什么交通工具比较合适", s_id)
    chat("我不太喜欢坐高铁", s_id)
    chat("我不想坐飞机", s_id)
    time.sleep(5)
    # FrameworkContextManager().set_context('trace_id', uuid.uuid4().hex)
    # chat("我刚才问了什么问题", s_id)
