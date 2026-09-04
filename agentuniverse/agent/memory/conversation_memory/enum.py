# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/15 11:42
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: enum.py

import enum
from enum import Enum


@enum.unique
class ConversationMessageEnum(Enum):
    """Enum of the conversation message roles.

    Values: input (user) and output (agent/assistant).
    """

    INPUT = 'input'
    OUTPUT = 'output'


@enum.unique
class ConversationMessageSourceType(Enum):
    """Enum of the source types that can produce a conversation message.

    Values: agent, tool, knowledge, llm, user.
    """

    AGENT = 'agent'
    AGENT = 'agent'
    TOOL = 'tool'
    KNOWLEDGE = 'knowledge'
    LLM = 'llm'
    USER = 'user'
