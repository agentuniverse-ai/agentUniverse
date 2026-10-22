# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 14:00
# @Author  : agentuniverse
# @FileName: internlm_llm.py

"""
InternLM (书生·浦语) LLM.

InternLM (https://internlm.intern-ai.org.cn) is the family of open-source
large language models developed by **Shanghai AI Laboratory** (上海人工智能实
验室). The series spans the tool-calling InternLM3 generation, the InternLM2.5
line with strong reasoning and long-context capabilities (internlm2.5-latest,
internlm2.5-20b-chat) and the earlier InternLM2 releases, all with bilingual
Chinese/English strength.

The official InternLM platform (https://intern-ai.org.cn) exposes a fully
**OpenAI-compatible** Chat Completions API at
``https://internlm-chat.intern-ai.org.cn/paas/v4``. Because of that
compatibility this component simply extends :class:`OpenAIStyleLLM` and only
needs to wire up the correct default environment variables, the InternLM API
base URL and the per-model maximum context-length table. Streaming, tool
calling, the async interface and the Langchain bridge are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by the models
# currently served on the InternLM platform. The values are indicative and
# sourced from the official InternLM model documentation
# (https://internlm.intern-ai.org.cn / https://huggingface.co/internlm):
# InternLM3 expands the window to 128K (131072 tokens) while the InternLM2.5
# generation keeps 32K (32768 tokens). When Shanghai AI Laboratory ships a new
# model it is sufficient to add an entry here, the rest of the component keeps
# working unchanged.
INTERNLM_MAX_CONTEXT_LENGTH = {
    # ---- InternLM3 generation (128K long-context) ----
    "internlm3-latest": 131072,
    # ---- InternLM2.5 generation (32K context) ----
    "internlm2.5-latest": 32768,
    "internlm2.5-20b-chat": 32768,
}

# Sensible default context length returned for models that are not yet listed
# in the table above. A conservative 8k window keeps prompt-budget checks on
# the safe side for freshly announced InternLM models, dated releases and
# aliases whose base entry cannot be resolved.
INTERNLM_DEFAULT_CONTEXT_LENGTH = 8192


class InternLMChatLLM(OpenAIStyleLLM):
    """InternLM LLM, an OpenAI-compatible wrapper around the InternLM API.

    Shanghai AI Laboratory serves its InternLM family of models
    (internlm3-latest, internlm2.5-latest, internlm2.5-20b-chat, ...) through
    an API that is fully OpenAI-compatible. Therefore this class only
    customises the credential/base-url plumbing and the model context-length
    lookup table while inheriting the complete request, streaming and
    langchain-bridge implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: InternLM platform API key. Loaded from the ``INTERNLM_API_KEY``
            environment variable when not provided explicitly. Create one at
            https://intern-ai.org.cn/apiManage.
        api_base: InternLM OpenAI-compatible API base URL. Defaults to
            ``https://internlm-chat.intern-ai.org.cn/paas/v4`` unless
            overridden through the ``INTERNLM_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("INTERNLM_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("INTERNLM_API_BASE") or
                                    "https://internlm-chat.intern-ai.org.cn/paas/v4")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("INTERNLM_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the InternLM chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the InternLM API
        base URL.

        Args:
            messages (list): The chat messages to send to InternLM.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the InternLM chat completions endpoint.

        Args:
            messages (list): The chat messages to send to InternLM.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'InternLMChatLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied ``internlm_llm.yaml.example``
        with a missing ``INTERNLM_API_KEY`` / ``INTERNLM_PROXY`` would otherwise
        assign ``''`` over the class defaults. That is worse than it sounds:
        the OpenAI client only rejects a *missing* key, so an empty key is
        silently sent upstream and surfaces as an opaque 401, and an empty
        ``api_base`` makes the client fall back to
        ``https://api.openai.com/v1`` — sending the InternLM platform key to
        the wrong endpoint. Normalizing the empty values here makes an unset
        variable behave exactly like an omitted key: ``api_key`` / ``proxy``
        fall back to ``None`` and ``api_base`` to the InternLM endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            InternLMChatLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("INTERNLM_API_BASE") or \
                "https://internlm-chat.intern-ai.org.cn/paas/v4"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured InternLM model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field, stored in the
           private ``_max_context_length`` attribute inherited from the
           LLM base class) that value wins.
        2. Otherwise the model name is looked up in the indicative
           :data:`INTERNLM_MAX_CONTEXT_LENGTH` table.
        3. As a last resort the conservative
           :data:`INTERNLM_DEFAULT_CONTEXT_LENGTH` of 8192 tokens is
           returned, which keeps budget checks safe for not yet listed
           models.

        Note that ``OpenAIStyleLLM`` itself always resolves to an int
        (falling back to its OpenAI table and a 4096 default), so consulting
        ``super()`` first would silently shadow the InternLM-specific lookup
        below; the explicit ``_max_context_length`` check keeps the
        precedence InternLM-specific while preserving the
        explicit-configuration-wins contract.
        """
        if self._max_context_length:
            return self._max_context_length
        if self.model_name in INTERNLM_MAX_CONTEXT_LENGTH:
            return INTERNLM_MAX_CONTEXT_LENGTH[self.model_name]
        return INTERNLM_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        InternLM models use their own tokenizer, which is not registered in
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
            # InternLM models are not registered in tiktoken by name;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
