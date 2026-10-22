# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/6 10:00
# @Author  : agentuniverse
# @FileName: reka_llm.py

"""
Reka AI LLM.

Reka AI (https://www.reka.ai) is a multimodal large language model company.
Its model family - **Reka Core** (flagship), **Reka Flash** (fast, balanced)
and **Reka Edge** (compact) - natively understands text, images and video,
which makes it a good fit for agents that reason over mixed-media inputs.

Reka exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.reka.ai/v1``. Because of that compatibility this component
simply extends :class:`OpenAIStyleLLM` and only needs to wire up the correct
default environment variables, the Reka API base URL and the per-model
maximum context-length table. Streaming, tool calling, the async interface
and the Langchain bridge are inherited unchanged.

A minimal usage example::

    from agentuniverse.llm.default.reka_llm import RekaLLM

    llm = RekaLLM(model_name='reka-flash')
    output = llm.call(messages=[{'role': 'user', 'content': 'Hello!'}])
    print(output.text)
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by the models
# currently available on the Reka API. The values are sourced from the
# official Reka documentation (https://docs.reka.ai). When Reka ships a new
# model it is sufficient to add an entry here, the rest of the component
# keeps working unchanged.
REKA_MAX_CONTEXT_LENGTH = {
    # ---- Reka Core: flagship multimodal model ----
    "reka-core": 65536,
    # ---- Reka Flash: fast, balanced multimodal model ----
    "reka-flash": 131072,
    # ---- Reka Edge: compact multimodal model ----
    "reka-edge": 131072,
}

# Sensible default context length returned for models that are not yet listed
# in the table above. A conservative 8k window keeps prompt-budget checks on
# the safe side for freshly announced Reka models.
REKA_DEFAULT_CONTEXT_LENGTH = 8192


class RekaLLM(OpenAIStyleLLM):
    """Reka AI LLM, an OpenAI-compatible wrapper around the Reka API.

    Reka serves its multimodal model family (Core, Flash, Edge) through an
    OpenAI-compatible endpoint, therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Reka API key. Loaded from the ``REKA_API_KEY`` environment
            variable when not provided explicitly. Create one at
            https://platform.reka.ai.
        api_base: Reka OpenAI-compatible API base URL. Defaults to
            ``https://api.reka.ai/v1`` unless overridden through the
            ``REKA_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.

    Example:
        >>> llm = RekaLLM(model_name='reka-flash', api_key='reka-***')
        >>> llm.max_context_length()
        131072
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("REKA_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("REKA_API_BASE") or
                                    "https://api.reka.ai/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("REKA_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the Reka chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the Reka API
        base URL.

        Args:
            messages (list): The chat messages to send to Reka.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the Reka chat completions endpoint.

        Args:
            messages (list): The chat messages to send to Reka.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Reka model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name is looked up in
           :data:`REKA_MAX_CONTEXT_LENGTH`.
        3. As a last resort :data:`REKA_DEFAULT_CONTEXT_LENGTH` is returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        return REKA_MAX_CONTEXT_LENGTH.get(self.model_name, REKA_DEFAULT_CONTEXT_LENGTH)

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Reka models are not registered in ``tiktoken`` by name, so we fall
        back to the widely used ``cl100k_base`` encoding which gives a good
        approximation suitable for budget/prompt-window checks.

        Args:
            text: The raw string to tokenize.

        Returns:
            The integer number of tokens the text would be encoded into.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # Reka models (core / flash / edge) are not registered in
            # tiktoken by name; cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
