# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 11:36
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: zhipu_official_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

ZHIPU_MAX_CONTEXT_LENGTH = {
    "GLM-4-Plus": 128000,
    "GLM-4-0520": 128000,
    "GLM-4-AirX": 8000,
    "GLM-4-Air": 128000,
    "GLM-4-Long": 1000000,
    "GLM-4-Flash": 128000,
    "GLM-4": 128000,
}


class ZhiPuOfficialLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "https://open.bigmodel.cn/api/paas/v4/"

    def max_context_length(self) -> int:
        """Max context length.

        The total length of input tokens and generated tokens is limited by the openai model's context length.
        """
        return ZHIPU_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 128000)
