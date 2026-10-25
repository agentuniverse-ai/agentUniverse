# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: llamacpp_llm.py

"""
llama.cpp llama-server LLM.

llama.cpp (https://github.com/ggml-org/llama.cpp) is the reference C/C++
inference engine for **GGUF** large language models. Its ``llama-server``
binary loads a local ``.gguf`` file (Llama, Qwen, Mistral, Gemma, ...)
onto the CPU/GPU of the machine and serves it through a built-in local
API server. That server speaks a fully **OpenAI-compatible** Chat
Completions dialect on ``http://localhost:8080/v1`` by default, and the
served model identifier is whatever alias was passed on the command line
with ``--alias`` (or the GGUF file name) — there is no vendor model
catalogue at all.

Because of that OpenAI compatibility this component simply extends
:class:`OpenAIStyleLLM` and only needs to wire up the correct default
environment variables and the llama-server local endpoint. Streaming,
tool calling, the async interface and the Langchain bridge are inherited
unchanged. Two aspects are special about a local server runtime:

* **No API key is required.** The local llama-server accepts any bearer
  token, so the component defaults ``api_key`` to the harmless
  placeholder ``"no-key"`` purely because the OpenAI client refuses to
  be built without one; point ``LLAMACPP_API_KEY`` at a real value only
  if you put an authenticating gateway in front of the server.
* **No context-length table is possible.** Arbitrary local GGUF models
  arrive with arbitrary names and their context window is whatever
  ``-c`` flag the server was started with, so instead of a per-model
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

# Default URL of the llama.cpp llama-server API. The port 8080 is
# llama-server's documented default; override it through the
# LLAMACPP_API_BASE environment variable when the server was started
# with a different ``--host`` / ``--port`` combination.
LLAMACPP_DEFAULT_API_BASE = "http://localhost:8080/v1"

# Placeholder bearer token used when no real key is configured. A local
# llama-server does not authenticate requests and happily accepts any
# string, but the OpenAI python client refuses to be constructed with
# api_key=None, so a harmless constant is shipped instead of None.
LLAMACPP_PLACEHOLDER_API_KEY = "no-key"

# Conservative default context length returned when the YAML configuration
# does not state one. llama-server serves arbitrary local GGUF models under
# arbitrary aliases and the effective window is set by the ``-c`` start-up
# flag, so no per-model lookup table can be maintained; a small 8k default
# keeps prompt-budget checks on the safe side until the real limit is
# configured through the ``max_context_length`` YAML field.
LLAMACPP_DEFAULT_CONTEXT_LENGTH = 8192


class LlamaCppLLM(OpenAIStyleLLM):
    """llama.cpp llama-server LLM, an OpenAI-compatible wrapper around the
    llama.cpp local server.

    ``llama-server`` runs a local GGUF model and exposes it through an
    OpenAI-compatible API on ``http://localhost:8080/v1``. Therefore this
    class only customises the credential/base-url plumbing and the
    context-length fallback while inheriting the complete request,
    streaming and langchain-bridge implementation from
    :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Bearer token for the llama-server. **No key is
            required** for a local llama-server — it accepts any value,
            so the component defaults to the harmless ``"no-key"``
            placeholder (the OpenAI client refuses to be built without a
            key). Load a real token from the ``LLAMACPP_API_KEY``
            environment variable only when an authenticating gateway sits
            in front of the server.
        api_base: llama-server OpenAI-compatible local API base URL.
            Defaults to ``http://localhost:8080/v1`` unless overridden
            through the ``LLAMACPP_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy. llama-server runs on the same
            machine or LAN so a proxy is normally not applicable; the
            field is kept for consistency with the other OpenAI-style
            components and can be set through ``LLAMACPP_PROXY``.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("LLAMACPP_API_KEY") or
                                    LLAMACPP_PLACEHOLDER_API_KEY)
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("LLAMACPP_API_BASE") or
                                    LLAMACPP_DEFAULT_API_BASE)
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("LLAMACPP_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the llama-server chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the
        llama-server API base URL.

        Args:
            messages (list): The chat messages to send to llama-server.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the llama-server chat completions endpoint.

        Args:
            messages (list): The chat messages to send to llama-server.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'LlamaCppLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``llamacpp_llm.yaml.example`` with a missing
        ``LLAMACPP_API_BASE`` / ``LLAMACPP_PROXY`` would otherwise assign
        ``''`` over the class defaults. That is worse than it sounds: an
        empty ``api_base`` makes the OpenAI client fall back to
        ``https://api.openai.com/v1`` — sending llama-server requests to
        the wrong endpoint — and an empty ``api_key`` would be silently
        sent upstream. Normalizing the empty values here makes an unset
        variable behave exactly like an omitted key: ``api_key`` falls
        back to the harmless llama-server placeholder (or the
        ``LLAMACPP_API_KEY`` environment value), ``api_base`` to the
        local llama-server endpoint and ``proxy`` to ``None``.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            LlamaCppLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = get_from_env("LLAMACPP_API_KEY") or \
                LLAMACPP_PLACEHOLDER_API_KEY
        if not self.api_base:
            self.api_base = get_from_env("LLAMACPP_API_BASE") or \
                LLAMACPP_DEFAULT_API_BASE
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured local model.

        The combined length of the input prompt and the generated
        completion must fit within this window. llama-server serves
        arbitrary local GGUF models under arbitrary aliases with the
        effective window set by the ``-c`` start-up flag, so — unlike
        the cloud vendors — no per-model lookup table can be maintained.
        The value is resolved in the following order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field, stored in the
           private ``_max_context_length`` attribute inherited from the
           LLM base class) that value wins. **Set this in your YAML** to
           the window the server was started with (e.g. 32768 for a
           ``llama-server -c 32768`` invocation, 131072 for Llama 3.1).
        2. As a last resort the conservative
           :data:`LLAMACPP_DEFAULT_CONTEXT_LENGTH` of 8192 tokens is
           returned, which keeps budget checks safe for unconfigured
           models.

        Note that unlike earlier releases ``OpenAIStyleLLM`` itself now
        always resolves to an int (falling back to its OpenAI table and a
        4096 default), so consulting ``super()`` first would silently
        shadow the llama.cpp-specific logic below; the explicit
        ``_max_context_length`` check keeps the precedence right while
        preserving the explicit-configuration-wins contract.
        """
        if self._max_context_length:
            return self._max_context_length
        return LLAMACPP_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Locally served GGUF models (Llama, Qwen, Mistral, ...) each use
        their own tokenizer, none of which are registered in ``tiktoken``
        by their llama-server aliases, so we fall back to the widely used
        ``cl100k_base`` encoding which gives a good approximation
        suitable for budget/prompt-window checks.

        Args:
            text: The raw string to tokenize.

        Returns:
            The integer number of tokens the text would be encoded into.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # Local GGUF model aliases are not registered in tiktoken;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
