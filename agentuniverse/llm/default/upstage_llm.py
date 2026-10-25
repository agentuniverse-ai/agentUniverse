# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 19:00
# @Author  : agentuniverse
# @FileName: upstage_llm.py

"""
Upstage Solar LLM.

Upstage (https://upstage.ai) is a Korean AI company based in Seoul and the
team behind the **Solar** family of large language models. Solar models are
optimised for Korean and multilingual workloads and cover the full spectrum
from the flagship frontier model (solar-pro-2) over the cost-efficient
general-purpose variant (solar-pro, solar-mini) to a dedicated document
understanding model (solar-docvision).

Upstage exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.upstage.ai/v1/solar``. Because of that compatibility this
component simply extends :class:`OpenAIStyleLLM` and only needs to wire up
the correct default environment variables, the Upstage API base URL and the
per-model maximum context-length table. Streaming, tool calling, the async
interface and the Langchain bridge are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by the Solar
# models currently listed in the Upstage documentation (https://developers.upstage.ai).
# The values below are indicative 64k windows (65536 tokens) published by
# Upstage for the Solar generation available through the Solar API; treat them
# as a budgeting hint and confirm the current numbers in the official docs
# before relying on the exact limit. When Upstage ships a new model it is
# sufficient to add an entry here, the rest of the component keeps working
# unchanged.
UPSTAGE_MAX_CONTEXT_LENGTH = {
    # ---- Flagship frontier model ----
    "solar-pro-2": 65536,
    # ---- General-purpose models ----
    "solar-pro": 65536,
    "solar-mini": 65536,
    # ---- Document understanding model ----
    "solar-docvision": 65536,
}

# Sensible default context length returned for models that are not yet listed
# in the table above. A conservative 8k window keeps prompt-budget checks on
# the safe side for freshly announced Solar models and dated or aliased
# releases whose base entry cannot be resolved.
UPSTAGE_DEFAULT_CONTEXT_LENGTH = 8192


class UpstageLLM(OpenAIStyleLLM):
    """Upstage Solar LLM, an OpenAI-compatible wrapper around the Solar API.

    Upstage serves its Solar family of models (the solar-pro-2 flagship,
    solar-pro / solar-mini general-purpose models and the solar-docvision
    document understanding model) through an API that is fully
    OpenAI-compatible. Therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Upstage API key. Loaded from the ``UPSTAGE_API_KEY``
            environment variable when not provided explicitly. Create one at
            https://console.upstage.ai.
        api_base: Upstage OpenAI-compatible API base URL. Defaults to
            ``https://api.upstage.ai/v1/solar`` unless overridden through the
            ``UPSTAGE_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("UPSTAGE_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("UPSTAGE_API_BASE") or
                                    "https://api.upstage.ai/v1/solar")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("UPSTAGE_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the Upstage Solar chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the Upstage API
        base URL.

        Args:
            messages (list): The chat messages to send to Upstage.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the Upstage Solar chat completions endpoint.

        Args:
            messages (list): The chat messages to send to Upstage.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'UpstageLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``upstage_llm.yaml.example`` with a missing ``UPSTAGE_API_KEY`` /
        ``UPSTAGE_PROXY`` would otherwise assign ``''`` over the class
        defaults. That is worse than it sounds: the OpenAI client only
        rejects a *missing* key, so an empty key is silently sent upstream
        and surfaces as an opaque 401, and an empty ``api_base`` makes the
        client fall back to ``https://api.openai.com/v1`` — sending Upstage
        credentials to the wrong endpoint. Normalizing the empty values here
        makes an unset variable behave exactly like an omitted key:
        ``api_key`` / ``proxy`` fall back to ``None`` and ``api_base`` to
        the Upstage endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            UpstageLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("UPSTAGE_API_BASE") or \
                "https://api.upstage.ai/v1/solar"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Solar model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name is looked up in
           :data:`UPSTAGE_MAX_CONTEXT_LENGTH`.
        3. As a last resort :data:`UPSTAGE_DEFAULT_CONTEXT_LENGTH` is
           returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        if self.model_name in UPSTAGE_MAX_CONTEXT_LENGTH:
            return UPSTAGE_MAX_CONTEXT_LENGTH[self.model_name]
        return UPSTAGE_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Solar models use Upstage's own tokenizer, which is not registered in
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
            # Solar models are not registered in tiktoken by name;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
