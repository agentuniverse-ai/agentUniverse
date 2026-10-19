# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: hunyuan_llm.py

"""
Tencent Hunyuan LLM.

Tencent **Hunyuan** (混元, https://hunyuan.tencent.com) is Tencent's
family of large language models, covering deep-thinking reasoning models
(the T1 series), fast-thinking flagship models (the TurboS series), the
Hy3 generation Mixture-of-Experts models and long-running workhorses such
as hunyuan-lite / hunyuan-standard / hunyuan-large.

Hunyuan exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.hunyuan.cloud.tencent.com/v1`` (served through Tencent
Cloud's TokenHub gateway). Because of that compatibility this component
simply extends :class:`OpenAIStyleLLM` and only needs to wire up the
correct default environment variables, the Hunyuan API base URL and the
per-model maximum context-length table. Streaming, tool calling, the
async interface and the Langchain bridge are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by the
# models currently available on the Hunyuan OpenAI-compatible API. The
# values follow the official Tencent Cloud documentation and technical
# reports: the TurboS architecture supports up to 256K tokens
# (https://arxiv.org/abs/2505.15431), hunyuan-a13b and the 256K variants
# expose a 262144-token window, while the T1 deep-thinking series and the
# base standard/large windows are 32K. Hunyuan model identifiers are
# matched case-insensitively because Tencent documents the 256K variants
# with a capital ``K`` suffix (``hunyuan-standard-256K``). When Tencent
# ships a new model it is sufficient to add an entry here, the rest of
# the component keeps working unchanged.
HUNYUAN_MAX_CONTEXT_LENGTH = {
    # ---- Deep-thinking reasoning models (T1 series) ----
    "hunyuan-t1": 32768,
    "hunyuan-t1-latest": 32768,
    # ---- Fast-thinking flagship models (TurboS series) ----
    "hunyuan-turbos": 32768,
    "hunyuan-turbos-latest": 262144,
    "hunyuan-turbos-20250630": 262144,
    # ---- Hy3 generation MoE models ----
    "hy3": 262144,
    # ---- Open-source MoE series ----
    "hunyuan-a13b": 262144,
    # ---- Long-running base models ----
    "hunyuan-lite": 262144,
    "hunyuan-standard": 32768,
    "hunyuan-standard-256k": 262144,
    "hunyuan-large": 32768,
    "hunyuan-large-longcontext": 262144,
}

# Sensible default context length returned for models that are not yet
# listed in the table above. A conservative 32k window matches the
# smallest context commonly enforced across the Hunyuan lineup and keeps
# prompt-budget checks on the safe side for freshly announced models.
HUNYUAN_DEFAULT_CONTEXT_LENGTH = 32768


class HunyuanLLM(OpenAIStyleLLM):
    """Tencent Hunyuan LLM, an OpenAI-compatible wrapper around the Hunyuan API.

    Tencent serves its Hunyuan family of models (the T1 deep-thinking
    series, the TurboS fast-thinking flagships, the Hy3 MoE generation and
    the lite/standard/large workhorses) through an API that is fully
    OpenAI-compatible. Therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Hunyuan API key. Loaded from the ``HUNYUAN_API_KEY``
            environment variable when not provided explicitly. Create one
            in the Tencent Cloud console at
            https://console.cloud.tencent.com/hunyuan/api-key.
        api_base: Hunyuan OpenAI-compatible API base URL. Defaults to
            ``https://api.hunyuan.cloud.tencent.com/v1`` unless overridden
            through the ``HUNYUAN_API_BASE`` environment variable (e.g. to
            point the component at the international TokenHub endpoint).
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("HUNYUAN_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("HUNYUAN_API_BASE") or
                                    "https://api.hunyuan.cloud.tencent.com/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("HUNYUAN_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the Hunyuan chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the Hunyuan
        API base URL.

        Args:
            messages (list): The chat messages to send to Hunyuan.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the Hunyuan chat completions endpoint.

        Args:
            messages (list): The chat messages to send to Hunyuan.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'HunyuanLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied ``hunyuan_llm.yaml.example``
        with a missing ``HUNYUAN_API_KEY`` / ``HUNYUAN_PROXY`` would
        otherwise assign ``''`` over the class defaults. That is worse than
        it sounds: the OpenAI client only rejects a *missing* key, so an
        empty key is silently sent upstream and surfaces as an opaque 401,
        and an empty ``api_base`` makes the client fall back to
        ``https://api.openai.com/v1`` — sending Hunyuan credentials to the
        wrong endpoint. Normalizing the empty values here makes an unset
        variable behave exactly like an omitted key: ``api_key`` /
        ``proxy`` fall back to ``None`` and ``api_base`` to the Hunyuan
        endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            HunyuanLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("HUNYUAN_API_BASE") or \
                "https://api.hunyuan.cloud.tencent.com/v1"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Hunyuan model.

        The combined length of the input prompt and the generated
        completion must fit within this window. The value is resolved in
        the following order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name is looked up (case-insensitively, so
           the documented ``hunyuan-standard-256K`` capitalisation also
           resolves) in :data:`HUNYUAN_MAX_CONTEXT_LENGTH`.
        3. If the model carries a ``-latest`` suffix that is not itself a
           table entry, the suffix is stripped and the base name is looked
           up as well.
        4. As a last resort :data:`HUNYUAN_DEFAULT_CONTEXT_LENGTH` is
           returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        if self.model_name:
            model_name = self.model_name.lower()
            if model_name in HUNYUAN_MAX_CONTEXT_LENGTH:
                return HUNYUAN_MAX_CONTEXT_LENGTH[model_name]
            if model_name.endswith('-latest'):
                base_name = model_name[:-len('-latest')]
                if base_name in HUNYUAN_MAX_CONTEXT_LENGTH:
                    return HUNYUAN_MAX_CONTEXT_LENGTH[base_name]
        return HUNYUAN_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Hunyuan models use Tencent's own tokenizer, which is not
        registered in ``tiktoken`` by model name, so we fall back to the
        widely used ``cl100k_base`` encoding which gives a good
        approximation suitable for budget/prompt-window checks.

        Args:
            text: The raw string to tokenize.

        Returns:
            The integer number of tokens the text would be encoded into.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # Hunyuan models are not registered in tiktoken by name;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
