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
    """Enumeration of memory storage types.

    Attributes:
        SHORT_TERM: Short term memory, kept within a chat.
        LONG_TERM: Long term memory, persisted across chats.
    """

    SHORT_TERM = 'short_term'
    LONG_TERM = 'long_term'


@enum.unique
class ChatMessageEnum(Enum):
    """Enumeration of chat message role types.

    Attributes:
        SYSTEM: A system role message.
        HUMAN: A human (user) role message.
        AI: An AI (assistant) role message.
        INPUT: An input message.
        OUTPUT: An output message.
        USER: An alias of the human role.
        ASSISTANT: An alias of the AI role.
    """

    SYSTEM = 'system'
    HUMAN = 'human'
    AI = 'ai'
    INPUT = 'input'
    OUTPUT = 'output'
    USER = 'user'
    ASSISTANT = 'assistant'
