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
    INPUT = "input"
    OUTPUT = "output"


@enum.unique
class ConversationMessageSourceType(Enum):
    AGENT = "agent"
    TOOL = "tool"
    KNOWLEDGE = "knowledge"
    LLM = "llm"
    USER = "user"
