# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/15 11:42
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: enum.py
import enum
from enum import Enum


@enum.unique
class MemoryTypeEnum(Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


@enum.unique
class ChatMessageEnum(Enum):
    SYSTEM = "system"
    HUMAN = "human"
    AI = "ai"
    INPUT = "input"
    OUTPUT = "output"
    USER = "user"
    ASSISTANT = "assistant"
