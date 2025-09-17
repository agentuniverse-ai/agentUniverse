#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time : 2025/2/12 14:37
# @Author : wozhapen
# @mail : wozhapen@gmail.com
# @FileName :gemini_openai_style_llm.py

from typing import Optional, Any, Union, Iterator, AsyncIterator

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# Define maximum context lengths for different Gemini models
GEMINI_MAX_CONTEXT_LENGTH = {
    "gemini-2.0-flash": 1048576  # Example value, adjust as needed
    # Add more Gemini models and their context lengths as needed
}


class GeminiOpenAIStyleLLM(OpenAIStyleLLM):
    """
    Gemini OpenAI style LLM
    Args:
        api_key: API key for the model ,from Google AI Studio or Vertex AI
        api_base: API base URL for the model (optional, depending on the service)
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("GOOGLE_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("GOOGLE_API_BASE"))
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("GOOGLE_PROXY"))
    organization: Optional[str] = None  # Gemini does not require organization.

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

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return GEMINI_MAX_CONTEXT_LENGTH.get(self.model_name, 8000)  # Default context length if model not found

    """ 
        The current Google client does not support setting a proxy, 
        therefore local debugging is not supported.
    """
    # def get_num_tokens(self, text: str) -> int:
    #     """
    #       use genai
    #     """
    #     try:
    #         from google import genai
    #         client = genai.Client(api_key=self.api_key)
    #         response = client.models.count_tokens(
    #             model=self.model_name,
    #             contents=text,
    #         )
    #         return response.total_tokens
    #     except Exception as e:
    #         print(
    #             f"Warning: Unable to accurately count tokens for Gemini. Error: {e}")
    #         # Fallback:  Simple word count as a very rough estimate
    #         return len(text.split())
