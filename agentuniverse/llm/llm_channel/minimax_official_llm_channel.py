# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/7/20 10:00
# @Author  : agentuniverse
# @Email   : agentuniverse@example.com
# @FileName: minimax_official_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

# Context window for each MiniMax model — shared with MiniMaxOpenAIStyleLLM.
MINIMAX_MAX_CONTEXT_LENGTH = {
    "MiniMax-M3": 1000000,
    "MiniMax-M2.7": 204800,
    "MiniMax-M2.7-highspeed": 204800,
    "MiniMax-M2.5": 204800,
    "MiniMax-M2.5-highspeed": 204800,
    "MiniMax-M2.1": 204800,
    "MiniMax-M2.1-highspeed": 204800,
    "MiniMax-M2": 204800,
    "M2-her": 64000,
}

# Conservative fallback matching the smallest current catalog entry (M2-her).
_MINIMAX_DEFAULT_CONTEXT_LENGTH = 64000

# Official OpenAI-compatible base URLs.
#   China:        https://api.minimaxi.com/v1
#   International: https://api.minimax.io/v1
# Both endpoints serve the same OpenAI-compatible chat completions API; pick the
# one matching the user's account region via the channel yaml.
_MINIMAX_BASE_URL_CN = "https://api.minimaxi.com/v1"
_MINIMAX_BASE_URL_INTL = "https://api.minimax.io/v1"


class MiniMaxOfficialLLMChannel(LLMChannel):
    """MiniMax OpenAI-compatible official channel.

    Regional selection is driven by ``channel_api_base`` in the channel yaml
    (defaulting to the China endpoint). Examples for both regions are provided
    under ``examples/sample_standard_app/intelligence/agentic/llm/buildin/minimax/channel/``.
    """

    # Default to the China endpoint; override per-channel via yaml ``channel_api_base``.
    channel_api_base: Optional[str] = _MINIMAX_BASE_URL_CN

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return MINIMAX_MAX_CONTEXT_LENGTH.get(self.channel_model_name, _MINIMAX_DEFAULT_CONTEXT_LENGTH)