# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/25 10:00
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: huggingface_hub_llm.py
from typing import Optional, Any, Union, Iterator, AsyncIterator

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput

HUGGINGFACE_MAX_CONTEXT_LENGTH = {
    "gpt2": 1024,
    "gpt2-medium": 1024,
    "gpt2-large": 1024,
    "gpt2-xl": 1024,
    "EleutherAI/gpt-neo-2.7B": 2048,
    "EleutherAI/gpt-j-6B": 2048,
    "bigscience/bloom": 2048,
    "bigscience/bloom-7b1": 2048,
    "facebook/opt-1.3b": 2048,
    "facebook/opt-2.7b": 2048,
    "facebook/opt-6.7b": 2048,
    "facebook/opt-13b": 2048,
    "meta-llama/Llama-2-7b": 4096,
    "meta-llama/Llama-2-13b": 4096,
    "meta-llama/Llama-2-70b": 4096,
    "mistralai/Mistral-7B-v0.1": 8192,
    "mistralai/Mixtral-8x7B-v0.1": 32768,
    "tiiuae/falcon-7b": 2048,
    "tiiuae/falcon-40b": 2048,
}


class HuggingFaceHubLLM(LLM):
    """
    HuggingFace Hub LLM implementation using the HuggingFace Inference API.

    Attributes:
        api_key (Optional[str]): The HuggingFace API key. Defaults to HF_API_KEY env var.
        model_name (Optional[str]): The model name on HuggingFace Hub.
        endpoint_url (Optional[str]): Custom endpoint URL for the model.
        temperature (Optional[float]): Sampling temperature.
        max_new_tokens (Optional[int]): Maximum number of tokens to generate.
        top_p (Optional[float]): Top-p sampling parameter.
        top_k (Optional[int]): Top-k sampling parameter.
        repetition_penalty (Optional[float]): Repetition penalty.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("HF_API_KEY"))
    endpoint_url: Optional[str] = Field(default_factory=lambda: get_from_env("HF_ENDPOINT_URL"))
    max_new_tokens: Optional[int] = Field(default=512)
    top_p: Optional[float] = Field(default=0.95)
    top_k: Optional[int] = Field(default=50)
    repetition_penalty: Optional[float] = Field(default=1.0)
    do_sample: Optional[bool] = Field(default=True)

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Call the HuggingFace Hub LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Union[LLMOutput, Iterator[LLMOutput]]: The LLM output.
        """
        try:
            from huggingface_hub import InferenceClient
        except ImportError:
            raise ImportError(
                "huggingface_hub is not installed. "
                "Please install it with `pip install huggingface_hub`"
            )

        client = InferenceClient(
            token=self.api_key,
            model=self.endpoint_url or self.model_name,
            timeout=self.request_timeout or 120,
        )

        # Convert messages to prompt format
        prompt = self._messages_to_prompt(messages)

        params = {
            "max_new_tokens": kwargs.pop("max_new_tokens", self.max_new_tokens),
            "temperature": kwargs.pop("temperature", self.temperature),
            "top_p": kwargs.pop("top_p", self.top_p),
            "top_k": kwargs.pop("top_k", self.top_k),
            "repetition_penalty": kwargs.pop("repetition_penalty", self.repetition_penalty),
            "do_sample": kwargs.pop("do_sample", self.do_sample),
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = client.text_generation(
            prompt,
            **params,
            **kwargs
        )

        return LLMOutput(text=response, raw={"model": self.model_name, "response": response})

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Async call the HuggingFace Hub LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Union[LLMOutput, AsyncIterator[LLMOutput]]: The LLM output.
        """
        # HuggingFace Inference API doesn't have native async support in the client
        # We run it in an executor
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._call(messages, **kwargs))

    def _messages_to_prompt(self, messages: list) -> str:
        """Convert messages to a single prompt string.

        Args:
            messages (list): List of message dicts with 'role' and 'content'.

        Returns:
            str: Combined prompt string.
        """
        prompt_parts = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            else:
                prompt_parts.append(f"{role.capitalize()}: {content}")

        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)

    def max_context_length(self) -> int:
        """Return the maximum context length for the model."""
        if super().max_context_length():
            return super().max_context_length()
        return HUGGINGFACE_MAX_CONTEXT_LENGTH.get(self.model_name, 2048)

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens in the text.

        Args:
            text (str): The text to tokenize.

        Returns:
            int: The number of tokens.
        """
        try:
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            return len(tokenizer.encode(text))
        except Exception:
            # Fallback to simple estimation
            return len(text.split()) * 2

    def as_langchain(self):
        """Convert to a LangChain compatible LLM."""
        try:
            from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
        except ImportError:
            raise ImportError(
                "langchain_community is not installed. "
                "Please install it with `pip install langchain-community`"
            )

        return HuggingFaceEndpoint(
            endpoint_url=self.endpoint_url or f"https://api-inference.huggingface.co/models/{self.model_name}",
            huggingfacehub_api_token=self.api_key,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            repetition_penalty=self.repetition_penalty,
        )
