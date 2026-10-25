# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: openrouter_llm.py

"""
OpenRouter LLM.

OpenRouter (https://openrouter.ai) is a unified gateway that exposes
**hundreds of large language models** from dozens of providers (OpenAI,
Anthropic, Google, Meta, Mistral, DeepSeek, Qwen, xAI and many more)
through a single **OpenAI-compatible** Chat Completions API at
``https://openrouter.ai/api/v1``. Models are addressed with their
prefixed routing name, e.g. ``openai/gpt-4o-mini`` or
``anthropic/claude-3.5-sonnet``.

Because the API is OpenAI-compatible this component simply extends
:class:`OpenAIStyleLLM` and only needs to wire up the correct default
environment variables, the OpenRouter API base URL and the optional
attribution headers (``HTTP-Referer`` / ``X-Title``) that OpenRouter uses
to attribute traffic to an application on its public rankings page.
Streaming, tool calling, the async interface and the Langchain bridge are
inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The OpenRouter API base URL. This is the plain base - the OpenAI client
# appends the /chat/completions route itself, so the route must NOT be part
# of this value.
OPENROUTER_DEFAULT_API_BASE = "https://openrouter.ai/api/v1"

# OpenRouter routes to hundreds of models from many different providers, so
# unlike single-provider components there is no fixed context-length table
# that could be hard-coded here. The YAML ``max_context_length`` field is the
# authoritative source; this value is only a conservative fallback for
# prompt-budget checks when the user did not configure one. Set
# ``max_context_length`` explicitly when using large-context models
# (e.g. 200000 for ``anthropic/claude-3.5-sonnet``) so agentUniverse does not
# truncate prompts unnecessarily.
OPENROUTER_DEFAULT_CONTEXT_LENGTH = 8192


class OpenRouterLLM(OpenAIStyleLLM):
    """OpenRouter LLM, an OpenAI-compatible wrapper around the OpenRouter API.

    OpenRouter aggregates hundreds of models behind one OpenAI-compatible
    endpoint, so this class only customises the credential/base-url plumbing
    and the optional attribution headers while inheriting the complete
    request, streaming and langchain-bridge implementation from
    :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: OpenRouter API key. Loaded from the ``OPENROUTER_API_KEY``
            environment variable when not provided explicitly. Create one at
            https://openrouter.ai/settings/keys.
        api_base: OpenRouter OpenAI-compatible API base URL. Defaults to
            ``https://openrouter.ai/api/v1`` unless overridden through the
            ``OPENROUTER_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
        http_referer: Optional value for the ``HTTP-Referer`` attribution
            header. OpenRouter displays it on its public rankings/leaderboard
            so requests can be attributed to your site or app.
        app_title: Optional value for the ``X-Title`` attribution header.
            OpenRouter displays the app title next to the ``HTTP-Referer``
            attribution on its rankings page.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("OPENROUTER_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("OPENROUTER_API_BASE") or
                                    OPENROUTER_DEFAULT_API_BASE)
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("OPENROUTER_PROXY"))
    http_referer: Optional[str] = Field(default_factory=lambda: get_from_env("OPENROUTER_HTTP_REFERER"))
    app_title: Optional[str] = Field(default_factory=lambda: get_from_env("OPENROUTER_APP_TITLE"))

    def _attribution_headers(self) -> dict:
        """Build the extra headers to send with every request.

        The OpenRouter attribution headers (``HTTP-Referer`` and ``X-Title``)
        are optional but recommended: OpenRouter uses them to attribute
        traffic to an application on its public rankings page. Headers that
        were already configured explicitly through the YAML
        ``extra_headers`` block always win over the dedicated fields.

        Returns:
            A dict with the merged headers, possibly empty when neither
            attribution fields nor ``extra_headers`` are configured.
        """
        headers = dict(self.ext_headers or {})
        if self.http_referer:
            headers.setdefault('HTTP-Referer', self.http_referer)
        if self.app_title:
            headers.setdefault('X-Title', self.app_title)
        return headers

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the OpenRouter chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation injects the OpenRouter attribution headers
        (when configured) and delegates to the OpenAI-style parent which
        constructs and dispatches the request against the OpenRouter API
        base URL.

        Args:
            messages (list): The chat messages to send to OpenRouter.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...
                An explicit ``extra_headers`` kwarg suppresses the automatic
                attribution headers.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        if 'extra_headers' not in kwargs:
            attribution_headers = self._attribution_headers()
            if attribution_headers:
                kwargs['extra_headers'] = attribution_headers
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the OpenRouter chat completions endpoint.

        Args:
            messages (list): The chat messages to send to OpenRouter.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client. An explicit ``extra_headers`` kwarg suppresses
                the automatic attribution headers.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        if 'extra_headers' not in kwargs:
            attribution_headers = self._attribution_headers()
            if attribution_headers:
                kwargs['extra_headers'] = attribution_headers
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'OpenRouterLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``openrouter_llm.yaml.example`` with a missing
        ``OPENROUTER_API_KEY`` / ``OPENROUTER_PROXY`` would otherwise
        assign ``''`` over the class defaults. That is worse than it sounds:
        the OpenAI client only rejects a *missing* key, so an empty key is
        silently sent upstream and surfaces as an opaque 401, and an empty
        ``api_base`` makes the client fall back to
        ``https://api.openai.com/v1`` - sending the OpenRouter credentials
        to the wrong endpoint. Normalizing the empty values here makes an
        unset variable behave exactly like an omitted key: ``api_key`` /
        ``proxy`` / attribution fields fall back to ``None`` and
        ``api_base`` to the OpenRouter endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            OpenRouterLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        config_value = component_configer.configer.value
        if config_value.get('http_referer'):
            self.http_referer = config_value.get('http_referer')
        if config_value.get('app_title'):
            self.app_title = config_value.get('app_title')
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("OPENROUTER_API_BASE") or \
                OPENROUTER_DEFAULT_API_BASE
        if not self.proxy:
            self.proxy = None
        if not self.http_referer:
            self.http_referer = None
        if not self.app_title:
            self.app_title = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured model.

        The combined length of the input prompt and the generated completion
        must fit within this window. OpenRouter routes to hundreds of models
        from many providers whose context windows range from 4k to 1M+
        tokens and change frequently, so no static lookup table is kept.
        The value is resolved as:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) or through
           ``set_by_agent_model`` that value wins. **Users are expected to
           set this field** to the documented window of the model they
           route to.
        2. Otherwise the conservative
           :data:`OPENROUTER_DEFAULT_CONTEXT_LENGTH` (8192) is returned so
           prompt-budget checks stay on the safe side. Note that this
           fallback may be far smaller than the real window of
           large-context models; configure ``max_context_length`` to make
           full use of them.
        """
        if super().max_context_length():
            return super().max_context_length()
        return OPENROUTER_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        OpenRouter routes to models from many providers, each with their own
        tokenizer, and the prefixed routing names (e.g.
        ``openai/gpt-4o-mini``) are not registered in ``tiktoken``. When the
        model name resolves to a known OpenAI tokenizer that one is used,
        otherwise we fall back to the widely used ``cl100k_base`` encoding
        which gives a good approximation suitable for budget/prompt-window
        checks.

        Args:
            text: The raw string to tokenize.

        Returns:
            The integer number of tokens the text would be encoded into.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # Routing names such as "anthropic/claude-3.5-sonnet" are not
            # registered in tiktoken by name; cl100k_base is a robust
            # generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
