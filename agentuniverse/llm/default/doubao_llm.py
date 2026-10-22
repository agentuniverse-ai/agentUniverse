# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: doubao_llm.py

"""
Doubao (Volcengine Ark) LLM.

Doubao (豆包) is the family of large language models developed by **ByteDance**
and served through **Volcengine Ark** (火山方舟), ByteDance's managed model
platform. The family spans the general-purpose ``doubao-pro`` models, the
newer ``doubao-1.5-pro`` generation and the cost-optimised ``doubao-lite``
models, covering the full spectrum from 32k to 256k context windows.

Ark exposes a fully **OpenAI-compatible** Chat Completions API at
``https://ark.cn-beijing.volces.com/api/v3``. Because of that compatibility
this component simply extends :class:`OpenAIStyleLLM` and only needs to wire
up the correct default environment variables, the Ark API base URL and an
indicative per-model maximum context-length table. Streaming, tool calling,
the async interface and the Langchain bridge are inherited unchanged.
"""

import re
from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# Indicative maximum context length (input + output tokens) for popular
# Doubao model families served by Volcengine Ark. The values follow ByteDance's
# published model cards. Because Ark keeps adding generations and regional
# variants, the table is indicative rather than exhaustive: any model that is
# not listed falls back to a conservative 8192-token window (see
# DOUBAO_DEFAULT_CONTEXT_LENGTH), and users can always state the exact limit
# explicitly through the ``max_context_length`` YAML field. When ByteDance
# ships a new model it is sufficient to add an entry here, the rest of the
# component keeps working unchanged.
DOUBAO_MAX_CONTEXT_LENGTH = {
    # ---- Doubao 1.0 general-purpose family ----
    "doubao-pro-32k": 32768,
    "doubao-pro-128k": 131072,
    # ---- Doubao 1.5 family ----
    "doubao-1.5-pro-256k": 262144,
    # ---- Cost-optimised family ----
    "doubao-lite-32k": 32768,
}

# Conservative default context length returned for models that are not
# listed in the table above. Regional variants, freshly announced models and
# Ark inference endpoints (``ep-...``) can have very different windows, so a
# small 8k default keeps prompt-budget checks on the safe side until an
# explicit ``max_context_length`` is configured or a table entry is added.
DOUBAO_DEFAULT_CONTEXT_LENGTH = 8192

# Ark model IDs carry a version date suffix, e.g. ``doubao-pro-32k-250527``
# for the 2025-05-27 snapshot of ``doubao-pro-32k``. Such a trailing segment
# is stripped before the second table lookup so dated snapshots resolve to
# their family's context window.
_DOUBAO_DATE_SUFFIX_RE = re.compile(r"^(?P<base>.+)-(?P<date>\d{6,8})$")

# Ark API base URL and the default environment variable names.
DOUBAO_API_BASE_DEFAULT = "https://ark.cn-beijing.volces.com/api/v3"


def _doubao_api_key_from_env() -> Optional[str]:
    """Resolve the Doubao API key from the environment.

    ``ARK_API_KEY`` is the canonical variable used across the Volcengine
    ecosystem (the bundled :class:`DoubaoEmbedding` component reads it as
    well), so it is consulted first. ``DOUBAO_API_KEY`` is honoured as an
    explicit Doubao-only alias for users who prefer a component-specific
    name.

    Returns:
        The first non-empty environment value, or ``None`` when neither
        variable is set.
    """
    return get_from_env("ARK_API_KEY") or get_from_env("DOUBAO_API_KEY")


class DoubaoLLM(OpenAIStyleLLM):
    """Doubao LLM, an OpenAI-compatible wrapper around the Volcengine Ark API.

    ByteDance serves its Doubao model family (``doubao-pro``,
    ``doubao-1.5-pro``, ``doubao-lite``) through Volcengine Ark with an API
    that is fully OpenAI-compatible. Therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Ark API key. Loaded from the ``ARK_API_KEY`` environment
            variable when not provided explicitly, falling back to
            ``DOUBAO_API_KEY``. Create one in the Volcengine console at
            https://console.volcengine.com/ark.
        api_base: Ark OpenAI-compatible API base URL. Defaults to
            ``https://ark.cn-beijing.volces.com/api/v3`` unless overridden
            through the ``DOUBAO_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests, loaded
            from the ``DOUBAO_PROXY`` environment variable.
    """

    api_key: Optional[str] = Field(default_factory=_doubao_api_key_from_env)
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("DOUBAO_API_BASE") or
                                    DOUBAO_API_BASE_DEFAULT)
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("DOUBAO_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the Ark chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the Ark API base
        URL.

        Args:
            messages (list): The chat messages to send to Doubao.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the Ark chat completions endpoint.

        Args:
            messages (list): The chat messages to send to Doubao.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'DoubaoLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied ``doubao_llm.yaml.example``
        with a missing ``ARK_API_KEY`` / ``DOUBAO_PROXY`` would otherwise
        assign ``''`` over the class defaults. That is worse than it sounds:
        the OpenAI client only rejects a *missing* key, so an empty key is
        silently sent upstream and surfaces as an opaque 401, and an empty
        ``api_base`` makes the client fall back to
        ``https://api.openai.com/v1`` — sending the Ark credential to the
        wrong endpoint. Normalizing the empty values here makes an unset
        variable behave exactly like an omitted key: ``api_key`` / ``proxy``
        fall back to ``None`` and ``api_base`` to the Ark endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            DoubaoLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = _doubao_api_key_from_env()
        if not self.api_base:
            self.api_base = get_from_env("DOUBAO_API_BASE") or DOUBAO_API_BASE_DEFAULT
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Doubao model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field, stored in the
           private ``_max_context_length`` attribute inherited from the
           LLM base class) that value wins.
        2. Otherwise the model name is looked up in the indicative
           :data:`DOUBAO_MAX_CONTEXT_LENGTH` table.
        3. Ark model IDs often carry a trailing version-date suffix (e.g.
           ``doubao-pro-32k-250527``); that suffix is stripped and the
           family name (``doubao-pro-32k``) looked up instead.
        4. As a last resort the conservative
           :data:`DOUBAO_DEFAULT_CONTEXT_LENGTH` of 8192 tokens is returned,
           which keeps budget checks safe for regional variants, brand-new
           models and Ark inference endpoints (``ep-...``).

        Note that unlike earlier releases ``OpenAIStyleLLM`` itself now
        always resolves to an int (falling back to its OpenAI table and a
        4096 default), so consulting ``super()`` first would silently shadow
        the Doubao-specific lookup below; the explicit ``_max_context_length``
        check keeps the precedence Doubao-specific while preserving the
        explicit-configuration-wins contract.
        """
        if self._max_context_length:
            return self._max_context_length
        if self.model_name in DOUBAO_MAX_CONTEXT_LENGTH:
            return DOUBAO_MAX_CONTEXT_LENGTH[self.model_name]
        if self.model_name:
            match = _DOUBAO_DATE_SUFFIX_RE.match(self.model_name)
            if match and match.group('base') in DOUBAO_MAX_CONTEXT_LENGTH:
                return DOUBAO_MAX_CONTEXT_LENGTH[match.group('base')]
        return DOUBAO_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Doubao models use ByteDance's own tokenizer, which is not registered
        in ``tiktoken`` by model name, so we fall back to the widely used
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
            # Doubao model names are not registered in tiktoken;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
