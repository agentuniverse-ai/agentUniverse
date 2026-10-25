# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: nvidia_nim_llm.py

"""
NVIDIA NIM LLM.

NVIDIA NIM (https://build.nvidia.com, NVIDIA Inference Microservices) is
NVIDIA's hosted model catalogue on NVIDIA AI Foundation. It serves flagship
open and community models — e.g. ``meta/llama-3.1-405b-instruct``,
``nvidia/nemotron-4-340b-instruct`` and ``deepseek-ai/deepseek-r1`` — with
accelerated inference, and offers 1000 free credits for trying the API.

NIM exposes a fully **OpenAI-compatible** Chat Completions API at
``https://integrate.api.nvidia.com/v1``. Because of that compatibility this
component simply extends :class:`OpenAIStyleLLM` and only needs to wire up
the correct default environment variables, the NIM API base URL and an
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

# Indicative maximum context length (input + output tokens) for popular
# models hosted on the NVIDIA NIM API. The values follow the upstream model
# releases: the Llama 3.1 family supports a 128k window, DeepSeek-R1 128k,
# while Nemotron-4 340B is documented with a 4k window. Because NVIDIA keeps
# adding NIM endpoints whose windows are controlled by the respective model
# vendor, the table is indicative rather than exhaustive: any model that is
# not listed falls back to a conservative 8192-token window (see
# NVIDIA_NIM_DEFAULT_CONTEXT_LENGTH), and users can always state the exact
# limit explicitly through the ``max_context_length`` YAML field. When
# NVIDIA ships a new model it is sufficient to add an entry here, the rest
# of the component keeps working unchanged.
NVIDIA_NIM_MAX_CONTEXT_LENGTH = {
    # ---- Meta Llama 3.1 family ----
    "meta/llama-3.1-405b-instruct": 131072,
    "meta/llama-3.1-70b-instruct": 131072,
    # ---- NVIDIA Nemotron ----
    "nvidia/nemotron-4-340b-instruct": 4096,
    # ---- DeepSeek reasoning model ----
    "deepseek-ai/deepseek-r1": 131072,
}

# Conservative default context length returned for models that are not
# listed in the table above. Freshly announced NIM endpoints can have very
# different windows, so a small 8k default keeps prompt-budget checks on
# the safe side until an explicit ``max_context_length`` is configured or a
# table entry is added.
NVIDIA_NIM_DEFAULT_CONTEXT_LENGTH = 8192


class NvidiaNimLLM(OpenAIStyleLLM):
    """NVIDIA NIM LLM, an OpenAI-compatible wrapper around the NIM API.

    NVIDIA serves the models of its build.nvidia.com catalogue (e.g.
    ``meta/llama-3.1-405b-instruct``,
    ``nvidia/nemotron-4-340b-instruct``, ``deepseek-ai/deepseek-r1``)
    through an API that is fully OpenAI-compatible. Therefore this class
    only customises the credential/base-url plumbing and the model
    context-length lookup table while inheriting the complete request,
    streaming and langchain-bridge implementation from
    :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: NVIDIA NIM API key. Loaded from the ``NVIDIA_API_KEY``
            environment variable when not provided explicitly, falling back
            to the alias ``NVAPI_KEY`` used by NVIDIA tooling. Create one at
            https://build.nvidia.com.
        api_base: NVIDIA NIM OpenAI-compatible API base URL. Defaults to
            ``https://integrate.api.nvidia.com/v1`` unless overridden
            through the ``NVIDIA_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("NVIDIA_API_KEY") or
                                                 get_from_env("NVAPI_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("NVIDIA_API_BASE") or
                                    "https://integrate.api.nvidia.com/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("NVIDIA_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the NVIDIA NIM chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the NIM API
        base URL.

        Args:
            messages (list): The chat messages to send to NVIDIA NIM.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the NVIDIA NIM chat completions endpoint.

        Args:
            messages (list): The chat messages to send to NVIDIA NIM.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'NvidiaNimLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``nvidia_nim_llm.yaml.example`` with a missing ``NVIDIA_API_KEY`` /
        ``NVAPI_KEY`` / ``NVIDIA_PROXY`` would otherwise assign ``''`` over
        the class defaults. That is worse than it sounds: the OpenAI client
        only rejects a *missing* key, so an empty key is silently sent
        upstream and surfaces as an opaque 401, and an empty ``api_base``
        makes the client fall back to ``https://api.openai.com/v1`` —
        sending the NIM key to the wrong endpoint. Normalizing the empty
        values here makes an unset variable behave exactly like an omitted
        key: ``api_key`` (re-consulting ``NVIDIA_API_KEY`` and the
        ``NVAPI_KEY`` alias) / ``proxy`` fall back to ``None`` and
        ``api_base`` to the NIM endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            NvidiaNimLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = get_from_env("NVIDIA_API_KEY") or \
                get_from_env("NVAPI_KEY")
        if not self.api_base:
            self.api_base = get_from_env("NVIDIA_API_BASE") or \
                "https://integrate.api.nvidia.com/v1"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured NIM model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field, stored in the
           private ``_max_context_length`` attribute inherited from the
           LLM base class) that value wins.
        2. Otherwise the model name is looked up in the indicative
           :data:`NVIDIA_NIM_MAX_CONTEXT_LENGTH` table.
        3. As a last resort the conservative
           :data:`NVIDIA_NIM_DEFAULT_CONTEXT_LENGTH` of 8192 tokens is
           returned, which keeps budget checks safe for freshly announced
           and not yet listed NIM models.

        Note that unlike earlier releases ``OpenAIStyleLLM`` itself now
        always resolves to an int (falling back to its OpenAI table and a
        4096 default), so consulting ``super()`` first would silently shadow
        the NVIDIA-specific lookup below; the explicit ``_max_context_length``
        check keeps the precedence NVIDIA-specific while preserving the
        explicit-configuration-wins contract.
        """
        if self._max_context_length:
            return self._max_context_length
        if self.model_name in NVIDIA_NIM_MAX_CONTEXT_LENGTH:
            return NVIDIA_NIM_MAX_CONTEXT_LENGTH[self.model_name]
        return NVIDIA_NIM_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        The models served by NVIDIA NIM (Llama, Nemotron, DeepSeek, ...)
        are addressed by their catalogue path (e.g.
        ``meta/llama-3.1-405b-instruct``) which is not registered in
        ``tiktoken`` by name, so we fall back to the widely used
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
            # NIM catalogue names are not registered in tiktoken;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
