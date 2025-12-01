#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time : 2025/12/1 10:37
# @Author : junxun
# @mail : junxun.t@ant-intl.com
# @FileName :gemini_openai_style_llm.py

from typing import Optional, Any, Union, Iterator, AsyncIterator

from pydantic import Field
import google.generativeai as genai

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput

GEMINI_MAX_CONTEXT_LENGTH = {
    "gemini-1.5-flash": 1048576,
    "gemini-1.5-pro": 1048576,
    "gemini-1.0-pro": 30720,
}


class GoogleGenaiLLM(LLM):
    """Google Genai LLM
    
    Note:
        The environment variable `GOOGLE_API_KEY` must be set.
    """
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("GOOGLE_API_KEY"))
    model_name: str = Field(default="gemini-1.5-flash")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        genai.configure(api_key=self.api_key)

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """ The call method of the LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            Union[LLMOutput, Iterator[LLMOutput]]: The output of the LLM.
        """
        streaming = kwargs.get('streaming', False)
        generation_config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }
        model = genai.GenerativeModel(self.model_name)
        
        if streaming:
            response = model.generate_content(messages, stream=True, generation_config=generation_config)
            return self._handle_streaming_response(response)
        else:
            response = model.generate_content(messages, generation_config=generation_config)
            text = response.text
            return LLMOutput(text=text, raw=response.__dict__)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """ The async call method of the LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            Union[LLMOutput, AsyncIterator[LLMOutput]]: The output of the LLM.
        """
        streaming = kwargs.get('streaming', False)
        generation_config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }
        model = genai.GenerativeModel(self.model_name)

        if streaming:
            response = await model.generate_content_async(messages, stream=True, generation_config=generation_config)
            return self._ahandle_streaming_response(response)
        else:
            response = await model.generate_content_async(messages, generation_config=generation_config)
            text = response.text
            return LLMOutput(text=text, raw=response.__dict__)

    def _handle_streaming_response(self, response: Iterator) -> Iterator[LLMOutput]:
        """Handle streaming response."""
        for chunk in response:
            if chunk.text:
                yield LLMOutput(text=chunk.text, raw=chunk.__dict__)

    async def _ahandle_streaming_response(self, response: AsyncIterator) -> AsyncIterator[LLMOutput]:
        """Handle async streaming response."""
        async for chunk in response:
            if chunk.text:
                yield LLMOutput(text=chunk.text, raw=chunk.__dict__)

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens in the text.
        
        Args:
            text (str): The text to count the tokens of.
        
        Returns:
            int: The number of tokens in the text.
        """
        model = genai.GenerativeModel(self.model_name)
        return model.count_tokens(text).total_tokens

    @property
    def max_context_length(self) -> int:
        """Get the maximum context length of the model."""
        return GEMINI_MAX_CONTEXT_LENGTH.get(self.model_name, 8000)
