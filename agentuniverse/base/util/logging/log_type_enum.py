# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/5 16:22
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: log_type_const.py
from enum import Enum


class LogTypeEnum(str, Enum):
    default = 'default'
    sls = 'sls'
    flask_request = 'flask_request'
    flask_response = 'flask_response'
    agent_input = 'agent_input'
    agent_invocation = 'agent_invocation'
    agent_first_token = 'agent_first_token'
    llm_input = 'llm_input'
    llm_invocation = 'llm_invocation'
    llm_token_usage = 'llm_token_usage'
    tool_input = 'tool_input'
    tool_invocation = 'tool_invocation'