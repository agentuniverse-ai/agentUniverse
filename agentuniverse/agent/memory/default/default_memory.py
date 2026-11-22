# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/26 18:23
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: default_memory.py
from agentuniverse.agent.memory.chat_memory import ChatMemory
from agentuniverse.llm.default.default_openai_llm import DefaultOpenAILLM


class DefaultMemory(ChatMemory):
    """The aU default memory module."""

    def __init__(self, **kwargs):
        """The __init__ method.

        Some parameters, such as name/description/type/memory_key,
        are injected into this class by the default_memory.yaml configuration.


        Args:
            llm (LLM): the LLM instance used by this memory.
            default memory uses DefaultOpenAILLM(gpt-4o) object as the memory llm.
        """
        super().__init__(**kwargs)
        self.llm = DefaultOpenAILLM(model_name="gpt-4o")
