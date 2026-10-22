# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: lmstudio_llm.py

"""
LM Studio LLM.

LM Studio (https://lmstudio.ai) is a desktop application for Windows, macOS
and Linux that runs large language models **fully locally**. It downloads
GGUF weights (Llama, Qwen, Mistral, Gemma, ...) from Hugging Face, loads
them onto the CPU/GPU of the machine and serves them through a built-in
local API server. That server speaks a fully **OpenAI-compatible** Chat
Completions dialect on ``http://localhost:1234/v1`` by default, and the
served model identifiers are whatever the user named the downloaded files
— there is no vendor model catalogue at all.

Because of that OpenAI compatibility this component simply extends
:class:`OpenAIStyleLLM` and only needs to wire up the correct default
environment variables and the LM Studio local endpoint. Streaming, tool
calling, the async interface and the Langchain bridge are inherited
unchanged. Two aspects are special about a local desktop runtime:

* **No API key is required.** The local server accepts any bearer token,
  so the component defaults ``api_key`` to the harmless placeholder
  ``"lm-studio"`` purely because the OpenAI client refuses to be built
  without one; point ``LMSTUDIO_API_KEY`` at a real value only if you put
  a gateway in front of the server.
* **No context-length table is possible.** Arbitrary GGUF models arrive
  with arbitrary names, so instead of a per-model lookup table the
  component falls back to a conservative 8192-token window and expects
  users to state the real limit through the ``max_context_length`` YAML
  field.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# Default URL of LM Studio's built-in local server. The port 1234 is LM
# Studio's documented default ("Local Server" tab in the LM Studio UI);
# override it through the LMSTUDIO_API_BASE environment variable when the
# server is bound to a different port or host.
LMSTUDIO_DEFAULT_API_BASE = "http://localhost:1234/v1"

# Placeholder bearer token used when no real key is configured. LM Studio
# does not authenticate requests from the local machine and happily accepts
# any string, but the OpenAI python client refuses to be constructed with
# api_key=None, so a harmless constant is shipped instead of None.
LMSTUDIO_PLACEHOLDER_API_KEY = "lm-studio"

# Conservative default context length returned when the YAML configuration
# does not state one. LM Studio serves arbitrary locally downloaded GGUF
# models under arbitrary user-chosen names, so no per-model lookup table
# can be maintained; a small 8k default keeps prompt-budget checks on the
# safe side until the real limit is configured through the
# ``max_context_length`` YAML field.
LMSTUDIO_DEFAULT_CONTEXT_LENGTH = 8192


class LMStudioLLM(OpenAIStyleLLM):
    """LM Studio LLM, an OpenAI-compatible wrapper around LM Studio's local server.

    LM Studio runs GGUF models locally and exposes them through an
    OpenAI-compatible API on ``http://localhost:1234/v1``. Therefore this
    class only customises the credential/base-url plumbing and the
    context-length fallback while inheriting the complete request,
    streaming and langchain-bridge implementation from
    :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Bearer token for the LM Studio server. **No key is
            required** for a local LM Studio server — it accepts any value,
            so the component defaults to the harmless ``"lm-studio"``
            placeholder (the OpenAI client refuses to be built without a
            key). Load a real token from the ``LMSTUDIO_API_KEY``
            environment variable only when an authenticating gateway sits
            in front of the server.
        api_base: LM Studio OpenAI-compatible local API base URL.
            Defaults to ``http://localhost:1234/v1`` unless overridden
            through the ``LMSTUDIO_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy. LM Studio runs on the same machine
            so a proxy is normally not applicable; the field is kept for
            consistency with the other OpenAI-style components and can be
            set through ``LMSTUDIO_PROXY``.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("LMSTUDIO_API_KEY") or
                                    LMSTUDIO_PLACEHOLDER_API_KEY)
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("LMSTUDIO_API_BASE") or
                                    LMSTUDIO_DEFAULT_API_BASE)
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("LMSTUDIO_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the LM Studio local chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the LM Studio
        API base URL.

        Args:
            messages (list): The chat messages to send to LM Studio.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the LM Studio local chat completions endpoint.

        Args:
            messages (list): The chat messages to send to LM Studio.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'LMStudioLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``lmstudio_llm.yaml.example`` with a missing
        ``LMSTUDIO_API_BASE`` / ``LMSTUDIO_PROXY`` would otherwise assign
        ``''`` over the class defaults. That is worse than it sounds: an
        empty ``api_base`` makes the OpenAI client fall back to
        ``https://api.openai.com/v1`` — sending LM Studio requests to the
        wrong endpoint — and an empty ``api_key`` would be silently sent
        upstream. Normalizing the empty values here makes an unset
        variable behave exactly like an omitted key: ``api_key`` falls
        back to the harmless LM Studio placeholder (or the
        ``LMSTUDIO_API_KEY`` environment value), ``api_base`` to the local
        LM Studio endpoint and ``proxy`` to ``None``.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            LMStudioLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = get_from_env("LMSTUDIO_API_KEY") or \
                LMSTUDIO_PLACEHOLDER_API_KEY
        if not self.api_base:
            self.api_base = get_from_env("LMSTUDIO_API_BASE") or \
                LMSTUDIO_DEFAULT_API_BASE
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured local model.

        The combined length of the input prompt and the generated
        completion must fit within this window. LM Studio serves arbitrary
        locally downloaded GGUF models under arbitrary user-chosen names,
        so — unlike the cloud vendors — no per-model lookup table can be
        maintained. The value is resolved in the following order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field, stored in the
           private ``_max_context_length`` attribute inherited from the
           LLM base class) that value wins. **Set this in your YAML** to
           the real window of the downloaded model (e.g. 32768 for most
           Qwen2.5-7B builds, 131072 for Llama 3.1).
        2. As a last resort the conservative
           :data:`LMSTUDIO_DEFAULT_CONTEXT_LENGTH` of 8192 tokens is
           returned, which keeps budget checks safe for unconfigured
           models.

        Note that unlike earlier releases ``OpenAIStyleLLM`` itself now
        always resolves to an int (falling back to its OpenAI table and a
        4096 default), so consulting ``super()`` first would silently
        shadow the LM Studio-specific logic below; the explicit
        ``_max_context_length`` check keeps the precedence right while
        preserving the explicit-configuration-wins contract.
        """
        if self._max_context_length:
            return self._max_context_length
        return LMSTUDIO_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Locally served GGUF models (Llama, Qwen, Mistral, ...) each use
        their own tokenizer, none of which are registered in ``tiktoken``
        by their LM Studio model names, so we fall back to the widely used
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
            # Local GGUF model names are not registered in tiktoken;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
