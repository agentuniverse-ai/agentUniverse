# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: baichuan_openai_style_llm.py
from typing import Optional, Any, Union, Iterator, AsyncIterator

from pydantic import Field

from agentuniverse.base.annotation.trace import trace_llm
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

BAICHUAN_Max_CONTEXT_LENGTH = {
    "Baichuan2-Turbo": 8000,
    "Baichuan2-Turbo-192k": 192000,
    "Baichuan3-Turbo": 8000,
    "Baichuan3-Turbo-128k": 128000,
    "Baichuan4": 8000,
}


class BAICHUANOpenAIStyleLLM(OpenAIStyleLLM):
    """
    BAICHUAN OpenAI Style LLM
    Args:
        api_key (Optional[str]): API key for the model. Defaults to None.
        api_base (Optional[str]): API base URL for the model. Defaults to "https://api.openai.com/v1".
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("BAICHUAN_API_KEY"))
    api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("BAICHUAN_API_BASE") or "https://api.baichuan-ai.com/v1"
    )
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("BAICHUAN_PROXY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("BAICHUAN_ORGANIZATION"))

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return BAICHUAN_Max_CONTEXT_LENGTH.get(self.model_name, 8000)

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """The call method of the LLM.

        Users can customize how the model interacts by overriding call method of the LLM class.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """The async call method of the LLM.

        Users can customize how the model interacts by overriding acall method of the LLM class.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return await super()._acall(messages, **kwargs)
