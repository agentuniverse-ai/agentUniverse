# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 15:00
# @Author  : agentuniverse
# @FileName: deepinfra_llm.py

"""
DeepInfra LLM.

DeepInfra (https://deepinfra.com) is a serverless inference platform that
hosts a large catalog of open-weight large language models — Llama, Qwen,
DeepSeek, Mistral, Gemma and many more — behind a single billable API.
Instead of tying users to one proprietary vendor it offers hosted versions
of community models with per-token pricing, so an agent can switch between
e.g. ``meta-llama/Meta-Llama-3.1-405B-Instruct`` and
``deepseek-ai/DeepSeek-V3`` by changing a single config line.

DeepInfra exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.deepinfra.com/v1/openai``. Because of that compatibility this
component simply extends :class:`OpenAIStyleLLM` and only needs to wire up
the correct default environment variables, the DeepInfra API base URL and an
indicative per-model maximum context-length table. Streaming, tool calling,
the async interface and the Langchain bridge are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# Indicative context length (input + output tokens) for a selection of the
# most popular models currently served by DeepInfra, expressed in tokens
# (128k = 131072, 64k = 65536, 32k = 32768). DeepInfra is a hosting
# platform for third-party open-weight models: the catalog rotates
# frequently and the effective window of a served checkpoint is decided by
# the model publisher, so these values are *indicative* defaults for
# prompt-budget checks rather than a contractual guarantee — always confirm
# on https://deepinfra.com/models. When DeepInfra adds a model it is
# sufficient to add an entry here, the rest of the component keeps working
# unchanged.
DEEPINFRA_MAX_CONTEXT_LENGTH = {
    # ---- Meta Llama 3.1 family ----
    "meta-llama/Meta-Llama-3.1-405B-Instruct": 131072,
    "meta-llama/Meta-Llama-3.1-70B-Instruct": 131072,
    "meta-llama/Meta-Llama-3.1-8B-Instruct": 131072,
    # ---- Qwen family ----
    "Qwen/Qwen2.5-72B-Instruct": 32768,
    # ---- DeepSeek family ----
    "deepseek-ai/DeepSeek-V3": 65536,
}

# Sensible default context length returned for models that are not yet
# listed in the table above. Because DeepInfra hosts a long tail of models
# of very different vintages, a conservative 8k window keeps prompt-budget
# checks on the safe side for freshly added or unlisted checkpoints.
DEEPINFRA_DEFAULT_CONTEXT_LENGTH = 8192


class DeepInfraLLM(OpenAIStyleLLM):
    """DeepInfra LLM, an OpenAI-compatible wrapper around the DeepInfra API.

    DeepInfra serves a large catalog of open-weight models (Llama, Qwen,
    DeepSeek, ...) through an API that is fully OpenAI-compatible.
    Therefore this class only customises the credential/base-url plumbing
    and the model context-length lookup table while inheriting the complete
    request, streaming and langchain-bridge implementation from
    :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: DeepInfra API key. Loaded from the ``DEEPINFRA_API_KEY``
            environment variable when not provided explicitly. Create one
            at https://deepinfra.com/dashboard/settings.
        api_base: DeepInfra OpenAI-compatible API base URL. Defaults to
            ``https://api.deepinfra.com/v1/openai`` unless overridden
            through the ``DEEPINFRA_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("DEEPINFRA_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("DEEPINFRA_API_BASE") or
                                    "https://api.deepinfra.com/v1/openai")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("DEEPINFRA_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the DeepInfra chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the DeepInfra
        API base URL.

        Args:
            messages (list): The chat messages to send to DeepInfra.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the DeepInfra chat completions endpoint.

        Args:
            messages (list): The chat messages to send to DeepInfra.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'DeepInfraLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``deepinfra_llm.yaml.example`` with a missing ``DEEPINFRA_API_KEY``
        / ``DEEPINFRA_PROXY`` would otherwise assign ``''`` over the class
        defaults. That is worse than it sounds: the OpenAI client only
        rejects a *missing* key, so an empty key is silently sent upstream
        and surfaces as an opaque 401, and an empty ``api_base`` makes the
        client fall back to ``https://api.openai.com/v1`` — sending
        DeepInfra credentials to the wrong endpoint. Normalizing the empty
        values here makes an unset variable behave exactly like an omitted
        key: ``api_key`` / ``proxy`` fall back to ``None`` and ``api_base``
        to the DeepInfra endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            DeepInfraLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("DEEPINFRA_API_BASE") or \
                "https://api.deepinfra.com/v1/openai"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured model.

        The combined length of the input prompt and the generated
        completion must fit within this window. The value is resolved in
        the following order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name (DeepInfra uses ``org/model``
           identifiers, e.g. ``Qwen/Qwen2.5-72B-Instruct``) is looked up
           in :data:`DEEPINFRA_MAX_CONTEXT_LENGTH`. The values there are
           indicative, sourced from each model publisher's documentation.
        3. As a last resort :data:`DEEPINFRA_DEFAULT_CONTEXT_LENGTH` is
           returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        if self.model_name in DEEPINFRA_MAX_CONTEXT_LENGTH:
            return DEEPINFRA_MAX_CONTEXT_LENGTH[self.model_name]
        return DEEPINFRA_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        DeepInfra serves many different open-weight models, each with its
        own tokenizer, and most are not registered in ``tiktoken`` by the
        ``org/model`` identifier, so we fall back to the widely used
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
            # org/model identifiers are not registered in tiktoken;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
