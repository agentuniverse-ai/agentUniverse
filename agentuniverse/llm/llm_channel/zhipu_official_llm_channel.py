# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 11:36
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: zhipu_official_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

ZHIPU_MAX_CONTEXT_LENGTH = {
    # ===== GLM-4 系列（docs: glm-4）=====
    "GLM-4-Plus": 128000,
    "glm-4-plus": 128000,

    "GLM-4-Air": 128000,              # 兼容旧命名（实际对应 Air-250414 / 或 glm-4-air）
    "glm-4-air": 128000,
    "GLM-4-Air-250414": 128000,
    "glm-4-air-250414": 128000,

    "GLM-4-AirX": 8000,
    "glm-4-airx": 8000,

    "GLM-4-Flash": 128000,            # 兼容旧命名
    "glm-4-flash": 128000,
    "GLM-4-Flash-250414": 128000,
    "glm-4-flash-250414": 128000,

    "GLM-4-FlashX": 128000,           # 兼容旧命名
    "glm-4-flashx": 128000,
    "GLM-4-FlashX-250414": 128000,
    "glm-4-flashx-250414": 128000,

    "GLM-4": 128000,                  # 文档/示例里仍能见到 glm-4 作为模型编码
    "glm-4": 128000,

    # 你原来写的快照名（保留）
    "GLM-4-0520": 128000,

    # ===== 超长上下文 =====
    "GLM-4-Long": 1000000,
    "glm-4-long": 1000000,

    # ===== 新旗舰/新免费模型（docs: model-overview / glm-4.7 / glm-4.7-flash）=====
    "GLM-4.7": 200000,
    "glm-4.7": 200000,
    "GLM-4.7-FlashX": 200000,
    "glm-4.7-flashx": 200000,
    "GLM-4.7-Flash": 200000,
    "glm-4.7-flash": 200000,

    "GLM-4.6": 200000,
    "glm-4.6": 200000,

    "GLM-4.5-Air": 128000,
    "glm-4.5-air": 128000,
    "GLM-4.5-AirX": 128000,
    "glm-4.5-airx": 128000,
    "GLM-4.5-Flash": 128000,
    "glm-4.5-flash": 128000,

    # ===== 推理模型 GLM-Z1（文档提示：系列已下线，但这里给你留兼容映射）=====
    "GLM-Z1-Air": 128000,
    "glm-z1-air": 128000,
    "GLM-Z1-AirX": 32000,
    "glm-z1-airx": 32000,
    "GLM-Z1-FlashX": 128000,
    "glm-z1-flashx": 128000,
    "GLM-Z1-Flash": 128000,
    "glm-z1-flash": 128000,
}


class ZhiPuOfficialLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "https://open.bigmodel.cn/api/paas/v4/"

    def max_context_length(self) -> int:
        """Max context length.

          The total length of input tokens and generated tokens is limited by the openai model's context length.
          """
        return ZHIPU_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 128000)
