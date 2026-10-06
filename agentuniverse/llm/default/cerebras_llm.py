# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/6 10:00
# @Author  : agentuniverse
# @FileName: cerebras_llm.py

"""
Cerebras Inference LLM.

Cerebras (https://www.cerebras.ai) builds the **Wafer-Scale Engine (WSE)**,
the largest chip ever made, and runs a cloud inference service on top of it.
Because the whole model fits on a single wafer, Cerebras delivers
industry-leading token generation speeds - typically hundreds to thousands of
tokens per second - for a curated set of open-weight large language models
such as Meta's Llama family, Qwen and open-source reasoning models.

Cerebras exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.cerebras.ai/v1``. Because of that compatibility this component
simply extends :class:`OpenAIStyleLLM` and only needs to wire up the correct
default environment variables, the Cerebras API base URL and the per-model
maximum context-length table. Streaming, tool calling, the async interface
and the Langchain bridge are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by the models
# currently available on the Cerebras Inference API. The values are sourced
# from the official Cerebras model documentation
# (https://inference-docs.cerebras.ai/models/overview). When Cerebras ships a
# new model it is sufficient to add an entry here, the rest of the component
# keeps working unchanged.
CEREBRAS_MAX_CONTEXT_LENGTH = {
    # ---- Meta Llama family ----
    "llama-3.3-70b": 131072,
    "llama3.1-8b": 131072,
    "llama4-scout-17b-16e-instruct": 131072,
    # ---- Qwen family ----
    "qwen-3-32b": 131072,
    "qwen-3-235b-a22b-instruct-2507": 131072,
    # ---- OpenAI open-weight models ----
    "gpt-oss-120b": 131072,
}

# Sensible default context length returned for models that are not yet listed
# in the table above. A conservative 8k window keeps prompt-budget checks on
# the safe side for freshly announced Cerebras models.
CEREBRAS_DEFAULT_CONTEXT_LENGTH = 8192


class CerebrasLLM(OpenAIStyleLLM):
    """Cerebras Inference LLM, an OpenAI-compatible wrapper around the Cerebras API.

    Cerebras runs popular open-weight models (Llama 3.x, Llama 4 Scout,
    Qwen 3, gpt-oss, ...) on its Wafer-Scale Engine hardware which produces
    the fastest token generation available in the market. The Cerebras API is
    fully OpenAI-compatible, therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Cerebras API key. Loaded from the ``CEREBRAS_API_KEY``
            environment variable when not provided explicitly. Create one at
            https://cloud.cerebras.ai.
        api_base: Cerebras OpenAI-compatible API base URL. Defaults to
            ``https://api.cerebras.ai/v1`` unless overridden through the
            ``CEREBRAS_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("CEREBRAS_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("CEREBRAS_API_BASE") or
                                    "https://api.cerebras.ai/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("CEREBRAS_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the Cerebras chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the Cerebras API
        base URL.

        Args:
            messages (list): The chat messages to send to Cerebras.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the Cerebras chat completions endpoint.

        Args:
            messages (list): The chat messages to send to Cerebras.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Cerebras model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name is looked up in
           :data:`CEREBRAS_MAX_CONTEXT_LENGTH`.
        3. As a last resort :data:`CEREBRAS_DEFAULT_CONTEXT_LENGTH` is
           returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        return CEREBRAS_MAX_CONTEXT_LENGTH.get(self.model_name, CEREBRAS_DEFAULT_CONTEXT_LENGTH)

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Cerebras serves a heterogeneous set of open-weight models, each with
        its own tokenizer. Because those tokenizers are not always registered
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
            # Most Cerebras models (llama, qwen, gpt-oss) are not registered
            # in tiktoken by name; cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
