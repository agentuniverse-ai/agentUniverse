# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 16:00
# @Author  : agentuniverse
# @FileName: perplexity_llm.py

"""
Perplexity (Sonar) LLM.

Perplexity (https://www.perplexity.ai) exposes its **Sonar** family of
online large language models through a fully **OpenAI-compatible** Chat
Completions API at ``https://api.perplexity.ai``. Sonar models combine a
standard LLM with live web search and return grounded answers with
citations, covering the full spectrum from the fast and lightweight
``sonar`` over the extended-context ``sonar-pro`` and the chain-of-thought
``sonar-reasoning`` / ``sonar-reasoning-pro`` variants to the
multi-step research model ``sonar-deep-research``.

Because of that OpenAI compatibility this component simply extends
:class:`OpenAIStyleLLM` and only needs to wire up the correct default
environment variables, the Perplexity API base URL and the per-model
maximum context-length table. Streaming, tool calling, the async
interface and the Langchain bridge are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# Indicative maximum context length (input + output tokens) of the Sonar
# models currently available on the Perplexity API. The values are taken
# from the official Perplexity models documentation
# (https://docs.perplexity.ai/guides/getting-started), which lists an
# online context of 127072 tokens for the sonar generation and documents
# the limits as roughly 200k for sonar / sonar-pro and ~128k for
# sonar-reasoning-pro. Because Perplexity tunes these windows together
# with the amount of search context injected at request time, the table is
# *indicative*: treat it as a budgeting aid for prompt-window checks, not
# as a hard guarantee. When Perplexity ships a new model it is sufficient
# to add an entry here, the rest of the component keeps working unchanged.
PERPLEXITY_MAX_CONTEXT_LENGTH = {
    # ---- Fast, lightweight online models ----
    "sonar": 127072,
    "sonar-pro": 200000,
    # ---- Chain-of-thought reasoning models ----
    "sonar-reasoning": 127072,
    "sonar-reasoning-pro": 128000,
    # ---- Multi-step research model ----
    "sonar-deep-research": 127072,
}

# Sensible default context length returned for models that are not yet
# listed in the table above. A conservative 8k window keeps prompt-budget
# checks on the safe side for freshly announced Sonar models and dated or
# aliased releases whose base entry cannot be resolved.
PERPLEXITY_DEFAULT_CONTEXT_LENGTH = 8192


class PerplexityLLM(OpenAIStyleLLM):
    """Perplexity Sonar LLM, an OpenAI-compatible wrapper around the Perplexity API.

    Perplexity serves its Sonar family of online models (the lightweight
    ``sonar``, the extended-context ``sonar-pro``, the reasoning variants
    ``sonar-reasoning`` / ``sonar-reasoning-pro`` and the research model
    ``sonar-deep-research``) through an API that is fully
    OpenAI-compatible. Therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup
    table while inheriting the complete request, streaming and
    langchain-bridge implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Perplexity API key. Loaded from the ``PERPLEXITY_API_KEY``
            environment variable when not provided explicitly. Create one
            at https://www.perplexity.ai/settings/api.
        api_base: Perplexity OpenAI-compatible API base URL. Defaults to
            ``https://api.perplexity.ai`` unless overridden through the
            ``PERPLEXITY_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("PERPLEXITY_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("PERPLEXITY_API_BASE") or
                                    "https://api.perplexity.ai")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("PERPLEXITY_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the Perplexity chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the Perplexity
        API base URL.

        Args:
            messages (list): The chat messages to send to Perplexity.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the Perplexity chat completions endpoint.

        Args:
            messages (list): The chat messages to send to Perplexity.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'PerplexityLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``perplexity_llm.yaml.example`` with a missing
        ``PERPLEXITY_API_KEY`` / ``PERPLEXITY_PROXY`` would otherwise
        assign ``''`` over the class defaults. That is worse than it sounds:
        the OpenAI client only rejects a *missing* key, so an empty key is
        silently sent upstream and surfaces as an opaque 401, and an empty
        ``api_base`` makes the client fall back to
        ``https://api.openai.com/v1`` — sending Perplexity credentials to
        the wrong endpoint. Normalizing the empty values here makes an
        unset variable behave exactly like an omitted key: ``api_key`` /
        ``proxy`` fall back to ``None`` and ``api_base`` to the Perplexity
        endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            PerplexityLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("PERPLEXITY_API_BASE") or \
                "https://api.perplexity.ai"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Sonar model.

        The combined length of the input prompt and the generated
        completion must fit within this window. The value is resolved in
        the following order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name is looked up in
           :data:`PERPLEXITY_MAX_CONTEXT_LENGTH`. Perplexity publishes
           both offline and ``<modelname>-online`` flavours of the Sonar
           models, so a trailing ``-online`` suffix is stripped before
           the second lookup attempt.
        3. As a last resort :data:`PERPLEXITY_DEFAULT_CONTEXT_LENGTH` is
           returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        if self.model_name in PERPLEXITY_MAX_CONTEXT_LENGTH:
            return PERPLEXITY_MAX_CONTEXT_LENGTH[self.model_name]
        if self.model_name and self.model_name.endswith('-online'):
            base_name = self.model_name[:-len('-online')]
            if base_name in PERPLEXITY_MAX_CONTEXT_LENGTH:
                return PERPLEXITY_MAX_CONTEXT_LENGTH[base_name]
        return PERPLEXITY_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Sonar models use their own tokenizer, which is not registered in
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
            # Sonar models are not registered in tiktoken by name;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
