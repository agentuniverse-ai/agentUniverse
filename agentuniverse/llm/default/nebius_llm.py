# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: nebius_llm.py

"""
Nebius AI Studio LLM.

Nebius AI Studio (https://nebius.com/ai-studio) is the inference platform of
Nebius Group and serves a broad catalogue of **open-weight** flagship models
from many vendors under a single subscription-free, pay-as-you-go API: Meta
Llama (meta-llama/Meta-Llama-3.1-405B-Instruct), DeepSeek
(deepseek-ai/DeepSeek-V3), Qwen (Qwen/Qwen2.5-32B-Instruct, Qwen/QwQ-32B)
and Mistral (mistralai/Mistral-Nemo-Instruct-2407) among others.

AI Studio exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.studio.nebius.com/v1``. Because of that compatibility this
component simply extends :class:`OpenAIStyleLLM` and only needs to wire up
the correct default environment variables, the Nebius API base URL and the
per-model maximum context-length table. Streaming, tool calling, the async
interface and the Langchain bridge are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) of the open models most
# commonly served through Nebius AI Studio. Nebius keeps the native context
# window of the underlying open-weight models, so the values below follow the
# official model cards: 128k (131072) for the Llama 3.1/3.3, Qwen2.5 and
# QwQ families, 64k (65536) for Mixtral-8x22B and 8k (8192) for Gemma 2.
# The table is *indicative*: Nebius continuously adds and rotates models, so
# when a new model ships it is sufficient to add an entry here, the rest of
# the component keeps working unchanged.
NEBIUS_MAX_CONTEXT_LENGTH = {
    # ---- Meta Llama family ----
    "meta-llama/Meta-Llama-3.1-405B-Instruct": 131072,
    "meta-llama/Meta-Llama-3.1-70B-Instruct": 131072,
    "meta-llama/Meta-Llama-3.1-8B-Instruct": 131072,
    "meta-llama/Llama-3.3-70B-Instruct": 131072,
    "meta-llama/Llama-3.2-3B-Instruct": 131072,
    # ---- DeepSeek family ----
    "deepseek-ai/DeepSeek-V3": 131072,
    "deepseek-ai/DeepSeek-V3-0324": 131072,
    "deepseek-ai/DeepSeek-R1": 131072,
    # ---- Qwen family ----
    "Qwen/Qwen2.5-32B-Instruct": 131072,
    "Qwen/Qwen2.5-Coder-32B-Instruct": 131072,
    "Qwen/QwQ-32B": 131072,
    # ---- Mistral family ----
    "mistralai/Mistral-Nemo-Instruct-2407": 131072,
    "mistralai/Mixtral-8x22B-Instruct-v0.1": 65536,
    # ---- Others ----
    "microsoft/Phi-3.5-MoE-Instruct": 131072,
    "google/gemma-2-27b-it": 8192,
}

# Sensible default context length returned for models that are not yet listed
# in the table above. A conservative 8k window keeps prompt-budget checks on
# the safe side for freshly announced models and for the smaller open models
# whose windows vary between deployments.
NEBIUS_DEFAULT_CONTEXT_LENGTH = 8192


class NebiusLLM(OpenAIStyleLLM):
    """Nebius AI Studio LLM, an OpenAI-compatible wrapper around the AI Studio API.

    Nebius AI Studio serves a large catalogue of open-weight models (Meta
    Llama, DeepSeek, Qwen, Mistral and others) through an API that is fully
    OpenAI-compatible. Therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Nebius AI Studio API key. Loaded from the ``NEBIUS_API_KEY``
            environment variable when not provided explicitly. Create one in
            the Nebius AI Studio console at https://studio.nebius.ai.
        api_base: Nebius OpenAI-compatible API base URL. Defaults to
            ``https://api.studio.nebius.com/v1`` unless overridden through
            the ``NEBIUS_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("NEBIUS_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("NEBIUS_API_BASE") or
                                    "https://api.studio.nebius.com/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("NEBIUS_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the Nebius AI Studio chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the Nebius API
        base URL.

        Args:
            messages (list): The chat messages to send to Nebius AI Studio.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the Nebius AI Studio chat completions endpoint.

        Args:
            messages (list): The chat messages to send to Nebius AI Studio.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'NebiusLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``nebius_llm.yaml.example`` with a missing ``NEBIUS_API_KEY`` /
        ``NEBIUS_PROXY`` would otherwise assign ``''`` over the class
        defaults. That is worse than it sounds: the OpenAI client only
        rejects a *missing* key, so an empty key is silently sent upstream
        and surfaces as an opaque 401, and an empty ``api_base`` makes the
        client fall back to ``https://api.openai.com/v1`` — sending Nebius
        credentials to the wrong endpoint. Normalizing the empty values here
        makes an unset variable behave exactly like an omitted key:
        ``api_key`` / ``proxy`` fall back to ``None`` and ``api_base`` to
        the Nebius AI Studio endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            NebiusLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("NEBIUS_API_BASE") or \
                "https://api.studio.nebius.com/v1"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field, stored in the
           inherited ``_max_context_length`` attribute) that value wins.
        2. Otherwise the model name (Nebius uses the full
           ``organization/model`` identifier, e.g.
           ``meta-llama/Meta-Llama-3.1-70B-Instruct``) is looked up in
           :data:`NEBIUS_MAX_CONTEXT_LENGTH`.
        3. As a last resort :data:`NEBIUS_DEFAULT_CONTEXT_LENGTH` is
           returned.

        Note that the OpenAI-style parent implements its own fallback that
        consults the OpenAI model table with a 4096 default. It is
        deliberately bypassed here: Nebius AI Studio serves open models
        whose identifiers never appear in the OpenAI table, so the last two
        steps above provide the authoritative values for this endpoint.
        """
        if self._max_context_length:
            return self._max_context_length
        if self.model_name in NEBIUS_MAX_CONTEXT_LENGTH:
            return NEBIUS_MAX_CONTEXT_LENGTH[self.model_name]
        return NEBIUS_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        The open models served by Nebius AI Studio use their own tokenizers
        (Llama 3, DeepSeek, Qwen2.5, Mixtral ...), none of which are
        registered in ``tiktoken`` by the ``organization/model`` names used
        by the API, so we fall back to the widely used ``cl100k_base``
        encoding which gives a good approximation suitable for
        budget/prompt-window checks.

        Args:
            text: The raw string to tokenize.

        Returns:
            The integer number of tokens the text would be encoded into.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # The organization/model names are not registered in tiktoken;
            # cl100k_base is a robust generic fallback for the open models
            # served on Nebius AI Studio.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
