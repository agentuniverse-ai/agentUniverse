# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 16:20
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: default_openai_llm.py
from typing import Any, Optional, Iterator, Union, AsyncIterator

from pydantic import Field

from agentuniverse.base.annotation.trace import trace_llm
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

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


class DefaultOpenAILLM(OpenAIStyleLLM):
    """The agentUniverse default openai llm module.

    LLM parameters, such as name/description/model_name/max_tokens,
    are injected into this class by the default_openai_llm.yaml configuration.
    """
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_API_KEY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_ORGANIZATION"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_API_BASE"))
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """ The call method of the LLM.

        Users can customize how the model interacts by overriding call method of the LLM class.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """ The async call method of the LLM.

        Users can customize how the model interacts by overriding acall method of the LLM class.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return await super()._acall(messages, **kwargs)

    def max_context_length(self) -> int:
        """Max context length.

          The total length of input tokens and generated tokens is limited by the openai model's context length.
          """
        return OPENAI_MAX_CONTEXT_LENGTH.get(self.model_name, 4096)
