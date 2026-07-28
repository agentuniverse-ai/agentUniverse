# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/7/20 10:00
# @Author  : agentuniverse
# @Email   : agentuniverse@example.com
# @FileName: minimax_openai_style_llm.py

from typing import Optional, Any, Union, Iterator, AsyncIterator

from pydantic import Field

from agentuniverse.base.annotation.trace import trace_llm
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

MINIMAX_MAX_CONTEXT_LENGTH = {
    "MiniMax-Text-01": 1000192,
    "MiniMax-VL-01": 1000192,
    "abab6.5s-chat": 8000,
    "abab6.5-chat": 8000,
    "abab5.5s-chat": 8000,
    "abab5.5-chat": 8000,
}


class MiniMaxOpenAIStyleLLM(OpenAIStyleLLM):
    """The agentUniverse default MiniMax llm module.

    LLM parameters, such as name/description/model_name/max_tokens,
    are injected into this class by the minimax_openai_style_llm.yaml configuration.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("MINIMAX_API_KEY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("MINIMAX_ORGANIZATION"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("MINIMAX_API_BASE"))
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("MINIMAX_PROXY"))

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

          The total length of input tokens and generated tokens is limited by the MiniMax model's context length.
          """
        if super().max_context_length():
            return super().max_context_length()
        return MINIMAX_MAX_CONTEXT_LENGTH.get(self.model_name, 8000)
