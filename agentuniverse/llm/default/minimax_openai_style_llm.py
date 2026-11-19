# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/7/20 10:00
# @Author  : agentuniverse
# @Email   : agentuniverse@example.com
# @FileName: minimax_openai_style_llm.py

from typing import Optional

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# Context window for each MiniMax model, per the official OpenAI-compatible catalog
# (see https://api.minimaxi.com and https://api.minimax.io). Values are kept here in a
# single source of truth shared by both the LLM class and the channel class.
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

# Conservative fallback for any model name we haven't enumerated. Matches the
# smallest context window in the current catalog (M2-her) so we never advertise a
# larger window than the model actually supports.
_MINIMAX_DEFAULT_CONTEXT_LENGTH = 64000


class MiniMaxOpenAIStyleLLM(OpenAIStyleLLM):
    """The agentUniverse default MiniMax llm module.

    LLM parameters, such as name/description/model_name/max_tokens,
    are injected into this class by the minimax_openai_style_llm.yaml configuration.

    Regional base URL:
        - China:        https://api.minimaxi.com/v1   (default, see api_base below)
        - International: https://api.minimax.io/v1
    Switch by overriding ``api_base`` (or env var ``MINIMAX_API_BASE``) to point at
    the desired endpoint, or by wiring this LLM to a channel yaml that hard-codes the
    other endpoint. Both endpoints are OpenAI-compatible.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("MINIMAX_API_KEY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("MINIMAX_ORGANIZATION"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("MINIMAX_API_BASE"))
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("MINIMAX_PROXY"))

    def max_context_length(self) -> int:
        """Max context length.

        The total length of input tokens and generated tokens is limited by the MiniMax model's context length.
        """
        if super().max_context_length():
            return super().max_context_length()
        return MINIMAX_MAX_CONTEXT_LENGTH.get(self.model_name, _MINIMAX_DEFAULT_CONTEXT_LENGTH)