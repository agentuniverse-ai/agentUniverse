# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: fireworks_llm.py

"""
Fireworks AI LLM.

`Fireworks AI <https://fireworks.ai>`_ is an inference platform that hosts a
large catalogue of open-weight and fine-tuned large language models (Meta
Llama 3.x, Mistral Mixtral, DeepSeek and many community fine-tunes) on
managed GPU infrastructure, with a focus on low-latency, high-throughput
token generation. Models are addressed by their full serverless identifier,
e.g. ``accounts/fireworks/models/llama-v3p1-70b-instruct``.

Fireworks exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.fireworks.ai/inference/v1``. Because of that compatibility this
component simply extends :class:`OpenAIStyleLLM` and only needs to wire up
the correct default environment variables, the Fireworks API base URL and
the per-model maximum context-length table. Streaming, tool calling, the
async interface and the Langchain bridge are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by popular
# models available on the Fireworks serverless API. The values are sourced
# from the official Fireworks models documentation
# (https://fireworks.ai/models) and are indicative: Fireworks continuously
# adds new models and may bump the windows of existing ones. When Fireworks
# ships a new model it is sufficient to add an entry here, the rest of the
# component keeps working unchanged.
FIREWORKS_MAX_CONTEXT_LENGTH = {
    # ---- Meta Llama 3.1 family (128k context) ----
    "accounts/fireworks/models/llama-v3p1-405b-instruct": 131072,
    "accounts/fireworks/models/llama-v3p1-70b-instruct": 131072,
    "accounts/fireworks/models/llama-v3p1-8b-instruct": 131072,
    # ---- Mistral Mixtral (32k context) ----
    "accounts/fireworks/models/mixtral-8x7b-instruct": 32768,
    # ---- DeepSeek (128k context) ----
    "accounts/fireworks/models/deepseek-v3": 131072,
}

# The same table keyed by the bare model id (the part after the
# ``accounts/<account>/models/`` prefix). Fireworks also serves fine-tuned
# deployments under user accounts (``accounts/<your-account>/models/<id>``),
# so the context window of a known base model can be resolved even when it
# is hosted under a different account.
FIREWORKS_BARE_MODEL_CONTEXT_LENGTH = {
    key.split('/models/', 1)[1]: value
    for key, value in FIREWORKS_MAX_CONTEXT_LENGTH.items()
    if key.startswith('accounts/') and '/models/' in key
}

# Sensible default context length returned for models that are not yet listed
# in the table above. A conservative 8k window keeps prompt-budget checks on
# the safe side for freshly announced models, dated releases and user-hosted
# fine-tunes whose base entry cannot be resolved.
FIREWORKS_DEFAULT_CONTEXT_LENGTH = 8192


class FireworksLLM(OpenAIStyleLLM):
    """Fireworks AI LLM, an OpenAI-compatible wrapper around the Fireworks API.

    Fireworks serves its model catalogue through an API that is fully
    OpenAI-compatible. Therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Fireworks API key. Loaded from the ``FIREWORKS_API_KEY``
            environment variable when not provided explicitly. Create one at
            https://fireworks.ai/account/api-keys.
        api_base: Fireworks OpenAI-compatible API base URL. Defaults to
            ``https://api.fireworks.ai/inference/v1`` unless overridden
            through the ``FIREWORKS_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("FIREWORKS_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("FIREWORKS_API_BASE") or
                                    "https://api.fireworks.ai/inference/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("FIREWORKS_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the Fireworks chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the Fireworks
        API base URL.

        Args:
            messages (list): The chat messages to send to Fireworks.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the Fireworks chat completions endpoint.

        Args:
            messages (list): The chat messages to send to Fireworks.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'FireworksLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``fireworks_llm.yaml.example`` with a missing ``FIREWORKS_API_KEY``
        / ``FIREWORKS_PROXY`` would otherwise assign ``''`` over the class
        defaults. That is worse than it sounds: the OpenAI client only
        rejects a *missing* key, so an empty key is silently sent upstream
        and surfaces as an opaque 401, and an empty ``api_base`` makes the
        client fall back to ``https://api.openai.com/v1`` — sending Fireworks
        credentials to the wrong endpoint. Normalizing the empty values here
        makes an unset variable behave exactly like an omitted key:
        ``api_key`` / ``proxy`` fall back to ``None`` and ``api_base`` to
        the Fireworks endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            FireworksLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("FIREWORKS_API_BASE") or \
                "https://api.fireworks.ai/inference/v1"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Fireworks model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the full model identifier (e.g.
           ``accounts/fireworks/models/llama-v3p1-70b-instruct``) is looked
           up in :data:`FIREWORKS_MAX_CONTEXT_LENGTH`.
        3. Fireworks also serves fine-tuned models under user accounts
           (``accounts/<your-account>/models/<base-model>``), so the bare
           model id after the ``accounts/<account>/models/`` prefix is
           looked up in :data:`FIREWORKS_BARE_MODEL_CONTEXT_LENGTH`.
        4. As a last resort :data:`FIREWORKS_DEFAULT_CONTEXT_LENGTH` is
           returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        if self.model_name in FIREWORKS_MAX_CONTEXT_LENGTH:
            return FIREWORKS_MAX_CONTEXT_LENGTH[self.model_name]
        if self.model_name and self.model_name.startswith('accounts/') \
                and '/models/' in self.model_name:
            base_name = self.model_name.split('/models/', 1)[1]
            if base_name in FIREWORKS_BARE_MODEL_CONTEXT_LENGTH:
                return FIREWORKS_BARE_MODEL_CONTEXT_LENGTH[base_name]
        return FIREWORKS_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Fireworks models use their own tokenizers (Llama 3 / Mixtral /
        DeepSeek families), which are not registered in ``tiktoken`` by
        model name, so we fall back to the widely used ``cl100k_base``
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
            # Fireworks model identifiers (accounts/.../models/...) are not
            # registered in tiktoken by name; cl100k_base is a robust
            # generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
