# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 11:38
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: kimi_official_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

KIMI_MAX_CONTEXT_LENGTH = {
    # ===== Moonshot-v1 (text) =====
    "moonshot-v1-8k": 8192,        # 8,192 tokens
    "moonshot-v1-32k": 32768,      # 32,768 tokens
    "moonshot-v1-128k": 131072,    # 131,072 tokens
    "moonshot-v1-auto": 131072,

    # ===== Moonshot-v1 (vision preview) =====
    "moonshot-v1-8k-vision-preview": 8192,
    "moonshot-v1-32k-vision-preview": 32768,
    "moonshot-v1-128k-vision-preview": 131072,

    # ===== Kimi K2 (text / agentic) =====
    "kimi-k2-0711-preview": 131072,       # 128K
    "kimi-k2-0905-preview": 262144,       # 256K
    "kimi-k2-turbo-preview": 262144,      # 256K (高速版，对标最新 k2)
    "kimi-k2-thinking": 262144,           # 256K (思考模型)
    "kimi-k2-thinking-turbo": 262144,     # 256K (思考+高速)

    # ===== Kimi K2.5 (native multimodal) =====
    "kimi-k2.5": 262144,                 # 256K (多模态：文本+图像)
}


class KimiOfficialLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "https://api.moonshot.cn/v1"

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return KIMI_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 8000)
