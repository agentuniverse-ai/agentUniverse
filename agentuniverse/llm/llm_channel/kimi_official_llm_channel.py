# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 11:38
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: kimi_official_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

KIMI_MAX_CONTEXT_LENGTH = {
    "moonshot-v1-8k": 8000,
    "moonshot-v1-32k": 32000,
    "moonshot-v1-128k": 128000
}


class KimiOfficialLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "https://api.moonshot.cn/v1"

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Kimi model.

        Uses the value configured on the parent class when set, otherwise
        looks the model up in ``KIMI_MAX_CONTEXT_LENGTH`` and falls back to
        8000 for unknown models.
        """
        if super().max_context_length():
            return super().max_context_length()
        return KIMI_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 8000)
