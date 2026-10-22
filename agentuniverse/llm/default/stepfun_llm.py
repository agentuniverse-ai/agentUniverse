# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 00:00
# @Author  : agentuniverse
# @FileName: stepfun_llm.py

"""
StepFun (阶跃星辰) LLM.

StepFun (https://www.stepfun.com) is a Chinese large model company whose
**Step** model family covers the full spectrum from the flagship text model
``step-2-16k`` over the multimodal vision-language models ``step-1v-8k`` and
``step-1o-turbo-vision`` to the general-purpose ``step-1-8k``.

StepFun exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.stepfun.com/v1``. Because of that compatibility this component
simply extends :class:`OpenAIStyleLLM` and only needs to wire up the correct
default environment variables, the StepFun API base URL and the per-model
maximum context-length table. Streaming, tool calling, the async interface
and the Langchain bridge are inherited unchanged.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# Indicative maximum context length (input + output tokens) for the models
# currently available on the StepFun API. The values follow the model naming
# convention (``step-2-16k`` offers a 16k window, ``step-1-8k`` /
# ``step-1v-8k`` an 8k window) and the StepFun platform documentation for the
# ``step-1o-turbo-vision`` multimodal model (32k window). Because StepFun
# keeps releasing new models, the table is indicative rather than exhaustive:
# any model that is not listed falls back to a conservative 8192-token window
# (see STEPFUN_DEFAULT_CONTEXT_LENGTH), and users can always state the exact
# limit explicitly through the ``max_context_length`` YAML field. When
# StepFun ships a new model it is sufficient to add an entry here, the rest
# of the component keeps working unchanged.
STEPFUN_MAX_CONTEXT_LENGTH = {
    # ---- Flagship text model ----
    "step-2-16k": 16384,
    # ---- Multimodal vision-language models ----
    "step-1v-8k": 8192,
    "step-1o-turbo-vision": 32768,
    # ---- General-purpose model ----
    "step-1-8k": 8192,
}

# Conservative default context length returned for models that are not
# listed in the table above. Freshly announced or aliased models can have
# very different windows, so a small 8k default keeps prompt-budget checks
# on the safe side until an explicit ``max_context_length`` is configured or
# a table entry is added.
STEPFUN_DEFAULT_CONTEXT_LENGTH = 8192


class StepFunLLM(OpenAIStyleLLM):
    """StepFun (阶跃星辰) LLM, an OpenAI-compatible wrapper around the StepFun API.

    StepFun serves its Step model family (the flagship ``step-2-16k``, the
    multimodal ``step-1v-8k`` and ``step-1o-turbo-vision`` and the
    general-purpose ``step-1-8k``) through an API that is fully
    OpenAI-compatible. Therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: StepFun API key. Loaded from the ``STEPFUN_API_KEY``
            environment variable when not provided explicitly. Create one at
            https://platform.stepfun.com.
        api_base: StepFun OpenAI-compatible API base URL. Defaults to
            ``https://api.stepfun.com/v1`` unless overridden through the
            ``STEPFUN_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("STEPFUN_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("STEPFUN_API_BASE") or
                                    "https://api.stepfun.com/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("STEPFUN_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the StepFun chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the StepFun API
        base URL.

        Args:
            messages (list): The chat messages to send to StepFun.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the StepFun chat completions endpoint.

        Args:
            messages (list): The chat messages to send to StepFun.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'StepFunLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied ``stepfun_llm.yaml.example``
        with a missing ``STEPFUN_API_KEY`` / ``STEPFUN_PROXY`` would otherwise
        assign ``''`` over the class defaults. That is worse than it sounds:
        the OpenAI client only rejects a *missing* key, so an empty key is
        silently sent upstream and surfaces as an opaque 401, and an empty
        ``api_base`` makes the client fall back to
        ``https://api.openai.com/v1`` — sending the StepFun credentials to
        the wrong endpoint. Normalizing the empty values here makes an unset
        variable behave exactly like an omitted key: ``api_key`` / ``proxy``
        fall back to ``None`` and ``api_base`` to the StepFun endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            StepFunLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("STEPFUN_API_BASE") or \
                "https://api.stepfun.com/v1"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured StepFun model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field, stored in the
           private ``_max_context_length`` attribute inherited from the
           LLM base class) that value wins.
        2. Otherwise the model name is looked up in the indicative
           :data:`STEPFUN_MAX_CONTEXT_LENGTH` table.
        3. As a last resort the conservative
           :data:`STEPFUN_DEFAULT_CONTEXT_LENGTH` of 8192 tokens is
           returned, which keeps budget checks safe for freshly announced
           and not yet listed models.

        Note that unlike earlier releases ``OpenAIStyleLLM`` itself now
        always resolves to an int (falling back to its OpenAI table and a
        4096 default), so consulting ``super()`` first would silently shadow
        the StepFun-specific lookup below; the explicit
        ``_max_context_length`` check keeps the precedence StepFun-specific
        while preserving the explicit-configuration-wins contract.
        """
        if self._max_context_length:
            return self._max_context_length
        if self.model_name in STEPFUN_MAX_CONTEXT_LENGTH:
            return STEPFUN_MAX_CONTEXT_LENGTH[self.model_name]
        return STEPFUN_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Step models use StepFun's own tokenizer, which is not registered in
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
            # Step models are not registered in tiktoken by name;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
