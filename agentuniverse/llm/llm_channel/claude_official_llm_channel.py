# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 14:16
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: claude_official_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

CLAUDE_MAX_CONTEXT_LENGTH = {
    "claude-3-opus-20240229": 200000,
    "claude-3-sonnet-20240229": 200000,
    "claude-3-haiku-20240307": 200000,
    "claude-2.1": 200000,
    "claude-2.0": 100000,
    "claude-instant-1.2": 100000,
}


class ClaudeOfficialLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "https://api.anthropic.com/v1/"

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return CLAUDE_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 8000)
