# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 14:00
# @Author  : agentuniverse
# @FileName: xai_llm.py

"""
xAI (Grok) LLM.

xAI (https://x.ai) is the company behind the **Grok** family of large
language models. Grok models are tightly integrated with X (formerly
Twitter), are trained on xAI's own supercomputer **Colossus**, and cover the
full spectrum from flagship reasoning models (grok-4.x) over fast
tool-calling variants (grok-4.20-0309) to a dedicated coding model
(grok-build-0.1).

xAI exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.x.ai/v1``. Because of that compatibility this component simply
extends :class:`OpenAIStyleLLM` and only needs to wire up the correct default
environment variables, the xAI API base URL and the per-model maximum
context-length table. Streaming, tool calling, the async interface and the
Langchain bridge are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by the models
# currently available on the xAI API. The values are sourced from the
# official xAI models documentation (https://docs.x.ai/docs/models), which
# prints them as 500k / 1M / 256k; they are expanded to 500000 / 1000000 /
# 256000 following xAI's decimal convention (e.g. 256000 tokens for the
# grok-4 generation). This is also the conservative bound in case xAI backs
# one of the windows with a binary limit (524288 / 1048576 / 262144). When
# xAI ships a new model it is sufficient to add an entry here, the rest of
# the component keeps working unchanged.
XAI_MAX_CONTEXT_LENGTH = {
    # ---- Flagship reasoning models ----
    "grok-4.7": 500000,
    "grok-4.6": 500000,
    "grok-4.5": 500000,
    "grok-4.3": 1000000,
    # ---- Fast tool-calling / agent models ----
    "grok-4.20-0309-reasoning": 1000000,
    "grok-4.20-0309-non-reasoning": 1000000,
    "grok-4.20-multi-agent-0309": 1000000,
    # ---- Coding model ----
    "grok-build-0.1": 256000,
}

# Sensible default context length returned for models that are not yet listed
# in the table above. A conservative 32k window keeps prompt-budget checks on
# the safe side for freshly announced Grok models and dated or aliased
# releases whose base entry cannot be resolved.
XAI_DEFAULT_CONTEXT_LENGTH = 32768


class XaiLLM(OpenAIStyleLLM):
    """xAI Grok LLM, an OpenAI-compatible wrapper around the xAI API.

    xAI serves its Grok family of models (grok-4.x reasoning models, the
    grok-4.20 fast variants and the grok-build coding model) through an API
    that is fully OpenAI-compatible. Therefore this class only customises
    the credential/base-url plumbing and the model context-length lookup
    table while inheriting the complete request, streaming and
    langchain-bridge implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: xAI API key. Loaded from the ``XAI_API_KEY`` environment
            variable when not provided explicitly. Create one at
            https://console.x.ai.
        api_base: xAI OpenAI-compatible API base URL. Defaults to
            ``https://api.x.ai/v1`` unless overridden through the
            ``XAI_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("XAI_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("XAI_API_BASE") or
                                    "https://api.x.ai/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("XAI_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the xAI chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the xAI API
        base URL.

        Args:
            messages (list): The chat messages to send to xAI.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the xAI chat completions endpoint.

        Args:
            messages (list): The chat messages to send to xAI.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'XaiLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied ``xai_llm.yaml.example``
        with a missing ``XAI_API_KEY`` / ``XAI_PROXY`` would otherwise
        assign ``''`` over the class defaults. That is worse than it sounds:
        the OpenAI client only rejects a *missing* key, so an empty key is
        silently sent upstream and surfaces as an opaque 401, and an empty
        ``api_base`` makes the client fall back to ``https://api.openai.com/v1``
        — sending xAI credentials to the wrong endpoint. Normalizing the
        empty values here makes an unset variable behave exactly like an
        omitted key: ``api_key`` / ``proxy`` fall back to ``None`` and
        ``api_base`` to the xAI endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            XaiLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("XAI_API_BASE") or \
                "https://api.x.ai/v1"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Grok model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name is looked up in
           :data:`XAI_MAX_CONTEXT_LENGTH`. xAI documents ``<modelname>``,
           ``<modelname>-latest`` and ``<modelname>-<date>`` aliases for the
           same underlying release, so a trailing ``-latest`` suffix is
           stripped before the second lookup attempt.
        3. As a last resort :data:`XAI_DEFAULT_CONTEXT_LENGTH` is returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        if self.model_name in XAI_MAX_CONTEXT_LENGTH:
            return XAI_MAX_CONTEXT_LENGTH[self.model_name]
        if self.model_name and self.model_name.endswith('-latest'):
            base_name = self.model_name[:-len('-latest')]
            if base_name in XAI_MAX_CONTEXT_LENGTH:
                return XAI_MAX_CONTEXT_LENGTH[base_name]
        return XAI_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Grok models use xAI's own tokenizer, which is not registered in
        ``tiktoken`` by model name, so we fall back to the widely used
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
            # Grok models are not registered in tiktoken by name;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
