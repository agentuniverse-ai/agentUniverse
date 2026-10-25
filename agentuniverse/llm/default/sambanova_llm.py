# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: sambanova_llm.py

"""
SambaNova Cloud LLM.

SambaNova Cloud (https://cloud.sambanova.ai) is the model-serving platform of
SambaNova Systems, running open-weight flagship models on the purpose-built
SambaNova RDU hardware instead of GPUs. The catalogue spans the Meta Llama
family (Meta-Llama-3.3-70B-Instruct, Meta-Llama-3.1-405B-Instruct, ...),
Alibaba's Qwen3-32B and the DeepSeek-R1 reasoning model, delivering some of
the fastest tokens-per-second rates available for open models.

SambaNova exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.sambanova.ai/v1``. Because of that compatibility this component
simply extends :class:`OpenAIStyleLLM` and only needs to wire up the correct
default environment variables, the SambaNova API base URL and the per-model
maximum context-length table. Streaming, tool calling, the async interface
and the Langchain bridge are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) of the models commonly
# available on SambaNova Cloud. The values below follow the official
# SambaNova documentation: 128k (131072) for the large Llama 3.1/3.3 and
# DeepSeek-R1 deployments, the Llama 3.1 8B model served with its compact 16k
# (16384) window, and the Qwen3-32B deployment with a 32k (32768) window.
# The table is *indicative*: SambaNova continuously adds and rotates models,
# so when a new model ships it is sufficient to add an entry here, the rest
# of the component keeps working unchanged.
SAMBANOVA_MAX_CONTEXT_LENGTH = {
    # ---- Meta Llama family ----
    "Meta-Llama-3.3-70B-Instruct": 131072,
    "Meta-Llama-3.1-405B-Instruct": 131072,
    "Meta-Llama-3.1-70B-Instruct": 131072,
    "Meta-Llama-3.1-8B-Instruct": 16384,
    # ---- Reasoning models ----
    "DeepSeek-R1": 131072,
    # ---- Qwen family ----
    "Qwen3-32B": 32768,
}

# Sensible default context length returned for models that are not yet listed
# in the table above. A conservative 8k window keeps prompt-budget checks on
# the safe side for freshly announced models and for deployments whose window
# differs from the upstream model card.
SAMBANOVA_DEFAULT_CONTEXT_LENGTH = 8192


class SambaNovaLLM(OpenAIStyleLLM):
    """SambaNova Cloud LLM, an OpenAI-compatible wrapper around the SambaNova API.

    SambaNova Cloud serves open-weight models (Meta Llama, DeepSeek-R1,
    Qwen3 and others) on RDU accelerators through an API that is fully
    OpenAI-compatible. Therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: SambaNova Cloud API key. Loaded from the
            ``SAMBANOVA_API_KEY`` environment variable when not provided
            explicitly. Create one in the SambaNova Cloud dashboard at
            https://cloud.sambanova.ai.
        api_base: SambaNova OpenAI-compatible API base URL. Defaults to
            ``https://api.sambanova.ai/v1`` unless overridden through the
            ``SAMBANOVA_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SAMBANOVA_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("SAMBANOVA_API_BASE") or
                                    "https://api.sambanova.ai/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("SAMBANOVA_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the SambaNova chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the SambaNova
        API base URL.

        Args:
            messages (list): The chat messages to send to SambaNova.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the SambaNova chat completions endpoint.

        Args:
            messages (list): The chat messages to send to SambaNova.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'SambaNovaLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``sambanova_llm.yaml.example`` with a missing ``SAMBANOVA_API_KEY`` /
        ``SAMBANOVA_PROXY`` would otherwise assign ``''`` over the class
        defaults. That is worse than it sounds: the OpenAI client only
        rejects a *missing* key, so an empty key is silently sent upstream
        and surfaces as an opaque 401, and an empty ``api_base`` makes the
        client fall back to ``https://api.openai.com/v1`` — sending
        SambaNova credentials to the wrong endpoint. Normalizing the empty
        values here makes an unset variable behave exactly like an omitted
        key: ``api_key`` / ``proxy`` fall back to ``None`` and ``api_base``
        to the SambaNova endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            SambaNovaLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("SAMBANOVA_API_BASE") or \
                "https://api.sambanova.ai/v1"
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
        2. Otherwise the model name (SambaNova uses the exact model
           identifier, e.g. ``Meta-Llama-3.3-70B-Instruct``) is looked up in
           :data:`SAMBANOVA_MAX_CONTEXT_LENGTH`.
        3. As a last resort :data:`SAMBANOVA_DEFAULT_CONTEXT_LENGTH` is
           returned.

        Note that the OpenAI-style parent implements its own fallback that
        consults the OpenAI model table with a 4096 default. It is
        deliberately bypassed here: SambaNova serves open models whose
        identifiers never appear in the OpenAI table, so the last two steps
        above provide the authoritative values for this endpoint.
        """
        if self._max_context_length:
            return self._max_context_length
        if self.model_name in SAMBANOVA_MAX_CONTEXT_LENGTH:
            return SAMBANOVA_MAX_CONTEXT_LENGTH[self.model_name]
        return SAMBANOVA_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        The open models served by SambaNova use their own tokenizers (Llama 3,
        DeepSeek, Qwen3 ...), none of which are registered in ``tiktoken`` by
        the identifiers used by the API, so we fall back to the widely used
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
            # The SambaNova model identifiers are not registered in tiktoken;
            # cl100k_base is a robust generic fallback for the open models
            # served on SambaNova.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
