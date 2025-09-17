# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 14:13
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: baichuan_official_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

BAICHUAN_MAX_CONTEXT_LENGTH = {
    "Baichuan2-Turbo": 8000,
    "Baichuan2-Turbo-192k": 192000,
    "Baichuan3-Turbo": 8000,
    "Baichuan3-Turbo-128k": 128000,
    "Baichuan4": 8000,
}


class BaichuanOfficialLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "https://api.baichuan-ai.com/v1"

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return BAICHUAN_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 8000)
