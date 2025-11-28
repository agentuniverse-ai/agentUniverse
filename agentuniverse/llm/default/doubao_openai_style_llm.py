# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/25 09:52
# @Author  : huhao
# @Email   : hh446611@antgroup.com
# @FileName: doubao_openai_style_llm.py
from typing import Optional, Any, Union, Iterator, AsyncIterator

from dashscope import get_tokenizer
from pydantic import Field

from agentuniverse.base.annotation.trace import trace_llm
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

import requests
import os

DouBao_Max_CONTEXT_LENGTH = {
    "doubao-seed-1-6-lite-251015": 256000,
}


class DouBaoOpenAIStyleLLM(OpenAIStyleLLM):
    """
        DouBao OpenAI style LLM
        Args:
            api_key: API key for the model ,from os.env : DOUBAO_API_KEY
            api_base: API base URL for the model, from os.env : DOUBAO_API_BASE
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("DOUBAO_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env(
        "DOUBAO_API_BASE") or "https://ark.cn-beijing.volces.com/api/v3")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("DOUBAO_PROXY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("DOUBAO_ORGANIZATION"))

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
        return DouBao_Max_CONTEXT_LENGTH.get(self.model_name, 8000)

    def get_num_tokens(self, text: str) -> int:
        """
            Get the number of tokens in a text.
            
            Origin Rest API
            curl https://ark.cn-beijing.volces.com/api/v3/tokenization \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer 9fce90e0-9511-4bd8-a7b2-0f2808dbd313" \
            -d '{
                "model": "doubao-seed-1-6-lite",
                "text": ["天空为什么这么蓝"]                    
            }'
        """
        url = "https://ark.cn-beijing.volces.com/api/v3/tokenization"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('DOUBAO_API_KEY')}"  # 从环境变量获取 API Key
        }
        data = {
            "model": self.model_name,
            "text": [text]
        }

        response = requests.post(url, headers=headers, json=data)

        # 解析响应
        # print("分词结果：")
        # print(response.json())  # 输出分词结果

        return response.json()['data'][0]['total_tokens']