# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/7/20 10:00
# @Author  : agentuniverse
# @Email   : agentuniverse@example.com
# @FileName: minimax_official_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

MINIMAX_MAX_CONTEXT_LENGTH = {
    "MiniMax-Text-01": 1000192,
    "MiniMax-VL-01": 1000192,
    "abab6.5s-chat": 8000,
    "abab6.5-chat": 8000,
    "abab5.5s-chat": 8000,
    "abab5.5-chat": 8000,
}


class MiniMaxOfficialLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = 'https://api.minimaxi.com/v1'

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return MINIMAX_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 8000)
