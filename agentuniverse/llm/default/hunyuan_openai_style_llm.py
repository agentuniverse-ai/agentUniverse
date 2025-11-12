# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/4 11:23
# @Author  : sunhailin.shl
# @Email   : sunhailin.shl@antgroup.com
# @FileName: hunyuan_openai_style_llm.py
from typing import Optional, Any, Union, Iterator, AsyncIterator

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

HUNYUN_MAX_CONTEXT_LENGTH = {
    "hunyuan-t1-latest": 32768,
    "hunyuan-t1-20250822": 32768,
    "hunyuan-a13b": 229376,
    "hunyuan-turbos-latest": 32768,
    "hunyuan-turbos-20250716": 32768,
    "hunyuan-turbos-longtext-128k-20250325": 131072,
}


class HunyuanOpenAIStyleLLM(OpenAIStyleLLM):
    """
    Hunyuan OpenAI style LLM
    Args:
        api_key: API key for the model ,from dashscope : HUNYUAN_API_KEY
        api_base: API base URL for the model, from dashscope : HUNYUAN_API_BASE
    """

    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("HUNYUAN_API_KEY"))
    api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("HUNYUAN_API_BASE")
                                or "https://api.hunyuan.cloud.tencent.com/v1"
    )

    def _call(
        self,
        messages: list,
        **kwargs: Any,
    ) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """The call method of the LLM.

        Users can customize how the model interacts by overriding
        call method of the LLM class.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return super()._call(messages, **kwargs)

    async def _acall(
        self,
        messages: list,
        **kwargs: Any,
    ) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """The async call method of the LLM.

        Users can customize how the model interacts by overriding
        acall method of the LLM class.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return await super()._acall(messages, **kwargs)

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return HUNYUN_MAX_CONTEXT_LENGTH.get(self.model_name, 8000)
