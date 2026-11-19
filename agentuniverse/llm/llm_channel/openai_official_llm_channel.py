# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 11:45
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: openai_official_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

OPENAI_MAX_CONTEXT_LENGTH = {
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-0301": 4096,
    "gpt-3.5-turbo-0613": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo-16k-0613": 16384,
    "gpt-35-turbo": 4096,
    "gpt-35-turbo-16k": 16384,
    "gpt-3.5-turbo-1106": 16384,
    "gpt-3.5-turbo-0125": 16384,
    "gpt-4-0314": 8192,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-32k-0613": 32768,
    "gpt-4-0613": 8192,
    "gpt-4-1106-preview": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4o": 128000,
    "gpt-4o-2024-05-13": 128000,
}


class OpenAIOfficialLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "https://api.openai.com/v1"

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured OpenAI model.

        Uses the value configured on the parent class when set, otherwise
        looks the model up in ``OPENAI_MAX_CONTEXT_LENGTH`` and falls back to
        128000 for unknown models.
        """
        if super().max_context_length():
            return super().max_context_length()
        return OPENAI_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 128000)
