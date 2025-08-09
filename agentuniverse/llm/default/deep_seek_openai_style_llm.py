# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 17:49
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: deep_seek_openai_style_llm.py

from typing import Optional, Any, Union, Iterator, AsyncIterator

from pydantic import Field

from agentuniverse.base.annotation.trace import trace_llm
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

DEEpSEEkMAXCONTETNLENGTH = {
    "deepseek-chat": 64000,
    "deepseek-coder": 32000,
    "deepseek-reasoner": 64000
}


class DefaultDeepSeekLLM(OpenAIStyleLLM):
    """The agentUniverse default openai llm module.

    LLM parameters, such as name/description/model_name/max_tokens,
    are injected into this class by the default_openai_llm.yaml configuration.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("DEEPSEEK_API_KEY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("DEEPSEEK_ORGANIZATION"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("DEEPSEEK_API_BASE"))
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("DEEPSEEK_PROXY"))

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
        return DEEpSEEkMAXCONTETNLENGTH.get(self.model_name, 4096)

