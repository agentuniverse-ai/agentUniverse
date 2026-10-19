# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : agentuniverse
# @FileName: groq_llm.py

"""
Groq Cloud LLM.

Groq (https://groq.com) is an inference engine built on top of its custom
LPU (Language Processing Unit) hardware that delivers extremely fast
token generation for a curated set of open-source large language models
such as Meta's Llama family, Google's Gemma, and Mistral's Mixtral.

Groq exposes an OpenAI-compatible Chat Completions API at
``https://api.groq.com/openai/v1``. Because of that compatibility this
component simply extends :class:`OpenAIStyleLLM` and only needs to wire up
the correct default environment variables, the Groq API base URL and the
per-model maximum context length table.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.annotation.trace import trace_llm
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by the
# models currently available on the Groq Cloud API. The values are sourced
# from the official Groq documentation (https://console.groq.com/docs/models).
# When Groq ships a new model it is sufficient to add an entry here, the rest
# of the component keeps working unchanged.
GROQ_MAX_CONTEXT_LENGTH = {
    # ---- Meta Llama family ----
    "llama-3.3-70b-versatile": 131072,
    "llama-3.3-70b-instruct": 131072,
    "llama3-groq-70b-8192-tool-use-preview": 8192,
    "llama3-groq-70b-tool-use-preview": 8192,
    "llama-3.1-8b-instant": 131072,
    "llama-3.1-70b-versatile": 131072,
    "llama-3.1-8b-versatile": 131072,
    "llama3-70b-8192": 8192,
    "llama3-8b-8192": 8192,
    # ---- Google Gemma family ----
    "gemma2-9b-it": 8192,
    "gemma-7b-it": 8192,
    # ---- Mistral family ----
    "mixtral-8x7b-32768": 32768,
    # ---- OpenAI whisper (audio) ----
    "whisper-large-v3": 8000,
    "whisper-large-v3-turbo": 8000,
    "distil-whisper-large-v3-en": 8000,
}

# Sensible default context length returned for models that are not yet listed
# in the table above. Groq models very commonly expose an 8k window, so 8192
# is a safe conservative fallback.
GROQ_DEFAULT_CONTEXT_LENGTH = 8192


class GroqLLM(OpenAIStyleLLM):
    """Groq Cloud LLM, an OpenAI-compatible wrapper around the Groq inference API.

    Groq runs popular open-weight models (Llama 3.x, Mixtral, Gemma 2, ...)
    on its dedicated LPU hardware which produces near-instant token
    generation. The Groq API is fully OpenAI-compatible, therefore this
    class only customises the credential/base-url plumbing and the model
    context-length lookup table while inheriting the complete request,
    streaming and langchain-bridge implementation from
    :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Groq API key. Loaded from the ``GROQ_API_KEY`` environment
            variable when not provided explicitly. Create one at
            https://console.groq.com/keys.
        api_base: Groq OpenAI-compatible API base URL. Defaults to
            ``https://api.groq.com/openai/v1`` unless overridden through the
            ``GROQ_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
        organization: Optional organization id forwarded to the client.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("GROQ_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("GROQ_API_BASE") or
                                    "https://api.groq.com/openai/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("GROQ_PROXY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("GROQ_ORGANIZATION"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the Groq chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the Groq API
        base URL.

        Args:
            messages (list): The chat messages to send to Groq.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the Groq chat completions endpoint.

        Args:
            messages (list): The chat messages to send to Groq.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Groq model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name is looked up in
           :data:`GROQ_MAX_CONTEXT_LENGTH`.
        3. As a last resort :data:`GROQ_DEFAULT_CONTEXT_LENGTH` is returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        return GROQ_MAX_CONTEXT_LENGTH.get(self.model_name, GROQ_DEFAULT_CONTEXT_LENGTH)

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Groq serves a heterogeneous set of models, each with its own
        tokenizer. Because all of them are open-weight models whose
        tokenizers are not always registered in ``tiktoken`` by name, we
        fall back to the widely used ``cl100k_base`` encoding which gives a
        good approximation suitable for budget/prompt-window checks.

        Args:
            text: The raw string to tokenize.

        Returns:
            The integer number of tokens the text would be encoded into.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # Most Groq models (llama-3, mixtral, gemma) are not registered
            # in tiktoken by name; cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
