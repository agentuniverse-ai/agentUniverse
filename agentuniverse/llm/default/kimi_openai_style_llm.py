# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: kimi_openai_style_llm.py
from typing import Optional, Any, Union, Iterator, AsyncIterator

import requests
from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

KIMI_Max_CONTEXT_LENGTH = {
    "moonshot-v1-8k": 8000,
    "moonshot-v1-32k": 32000,
    "moonshot-v1-128k": 128000
}


class KIMIOpenAIStyleLLM(OpenAIStyleLLM):
    """
        KIMI's OpenAI Style LLM
        Attributes:
            api_key (Optional[str]): The API key to use for authentication. Defaults to None.
            api_base (Optional[str]): The base URL to use for the API. Defaults to None.
    """
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("KIMI_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env(
        "KIMI_API_BASE") or "https://api.moonshot.cn/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("KIMI_PROXY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("KIMI_ORGANIZATION"))

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
        return KIMI_Max_CONTEXT_LENGTH.get(self.model_name, 8000)

    def get_num_tokens(self, text: str) -> int:
        # Get the token count via HTTP
        messages = [{"role": "user", "content": text}]
        body = {"model": self.model_name, "messages": messages}
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.api_key}'}
        res = requests.post(f"{self.api_base}/tokenizers/estimate-token-count", headers=headers, json=body)
        return res.json().get('data').get('total_tokens')
