# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: qwen_openai_style_llm.py
from typing import Optional, Any, Union, Iterator, AsyncIterator

from dashscope import get_tokenizer
from pydantic import Field

from agentuniverse.base.annotation.trace import trace_llm
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

QWen_Max_CONTEXT_LENGTH = {
    # Turbo
    "qwen-turbo": 1_000_000,          # 当前等同 qwen-turbo-2025-02-11
    "qwen-turbo-latest": 1_000_000,   # 注：开启思考模式时，上下文会降到 131,072（但这里按“最大”口径取 1,000,000）
    "qwen-turbo-2025-04-28": 1_000_000,
    "qwen-turbo-0428": 1_000_000,
    "qwen-turbo-2025-02-11": 1_000_000,
    "qwen-turbo-0211": 1_000_000,
    "qwen-turbo-2024-09-19": 131_072,
    "qwen-turbo-0919": 131_072,
    "qwen-turbo-2024-06-24": 8_000,
    "qwen-turbo-0624": 8_000,

    # Plus
    "qwen-plus": 131_072,             # 当前等同 qwen-plus-2025-01-25
    "qwen-plus-latest": 131_072,
    "qwen-plus-2025-04-28": 131_072,
    "qwen-plus-0428": 131_072,
    "qwen-plus-2025-01-25": 131_072,
    "qwen-plus-0125": 131_072,
    "qwen-plus-2025-01-12": 131_072,
    "qwen-plus-0112": 131_072,

    # Max
    "qwen-max": 32_768,               # 当前等同 qwen-max-2024-09-19
    "qwen-max-latest": 131_072,
    "qwen-max-2025-01-25": 131_072,
    "qwen-max-0125": 131_072,
    "qwen-max-2024-09-19": 32_768,
    "qwen-max-0919": 32_768,
    "qwen-max-2024-04-28": 8_000,
    "qwen-max-0428": 8_000,
    "qwen-max-2024-04-03": 8_000,
    "qwen-max-0403": 8_000,
    "qwen-max-0107": 8_000,

    # Long
    "qwen-long": 10_000_000,
    "qwen-long-latest": 10_000_000,
    "qwen-long-2025-01-25": 10_000_000,
    "qwen-long-0125": 10_000_000,
}


class QWenOpenAIStyleLLM(OpenAIStyleLLM):
    """
        QWen OpenAI style LLM
        Args:
            api_key: API key for the model ,from dashscope : DASHSCOPE_API_KEY
            api_base: API base URL for the model, from dashscope : DASHSCOPE_API_BASE
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("DASHSCOPE_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env(
        "DASHSCOPE_API_BASE") or "https://dashscope.aliyuncs.com/compatible-mode/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("DASHSCOPE_PROXY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("DASHSCOPE_ORGANIZATION"))

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
        if super().max_context_length():
            return super().max_context_length()
        return QWen_Max_CONTEXT_LENGTH.get(self.model_name, 8000)

    def get_num_tokens(self, text: str) -> int:
        tokenizer = get_tokenizer(self.model_name)
        return len(tokenizer.encode(text))
