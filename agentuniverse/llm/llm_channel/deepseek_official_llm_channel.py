# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 14:07
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: deepseek_official_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

DEEPSEEK_MAX_CONTEXT_LENGTH = {
    "deepseek-chat": 128000,
    "deepseek-coder": 128000,
    "deepseek-reasoner": 128000
}


class DeepseekOfficialLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = 'https://api.deepseek.com/v1'

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return DEEPSEEK_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 8000)
