# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 16:20
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: default_openai_llm.py
from typing import Any, Optional, Iterator, Union, AsyncIterator

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OPENAI_MAX_CONTEXT_LENGTH, OpenAIStyleLLM


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
        if self._max_context_length:
            return self._max_context_length
        return OPENAI_MAX_CONTEXT_LENGTH.get(self.model_name, 4096)
