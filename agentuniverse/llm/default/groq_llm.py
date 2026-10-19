# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 10:00
# @Author  : agentuniverse
# @FileName: groq_llm.py

"""
Groq Cloud LLM.

Groq (https://groq.com) runs a cloud inference service built on its custom
LPU (Language Processing Unit) hardware, delivering near-instant token
generation - typically several hundreds of tokens per second - for a curated
set of open-weight large language models such as Meta's Llama family, the
OpenAI gpt-oss family, Google's Gemma and Mistral's Mixtral.

Groq exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.groq.com/openai/v1``. Because of that compatibility this
component simply extends :class:`OpenAIStyleLLM` and only needs to wire up
the correct default environment variables, the Groq API base URL and the
per-model maximum context-length table. Streaming, tool calling, the async
interface and the Langchain bridge are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by the models
# currently available on the Groq Cloud API. The values are sourced from the
# official Groq models documentation
# (https://console.groq.com/docs/models). When Groq ships a new model it is
# sufficient to add an entry here, the rest of the component keeps working
# unchanged.
GROQ_MAX_CONTEXT_LENGTH = {
    # ---- Meta Llama family ----
    "llama-3.3-70b-versatile": 131072,
    "llama-3.1-8b-instant": 131072,
    "llama-3.1-70b-versatile": 131072,
    "llama-3.1-8b-versatile": 131072,
    # ---- OpenAI open-weight models ----
    "openai/gpt-oss-120b": 131072,
    "openai/gpt-oss-20b": 131072,
    "openai/gpt-oss-safeguard-20b": 131072,
    # ---- Qwen family ----
    "qwen/qwen3.8-27b": 131072,
    # ---- Other preview partners ----
    "minimaxai/minimax-m2.7": 196608,
    "meta-models/muse-spark-open": 131072,
    # ---- Legacy models (deprecated on Groq, kept for backward compatibility) ----
    "mixtral-8x7b-32768": 32768,
    "gemma2-9b-it": 8192,
    "gemma-7b-it": 8192,
}

# Sensible default context length returned for models that are not yet listed
# in the table above. A conservative 8k window keeps prompt-budget checks on
# the safe side for freshly announced Groq models.
GROQ_DEFAULT_CONTEXT_LENGTH = 8192


class GroqLLM(OpenAIStyleLLM):
    """Groq Cloud LLM, an OpenAI-compatible wrapper around the Groq inference API.

    Groq runs popular open-weight models (Llama 3.x, gpt-oss, Qwen, Gemma,
    Mixtral, ...) on its LPU hardware which produces some of the fastest
    token generation available in the market. The Groq API is fully
    OpenAI-compatible, therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Groq API key. Loaded from the ``GROQ_API_KEY`` environment
            variable when not provided explicitly. Create one at
            https://console.groq.com/keys.
        api_base: Groq OpenAI-compatible API base URL. Defaults to
            ``https://api.groq.com/openai/v1`` unless overridden through the
            ``GROQ_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("GROQ_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("GROQ_API_BASE") or
                                    "https://api.groq.com/openai/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("GROQ_PROXY"))

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

        Groq serves a heterogeneous set of open-weight models, each with its
        own tokenizer. Because those tokenizers are not always registered
        in ``tiktoken`` by name, we fall back to the widely used
        ``cl100k_base`` encoding which gives a good approximation suitable
        for budget/prompt-window checks.

        Args:
            text: The raw string to tokenize.

        Returns:
            The integer number of tokens the text would be encoded into.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # Most Groq models (llama, gpt-oss, qwen, gemma, mixtral) are not
            # registered in tiktoken by name; cl100k_base is a robust generic
            # fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
