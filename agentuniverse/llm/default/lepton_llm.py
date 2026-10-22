# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: lepton_llm.py

"""
Lepton AI LLM.

Lepton AI (https://lepton.ai, now part of NVIDIA DGX Cloud Lepton) is a
managed AI platform that serves both open-source models it deploys itself
(e.g. ``llama3.1-8b``, ``llama3.1-70b``, ``mistral-7b``) and third-party
marketplace models (e.g. ``gpt-4o-mini``, ``claude-3-5-sonnet``) behind a
single billing and API surface.

Lepton exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.lepton.run/api/v1``. Because of that compatibility this
component simply extends :class:`OpenAIStyleLLM` and only needs to wire up
the correct default environment variables, the Lepton API base URL and an
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
# models hosted on Lepton. The values follow the upstream model releases
# (Llama 3.1 supports a 128k window, Mistral v0.1/v0.2 7B a 32k window).
# Because Lepton keeps adding deployments and marketplace models whose
# windows are controlled by the respective vendor, the table is indicative
# rather than exhaustive: any model that is not listed falls back to a
# conservative 8192-token window (see LEPTON_DEFAULT_CONTEXT_LENGTH), and
# users can always state the exact limit explicitly through the
# ``max_context_length`` YAML field. When Lepton ships a new model it is
# sufficient to add an entry here, the rest of the component keeps working
# unchanged.
LEPTON_MAX_CONTEXT_LENGTH = {
    # ---- Open-source models deployed by Lepton ----
    "llama3.1-8b": 131072,
    "llama3.1-70b": 131072,
    "mistral-7b": 32768,
    # ---- Marketplace models ----
    "gpt-4o-mini": 131072,
}

# Conservative default context length returned for models that are not
# listed in the table above. Marketplace and freshly announced models can
# have very different windows, so a small 8k default keeps prompt-budget
# checks on the safe side until an explicit ``max_context_length`` is
# configured or a table entry is added.
LEPTON_DEFAULT_CONTEXT_LENGTH = 8192


class LeptonLLM(OpenAIStyleLLM):
    """Lepton AI LLM, an OpenAI-compatible wrapper around the Lepton API.

    Lepton serves both self-deployed open-source models (``llama3.1-8b``,
    ``llama3.1-70b``, ``mistral-7b``) and third-party marketplace models
    (``gpt-4o-mini`` and friends) through an API that is fully
    OpenAI-compatible. Therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Lepton API key (workspace token). Loaded from the
            ``LEPTON_API_KEY`` environment variable when not provided
            explicitly. Create one at https://dashboard.lepton.ai.
        api_base: Lepton OpenAI-compatible API base URL. Defaults to
            ``https://api.lepton.run/api/v1`` unless overridden through the
            ``LEPTON_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("LEPTON_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("LEPTON_API_BASE") or
                                    "https://api.lepton.run/api/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("LEPTON_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the Lepton chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the Lepton API
        base URL.

        Args:
            messages (list): The chat messages to send to Lepton.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the Lepton chat completions endpoint.

        Args:
            messages (list): The chat messages to send to Lepton.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'LeptonLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied ``lepton_llm.yaml.example``
        with a missing ``LEPTON_API_KEY`` / ``LEPTON_PROXY`` would otherwise
        assign ``''`` over the class defaults. That is worse than it sounds:
        the OpenAI client only rejects a *missing* key, so an empty key is
        silently sent upstream and surfaces as an opaque 401, and an empty
        ``api_base`` makes the client fall back to
        ``https://api.openai.com/v1`` — sending the Lepton workspace token
        to the wrong endpoint. Normalizing the empty values here makes an
        unset variable behave exactly like an omitted key: ``api_key`` /
        ``proxy`` fall back to ``None`` and ``api_base`` to the Lepton
        endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            LeptonLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("LEPTON_API_BASE") or \
                "https://api.lepton.run/api/v1"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Lepton model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field, stored in the
           private ``_max_context_length`` attribute inherited from the
           LLM base class) that value wins.
        2. Otherwise the model name is looked up in the indicative
           :data:`LEPTON_MAX_CONTEXT_LENGTH` table.
        3. As a last resort the conservative
           :data:`LEPTON_DEFAULT_CONTEXT_LENGTH` of 8192 tokens is returned,
           which keeps budget checks safe for marketplace and not yet listed
           models.

        Note that unlike earlier releases ``OpenAIStyleLLM`` itself now
        always resolves to an int (falling back to its OpenAI table and a
        4096 default), so consulting ``super()`` first would silently shadow
        the Lepton-specific lookup below; the explicit ``_max_context_length``
        check keeps the precedence Lepton-specific while preserving the
        explicit-configuration-wins contract.
        """
        if self._max_context_length:
            return self._max_context_length
        if self.model_name in LEPTON_MAX_CONTEXT_LENGTH:
            return LEPTON_MAX_CONTEXT_LENGTH[self.model_name]
        return LEPTON_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        The open-source models served by Lepton (Llama, Mistral, Qwen, ...)
        are not registered in ``tiktoken`` by their Lepton deployment names,
        so we fall back to the widely used ``cl100k_base`` encoding which
        gives a good approximation suitable for budget/prompt-window checks.

        Args:
            text: The raw string to tokenize.

        Returns:
            The integer number of tokens the text would be encoded into.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # Lepton deployment names are not registered in tiktoken;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
