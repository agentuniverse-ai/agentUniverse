# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: novita_llm.py

"""
Novita AI LLM.

Novita AI (https://novita.ai) is a full-stack inference platform that serves
a broad catalogue of **open-weight** flagship models from many vendors under
a single pay-as-you-go API: Meta Llama
(meta-llama/llama-3.1-70b-instruct), DeepSeek (deepseek/deepseek_v3),
Qwen (qwen/qwen-2.5-32b-instruct) and Mistral (mistralai/mistral-nemo)
among others.

Novita exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.novita.ai/v3/openai``. Because of that compatibility this
component simply extends :class:`OpenAIStyleLLM` and only needs to wire up
the correct default environment variables, the Novita API base URL and the
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

# The maximum context length (input + output tokens) of the open models most
# commonly served through the Novita AI model API. The values below follow the
# official model cards and the Novita model pages: 128k (131072) for the
# Llama 3.1/3.2/3.3, DeepSeek-V3/R1 and Mistral Nemo families, while the
# Qwen2.5 deployments on Novita are served with their native 32k (32768)
# window. The table is *indicative*: Novita continuously adds and rotates
# models, so when a new model ships it is sufficient to add an entry here,
# the rest of the component keeps working unchanged.
NOVITA_MAX_CONTEXT_LENGTH = {
    # ---- Meta Llama family ----
    "meta-llama/llama-3.1-405b-instruct": 131072,
    "meta-llama/llama-3.1-70b-instruct": 131072,
    "meta-llama/llama-3.1-8b-instruct": 131072,
    "meta-llama/llama-3.3-70b-instruct": 131072,
    "meta-llama/llama-3.2-3b-instruct": 131072,
    # ---- DeepSeek family ----
    "deepseek/deepseek_v3": 131072,
    "deepseek/deepseek_r1": 131072,
    # ---- Qwen family ----
    "qwen/qwen-2.5-72b-instruct": 32768,
    "qwen/qwen-2.5-32b-instruct": 32768,
    # ---- Mistral family ----
    "mistralai/mistral-nemo": 131072,
}

# Sensible default context length returned for models that are not yet listed
# in the table above. A conservative 8k window keeps prompt-budget checks on
# the safe side for freshly announced models and for the smaller open models
# whose windows vary between deployments.
NOVITA_DEFAULT_CONTEXT_LENGTH = 8192


class NovitaLLM(OpenAIStyleLLM):
    """Novita AI LLM, an OpenAI-compatible wrapper around the Novita model API.

    Novita AI serves a large catalogue of open-weight models (Meta Llama,
    DeepSeek, Qwen, Mistral and others) through an API that is fully
    OpenAI-compatible. Therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Novita AI API key. Loaded from the ``NOVITA_API_KEY``
            environment variable when not provided explicitly. Create one in
            the Novita console at https://novita.ai/dashboard/keys.
        api_base: Novita OpenAI-compatible API base URL. Defaults to
            ``https://api.novita.ai/v3/openai`` unless overridden through
            the ``NOVITA_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("NOVITA_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("NOVITA_API_BASE") or
                                    "https://api.novita.ai/v3/openai")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("NOVITA_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the Novita chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the Novita API
        base URL.

        Args:
            messages (list): The chat messages to send to Novita.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the Novita chat completions endpoint.

        Args:
            messages (list): The chat messages to send to Novita.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'NovitaLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``novita_llm.yaml.example`` with a missing ``NOVITA_API_KEY`` /
        ``NOVITA_PROXY`` would otherwise assign ``''`` over the class
        defaults. That is worse than it sounds: the OpenAI client only
        rejects a *missing* key, so an empty key is silently sent upstream
        and surfaces as an opaque 401, and an empty ``api_base`` makes the
        client fall back to ``https://api.openai.com/v1`` — sending Novita
        credentials to the wrong endpoint. Normalizing the empty values here
        makes an unset variable behave exactly like an omitted key:
        ``api_key`` / ``proxy`` fall back to ``None`` and ``api_base`` to
        the Novita endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            NovitaLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("NOVITA_API_BASE") or \
                "https://api.novita.ai/v3/openai"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field, stored in the
           inherited ``_max_context_length`` attribute) that value wins.
        2. Otherwise the model name (Novita uses the lowercase
           ``organization/model`` identifier, e.g.
           ``meta-llama/llama-3.1-70b-instruct``) is looked up in
           :data:`NOVITA_MAX_CONTEXT_LENGTH`.
        3. As a last resort :data:`NOVITA_DEFAULT_CONTEXT_LENGTH` is
           returned.

        Note that the OpenAI-style parent implements its own fallback that
        consults the OpenAI model table with a 4096 default. It is
        deliberately bypassed here: Novita serves open models whose
        identifiers never appear in the OpenAI table, so the last two steps
        above provide the authoritative values for this endpoint.
        """
        if self._max_context_length:
            return self._max_context_length
        if self.model_name in NOVITA_MAX_CONTEXT_LENGTH:
            return NOVITA_MAX_CONTEXT_LENGTH[self.model_name]
        return NOVITA_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        The open models served by Novita use their own tokenizers (Llama 3,
        DeepSeek, Qwen2.5, Mistral NeMo ...), none of which are registered
        in ``tiktoken`` by the lowercase ``organization/model`` names used
        by the API, so we fall back to the widely used ``cl100k_base``
        encoding which gives a good approximation suitable for
        budget/prompt-window checks.

        Args:
            text: The raw string to tokenize.

        Returns:
            The integer number of tokens the text would be encoded into.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # The organization/model names are not registered in tiktoken;
            # cl100k_base is a robust generic fallback for the open models
            # served on Novita.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
