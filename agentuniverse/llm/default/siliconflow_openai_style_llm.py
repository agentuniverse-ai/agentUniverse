# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : dxz0069
# @FileName: siliconflow_openai_style_llm.py

from typing import Optional

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

SILICONFLOW_MAX_CONTEXT_LENGTH = {
    "Qwen/Qwen2.5-7B-Instruct": 32768,
    "Qwen/Qwen2.5-32B-Instruct": 32768,
    "Qwen/Qwen2.5-72B-Instruct": 32768,
    "Qwen/Qwen3-8B": 131072,
    "Qwen/Qwen3-32B": 131072,
    "Qwen/Qwen3-235B-A22B-Instruct": 131072,
    "deepseek-ai/DeepSeek-V3": 65536,
    "deepseek-ai/DeepSeek-R1": 65536,
    "THUDM/glm-4-9b-chat": 131072,
    "01-ai/Yi-1.5-9B-Chat-16K": 16384,
    "meta-llama/Meta-Llama-3.1-8B-Instruct": 131072,
}


class DefaultSiliconFlowLLM(OpenAIStyleLLM):
    """The agentUniverse default SiliconFlow llm module.

    SiliconFlow (https://siliconflow.cn) serves popular open source models
    through an OpenAI-compatible API, e.g.
    `Qwen/Qwen2.5-72B-Instruct` and `deepseek-ai/DeepSeek-V3`.

    LLM parameters, such as name/description/model_name/max_tokens,
    are injected into this class by the default_siliconflow_llm.yaml configuration.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SILICONFLOW_API_KEY"))
    api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("SILICONFLOW_API_BASE") or "https://api.siliconflow.cn/v1")

    def max_context_length(self) -> int:
        """Max context length.

        The total length of input tokens and generated tokens is limited by the model's context length.
        """
        if self._max_context_length:
            return self._max_context_length
        return SILICONFLOW_MAX_CONTEXT_LENGTH.get(self.model_name, 4096)
