# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 11:44
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: gemini_official_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

GEMINI_MAX_CONTEXT_LENGTH = {"gemini-2.0-flash": 1048576}


class GeminiOfficialLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "https://generativelanguage.googleapis.com/v1beta/openai/"

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return GEMINI_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 8000)
