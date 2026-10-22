# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: gpustack_llm.py

"""
GPUStack LLM.

GPUStack (https://gpustack.ai) is an open-source GPU cluster manager for
running large language models. It aggregates the GPUs of a fleet of
machines — workstations, servers, Apple-silicon Macs — into a single
cluster, schedules model deployments onto the available devices and serves
every deployed model through the GPUStack server's gateway. That gateway
speaks a fully **OpenAI-compatible** Chat Completions dialect on
``http://localhost:80/v1`` by default, and the served model identifiers
are whatever the operator deployed into the cluster (``llama3.1-8b``,
``qwen2.5-72b``, ...) — there is no vendor model catalogue at all.

Because of that OpenAI compatibility this component simply extends
:class:`OpenAIStyleLLM` and only needs to wire up the correct default
environment variables and the GPUStack gateway endpoint. Streaming, tool
calling, the async interface and the Langchain bridge are inherited
unchanged. Two aspects are special about a self-hosted cluster gateway:

* **An API key is optional.** A GPUStack gateway can run without key
  authentication (e.g. an isolated lab cluster), and in that mode it
  accepts any bearer token. The OpenAI python client refuses to be
  constructed without a key, so the component defaults ``api_key`` to the
  harmless placeholder ``"gpustack"``; point ``GPUSTACK_API_KEY`` at a
  real API key created in the GPUStack UI whenever the gateway enforces
  authentication (the default for production deployments).
* **No context-length table is possible.** Deployed models are arbitrary
  operator choices under arbitrary names, so instead of a per-model
  lookup table the component falls back to a conservative 8192-token
  window and expects users to state the real limit through the
  ``max_context_length`` YAML field.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# Default URL of the GPUStack gateway's OpenAI-compatible API. GPUStack's
# documented default is to serve on port 80 of the GPUStack server; override
# it through the GPUSTACK_API_BASE environment variable when the gateway is
# bound to a different port, host or TLS terminator.
GPUSTACK_DEFAULT_API_BASE = "http://localhost:80/v1"

# Placeholder bearer token used when no real key is configured. A GPUStack
# gateway without key authentication accepts any string, but the OpenAI
# python client refuses to be constructed with api_key=None, so a harmless
# constant is shipped instead of None.
GPUSTACK_PLACEHOLDER_API_KEY = "gpustack"

# Conservative default context length returned when the YAML configuration
# does not state one. GPUStack serves arbitrary operator-deployed models
# under arbitrary names, so no per-model lookup table can be maintained; a
# small 8k default keeps prompt-budget checks on the safe side until the
# real limit is configured through the ``max_context_length`` YAML field.
GPUSTACK_DEFAULT_CONTEXT_LENGTH = 8192


class GPUStackLLM(OpenAIStyleLLM):
    """GPUStack LLM, an OpenAI-compatible wrapper around a GPUStack gateway.

    GPUStack schedules model deployments across the GPUs of a self-hosted
    cluster and exposes them through an OpenAI-compatible API on
    ``http://localhost:80/v1``. Therefore this class only customises the
    credential/base-url plumbing and the context-length fallback while
    inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Bearer token for the GPUStack gateway. **No key is
            required** when the gateway runs without authentication — it
            accepts any value, so the component defaults to the harmless
            ``"gpustack"`` placeholder (the OpenAI client refuses to be
            built without a key). Load a real API key from the
            ``GPUSTACK_API_KEY`` environment variable whenever the gateway
            enforces authentication (API keys are created in the GPUStack
            UI under "API Keys").
        api_base: GPUStack OpenAI-compatible gateway API base URL.
            Defaults to ``http://localhost:80/v1`` unless overridden
            through the ``GPUSTACK_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy for reaching a GPUStack gateway that
            is only accessible through a corporate proxy; can be set
            through ``GPUSTACK_PROXY``.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("GPUSTACK_API_KEY") or
                                    GPUSTACK_PLACEHOLDER_API_KEY)
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("GPUSTACK_API_BASE") or
                                    GPUSTACK_DEFAULT_API_BASE)
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("GPUSTACK_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the GPUStack chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the GPUStack
        gateway API base URL.

        Args:
            messages (list): The chat messages to send to the deployed model.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the GPUStack chat completions endpoint.

        Args:
            messages (list): The chat messages to send to the deployed model.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'GPUStackLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``gpustack_llm.yaml.example`` with a missing
        ``GPUSTACK_API_KEY`` / ``GPUSTACK_API_BASE`` / ``GPUSTACK_PROXY``
        would otherwise assign ``''`` over the class defaults. That is worse
        than it sounds: an empty ``api_base`` makes the OpenAI client fall
        back to ``https://api.openai.com/v1`` — sending GPUStack requests to
        the wrong endpoint — and an empty ``api_key`` would be silently sent
        upstream. Normalizing the empty values here makes an unset variable
        behave exactly like an omitted key: ``api_key`` falls back to the
        harmless GPUStack placeholder (or the ``GPUSTACK_API_KEY``
        environment value), ``api_base`` to the GPUStack gateway endpoint
        and ``proxy`` to ``None``.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            GPUStackLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = get_from_env("GPUSTACK_API_KEY") or \
                GPUSTACK_PLACEHOLDER_API_KEY
        if not self.api_base:
            self.api_base = get_from_env("GPUSTACK_API_BASE") or \
                GPUSTACK_DEFAULT_API_BASE
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured deployed model.

        The combined length of the input prompt and the generated
        completion must fit within this window. GPUStack serves arbitrary
        operator-deployed models under arbitrary names (``llama3.1-8b``,
        ``qwen2.5-72b``, ...), so — unlike the cloud vendors — no per-model
        lookup table can be maintained. The value is resolved in the
        following order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field, stored in the
           private ``_max_context_length`` attribute inherited from the
           LLM base class) that value wins. **Set this in your YAML** to
           the real window of the deployed model (e.g. 131072 for
           Llama 3.1, 32768 for Qwen2.5).
        2. As a last resort the conservative
           :data:`GPUSTACK_DEFAULT_CONTEXT_LENGTH` of 8192 tokens is
           returned, which keeps budget checks safe for unconfigured
           models.

        Note that unlike earlier releases ``OpenAIStyleLLM`` itself now
        always resolves to an int (falling back to its OpenAI table and a
        4096 default), so consulting ``super()`` first would silently
        shadow the GPUStack-specific logic below; the explicit
        ``_max_context_length`` check keeps the precedence right while
        preserving the explicit-configuration-wins contract.
        """
        if self._max_context_length:
            return self._max_context_length
        return GPUSTACK_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Deployed models (Llama, Qwen, DeepSeek, ...) each use their own
        tokenizer, none of which are registered in ``tiktoken`` under their
        GPUStack deployment names, so we fall back to the widely used
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
            # GPUStack deployment names are not registered in tiktoken;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
