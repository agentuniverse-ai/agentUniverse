# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/13 19:38
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: huggingface_hub_openai_style_llm.py

from typing import Optional, Any, Union, Iterator, AsyncIterator

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM


class HuggingFaceHubLLM(OpenAIStyleLLM):
    """
    Huggingface hub OpenAI style LLM
    Args:
        api_key: API key for the model, obtain from huggingface
        api_base: API base URL for the model, from huggingface, default is https://router.huggingface.co/v1
        proxy: your proxy, default is None
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("HUGGINGFACE_HUB_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("HUGGINGFACE_HUB_API_BASE") or "https://router.huggingface.co/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("HUGGINGFACE_HUB_PROXY"))


    def _validate_call_params(self, messages: list) -> None:
        """Validate parameters before making API calls."""
        if not messages:
            raise ValueError("Messages cannot be empty")
        
        if not isinstance(messages, list):
            raise ValueError("Messages must be a list")
        
        if self.api_key is None:
            raise ValueError("API key is required but not provided. Please set HUGGINGFACE_HUB_API_KEY environment variable or provide api_key parameter")
        
        if not self.api_key.strip():
            raise ValueError("API key cannot be empty string")
        
        if self.api_base is None:
            raise ValueError("API base URL is required but not provided")
        
        if not self.api_base.strip():
            raise ValueError("API base URL cannot be empty string")

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """ The call method of the LLM.
        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        self._validate_call_params(messages)
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """ The async call method of the LLM.
        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        self._validate_call_params(messages)
        return await super()._acall(messages, **kwargs)