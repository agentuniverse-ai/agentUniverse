# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 11:44
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: gemini_official_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

GEMINI_MAX_CONTEXT_LENGTH = {
    "gemini-3.0-pro": 2097152,        # ~2M tokens (2^21)
    "gemini-3.0-flash": 1048576,
    "gemini-2.0-pro": 2097152,
    "gemini-2.0-flash": 1048576,  # ~1M tokens (2^20)
    "gemini-1.5-pro": 2097152,  # ~2M tokens (2^21)
    "gemini-1.5-flash": 1048576,  # ~1M tokens (2^20)
    "gemini-1.5-flash-8b": 1048576,  # ~1M tokens
    "gemini-1.0-pro": 32768,  # 32k tokens (2^15)
    "gemini-1.0-pro-vision": 16384,  # 16k tokens
}


class GeminiOfficialLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "https://generativelanguage.googleapis.com/v1beta/openai/"

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return GEMINI_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 8000)
