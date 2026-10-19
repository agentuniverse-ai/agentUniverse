# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: sensenova_llm.py

"""
SenseNova (SenseTime) LLM.

SenseNova (https://platform.sensenova.cn) is SenseTime's large model
platform behind the **SenseChat** family of large language models. It
covers the full spectrum from the flagship **SenseChat-5** dialogue
model over the low-latency **SenseChat-Turbo** variant to the
multimodal-capable **SenseNova-V6-Pro** generation.

SenseNova exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.sensenova.cn/compatible-mode/v1``. Because of that
compatibility this component simply extends :class:`OpenAIStyleLLM` and
only needs to wire up the correct default environment variables, the
SenseNova API base URL and the per-model maximum context-length table.
Streaming, tool calling, the async interface and the Langchain bridge
are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by the
# SenseChat models currently available on the SenseNova OpenAI-compatible
# endpoint. The values are indicative, follow the binary convention used
# by SenseNova's model cards (128k = 131072, 32k = 32768) and should be
# re-checked against the official SenseNova documentation
# (https://platform.sensenova.cn) when SenseTime ships new models. When a
# new model is released it is sufficient to add an entry here, the rest
# of the component keeps working unchanged.
SENSENOVA_MAX_CONTEXT_LENGTH = {
    # ---- Flagship dialogue models ----
    "SenseChat-5": 131072,
    # ---- Fast / low-latency variant ----
    "SenseChat-Turbo": 32768,
    # ---- V6 generation flagship ----
    "SenseNova-V6-Pro": 131072,
}

# Sensible default context length returned for models that are not yet
# listed in the table above. A conservative 8k window keeps
# prompt-budget checks on the safe side for freshly announced SenseChat
# releases and dated or aliased releases whose base entry cannot be
# resolved.
SENSENOVA_DEFAULT_CONTEXT_LENGTH = 8192


class SenseNovaLLM(OpenAIStyleLLM):
    """SenseNova SenseChat LLM, an OpenAI-compatible wrapper around the
    SenseTime SenseNova API.

    SenseTime serves its SenseChat family of models (SenseChat-5, the
    SenseChat-Turbo fast variant and the SenseNova-V6-Pro generation)
    through an endpoint that is fully OpenAI-compatible. Therefore this
    class only customises the credential/base-url plumbing and the model
    context-length lookup table while inheriting the complete request,
    streaming and langchain-bridge implementation from
    :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: SenseNova API key. Loaded from the ``SENSENOVA_API_KEY``
            environment variable when not provided explicitly. Create one
            in the SenseNova / SenseCore console (https://console.sensecore.cn).
        api_base: SenseNova OpenAI-compatible API base URL. Defaults to
            ``https://api.sensenova.cn/compatible-mode/v1`` unless
            overridden through the ``SENSENOVA_API_BASE`` environment
            variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SENSENOVA_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("SENSENOVA_API_BASE") or
                                    "https://api.sensenova.cn/compatible-mode/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("SENSENOVA_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the SenseNova chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the SenseNova
        API base URL.

        Args:
            messages (list): The chat messages to send to SenseNova.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the SenseNova chat completions endpoint.

        Args:
            messages (list): The chat messages to send to SenseNova.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'SenseNovaLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``sensenova_llm.yaml.example`` with a missing ``SENSENOVA_API_KEY``
        / ``SENSENOVA_PROXY`` would otherwise assign ``''`` over the class
        defaults. That is worse than it sounds: the OpenAI client only
        rejects a *missing* key, so an empty key is silently sent upstream
        and surfaces as an opaque 401, and an empty ``api_base`` makes the
        client fall back to ``https://api.openai.com/v1`` — sending
        SenseNova credentials to the wrong endpoint. Normalizing the empty
        values here makes an unset variable behave exactly like an omitted
        key: ``api_key`` / ``proxy`` fall back to ``None`` and ``api_base``
        to the SenseNova endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            SenseNovaLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("SENSENOVA_API_BASE") or \
                "https://api.sensenova.cn/compatible-mode/v1"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured SenseChat model.

        The combined length of the input prompt and the generated
        completion must fit within this window. The value is resolved in
        the following order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name is looked up in
           :data:`SENSENOVA_MAX_CONTEXT_LENGTH`.
        3. As a last resort :data:`SENSENOVA_DEFAULT_CONTEXT_LENGTH` is
           returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        if self.model_name in SENSENOVA_MAX_CONTEXT_LENGTH:
            return SENSENOVA_MAX_CONTEXT_LENGTH[self.model_name]
        return SENSENOVA_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        SenseChat models use SenseTime's own tokenizer, which is not
        registered in ``tiktoken`` by model name, so we fall back to the
        widely used ``cl100k_base`` encoding which gives a good
        approximation suitable for budget/prompt-window checks.

        Args:
            text: The raw string to tokenize.

        Returns:
            The integer number of tokens the text would be encoded into.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # SenseChat models are not registered in tiktoken by name;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
