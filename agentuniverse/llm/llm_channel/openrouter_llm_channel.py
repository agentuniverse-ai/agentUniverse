# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/2 11:04
# @Author  : sien75
# @Email   : shaoning.shao@antgroup.com
# @FileName: openrouter_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

OPENROUTER_MAX_CONTEXT_LENGTH = {
    "openai/gpt-5.1": 400000,
    "openai/gpt-5.1-codex": 400000,
    "openai/gpt-5-mini": 400000,
    "openai/gpt-5-nano": 400000,
    "anthropic/claude-sonnet-4.5": 1000000,
    "anthropic/claude-opus-4.5": 200000,
    "anthropic/claude-haiku-4.5": 200000,
    "google/gemini-3-pro-preview": 1048576,
    "google/gemini-2.5-flash": 1048576,
    "google/gemini-2.0-flash-001": 1048576,
    "x-ai/grok-4.1-fast:free": 2000000,
    "x-ai/grok-code-fast-1": 256000,
    "x-ai/grok-4-fast": 2000000,
    "qwen/qwen3-next-80b-a3b-instruct": 262144,
    "qwen/qwen3-235b-a22b-2507": 131072,
    "deepseek/deepseek-chat-v3.1": 163840,
    "deepseek/deepseek-chat-v3-0324": 163840,
    "minimax/minimax-m2": 204800,
    "z-ai/glm-4.6": 202752,
    "moonshotai/kimi-k2-thinking": 262144,
}

class OpenRouterLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "https://openrouter.ai/api/v1/chat/completions"

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return OPENROUTER_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 128000)
