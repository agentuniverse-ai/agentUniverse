# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 15:00
# @Author  : agentuniverse
# @FileName: siliconflow_llm.py

"""
SiliconFlow LLM.

SiliconFlow (https://siliconflow.cn, international site
https://siliconflow.com) is a Chinese **model-aggregation cloud platform**
that hosts third-party open-source large language models — DeepSeek
(``deepseek-ai/DeepSeek-V3``, ``deepseek-ai/DeepSeek-R1``), Alibaba's Qwen
family (``Qwen/Qwen2.5-72B-Instruct``, ...) and Zhipu's GLM open-weight
releases (``THUDM/glm-4-9b-chat``), among many others — behind one unified
billing and one unified API.

SiliconFlow exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.siliconflow.cn/v1``. Because of that compatibility this
component simply extends :class:`OpenAIStyleLLM` and only needs to wire up
the correct default environment variables, the SiliconFlow API base URL and
a per-model maximum context-length table. Streaming, tool calling, the
async interface and the Langchain bridge are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# Indicative maximum context length (input + output tokens) for common
# models currently hosted on the SiliconFlow platform. The values are
# conservative snapshots of the vendors' documentation / the SiliconFlow
# model cards; SiliconFlow rotates its catalogue frequently and the window
# of a given model can change with the serving deployment, so treat this
# table as *indicative*, not authoritative. When SiliconFlow adds a model
# it is sufficient to add an entry here, the rest of the component keeps
# working unchanged.
SILICONFLOW_MAX_CONTEXT_LENGTH = {
    # ---- DeepSeek reasoning / chat models ----
    "deepseek-ai/DeepSeek-V3": 65536,
    "deepseek-ai/DeepSeek-R1": 65536,
    # ---- Alibaba Qwen instruct models ----
    "Qwen/Qwen2.5-72B-Instruct": 32768,
    "Qwen/Qwen2.5-7B-Instruct": 32768,
    # ---- Zhipu GLM open-weight chat model ----
    "THUDM/glm-4-9b-chat": 131072,
}

# Sensible default context length returned for models that are not yet
# listed in the table above (SiliconFlow hosts hundreds of third-party
# models, most of them not listed). A conservative 8k window keeps
# prompt-budget checks on the safe side for freshly added or dated /
# quantized variants (``:free``, ``-250528``, ...) of known models too.
SILICONFLOW_DEFAULT_CONTEXT_LENGTH = 8192


class SiliconFlowLLM(OpenAIStyleLLM):
    """SiliconFlow LLM, an OpenAI-compatible wrapper around the SiliconFlow
    model-aggregation API.

    SiliconFlow serves a large catalogue of third-party open-source models
    (DeepSeek, Qwen, GLM, ...) through an API that is fully
    OpenAI-compatible. Therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: SiliconFlow API key. Loaded from the ``SILICONFLOW_API_KEY``
            environment variable when not provided explicitly. Create one at
            https://cloud.siliconflow.cn.
        api_base: SiliconFlow OpenAI-compatible API base URL. Defaults to
            ``https://api.siliconflow.cn/v1`` unless overridden through the
            ``SILICONFLOW_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SILICONFLOW_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("SILICONFLOW_API_BASE") or
                                    "https://api.siliconflow.cn/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("SILICONFLOW_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the SiliconFlow chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the SiliconFlow
        API base URL.

        Args:
            messages (list): The chat messages to send to SiliconFlow.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the SiliconFlow chat completions endpoint.

        Args:
            messages (list): The chat messages to send to SiliconFlow.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'SiliconFlowLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied
        ``siliconflow_llm.yaml.example`` with a missing
        ``SILICONFLOW_API_KEY`` / ``SILICONFLOW_PROXY`` would otherwise
        assign ``''`` over the class defaults. That is worse than it sounds:
        the OpenAI client only rejects a *missing* key, so an empty key is
        silently sent upstream and surfaces as an opaque 401, and an empty
        ``api_base`` makes the client fall back to
        ``https://api.openai.com/v1`` — sending SiliconFlow credentials to
        the wrong endpoint. Normalizing the empty values here makes an unset
        variable behave exactly like an omitted key: ``api_key`` / ``proxy``
        fall back to ``None`` and ``api_base`` to the SiliconFlow endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            SiliconFlowLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("SILICONFLOW_API_BASE") or \
                "https://api.siliconflow.cn/v1"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured hosted model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name is looked up in
           :data:`SILICONFLOW_MAX_CONTEXT_LENGTH`.
        3. As a last resort :data:`SILICONFLOW_DEFAULT_CONTEXT_LENGTH` is
           returned, because SiliconFlow hosts hundreds of third-party
           models and the table above only covers the common ones.
        """
        if super().max_context_length():
            return super().max_context_length()
        if self.model_name in SILICONFLOW_MAX_CONTEXT_LENGTH:
            return SILICONFLOW_MAX_CONTEXT_LENGTH[self.model_name]
        return SILICONFLOW_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        The models hosted on SiliconFlow (DeepSeek, Qwen, GLM, ...) each use
        their own vendor tokenizer, which is not registered in ``tiktoken``
        by the namespaced SiliconFlow model id, so we fall back to the
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
            # Namespaced SiliconFlow model ids (e.g. Qwen/Qwen2.5-7B-Instruct)
            # are not registered in tiktoken by name; cl100k_base is a
            # robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
