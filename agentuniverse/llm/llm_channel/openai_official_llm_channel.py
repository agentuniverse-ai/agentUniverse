# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 11:45
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: openai_official_llm_channel.py
from typing import Optional

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

OPENAI_MAX_CONTEXT_LENGTH = {
    # --- GPT-3.5 (legacy) ---
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-0301": 4096,
    "gpt-3.5-turbo-0613": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo-16k-0613": 16384,
    "gpt-3.5-turbo-1106": 16384,
    "gpt-3.5-turbo-0125": 16384,
    # Azure aliases
    "gpt-35-turbo": 4096,
    "gpt-35-turbo-16k": 16384,

    # --- GPT-4 (legacy) ---
    "gpt-4": 8192,
    "gpt-4-0314": 8192,
    "gpt-4-0613": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-32k-0613": 32768,

    # --- GPT-4 Turbo (legacy-ish) ---
    "gpt-4-1106-preview": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4-turbo-preview": 128000,

    # --- GPT-4.5 (deprecated preview) ---
    "gpt-4.5-preview": 128000,

    # --- GPT-4o family ---
    "gpt-4o": 128000,
    "gpt-4o-2024-05-13": 128000,
    "gpt-4o-2024-08-06": 128000,
    "gpt-4o-2024-11-20": 128000,

    "gpt-4o-mini": 128000,
    "gpt-4o-mini-2024-07-18": 128000,

    # audio preview (chat/completions)
    "gpt-4o-audio-preview": 128000,
    "gpt-4o-audio-preview-2024-10-01": 128000,
    "gpt-4o-audio-preview-2024-12-17": 128000,
    "gpt-4o-audio-preview-2025-06-03": 128000,

    "gpt-4o-mini-audio-preview": 128000,
    "gpt-4o-mini-audio-preview-2024-12-17": 128000,

    # search preview
    "gpt-4o-search-preview": 128000,
    "gpt-4o-mini-search-preview": 128000,

    # realtime
    "gpt-4o-realtime-preview": 32000,
    "gpt-4o-mini-realtime-preview": 16000,

    # speech-to-text / text-to-speech
    "gpt-4o-transcribe": 16000,
    "gpt-4o-transcribe-diarize": 16000,
    "gpt-4o-mini-transcribe": 16000,
    "gpt-4o-mini-tts": 2000,

    # --- GPT Audio / Realtime (GA) ---
    "gpt-audio": 128000,
    "gpt-audio-mini": 128000,
    "gpt-realtime": 32000,
    "gpt-realtime-mini": 32000,

    # --- GPT-4.1 family (1M context) ---
    "gpt-4.1": 1047576,
    "gpt-4.1-mini": 1047576,
    "gpt-4.1-nano": 1047576,

    # --- GPT-5 family ---
    "gpt-5": 400000,
    "gpt-5-mini": 400000,
    "gpt-5-nano": 400000,
    "gpt-5-pro": 400000,

    "gpt-5-chat-latest": 128000,
    "gpt-5.1": 400000,
    "gpt-5.1-chat-latest": 128000,
    "gpt-5.2": 400000,
    "gpt-5.2-chat-latest": 128000,
    "gpt-5.2-pro": 400000,

    # Codex variants
    "gpt-5-codex": 400000,
    "gpt-5.1-codex": 400000,
    "gpt-5.1-codex-mini": 400000,
    "gpt-5.1-codex-max": 400000,
    "gpt-5.2-codex": 400000,

    # --- o-series reasoning models ---
    "o1": 200000,
    "o1-pro": 200000,
    "o1-mini": 128000,

    "o3": 200000,
    "o3-mini": 200000,
    "o3-pro": 200000,
    "o3-deep-research": 200000,

    "o4-mini": 200000,
    "o4-mini-deep-research": 200000,

    # --- specialized / tooling ---
    "computer-use-preview": 8192,
    "codex-mini-latest": 200000,
}


class OpenAIOfficialLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "https://api.openai.com/v1"

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return OPENAI_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 128000)
