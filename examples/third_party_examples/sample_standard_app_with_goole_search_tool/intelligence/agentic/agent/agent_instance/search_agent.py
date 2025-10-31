# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: search_agent.py

from agentuniverse.agent.default.agent_template import AgentTemplate


class SearchAgent(AgentTemplate):
    """搜索智能体
    
    专门用于搜索的智能体，集成了Google搜索和Google学术搜索功能。
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
