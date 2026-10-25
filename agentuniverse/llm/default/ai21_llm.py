# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 16:00
# @Author  : agentuniverse
# @FileName: ai21_llm.py

"""
AI21 Labs (Jamba) LLM.

AI21 Labs (https://www.ai21.com) is the company behind the **Jamba** family
of large language models. Jamba models are built on a hybrid
SSM-Transformer architecture (Mamba + Transformer + MoE) which lets them
serve very long contexts at a fraction of the memory a pure Transformer
needs. The current line-up covers the Jamba 1.5 generation
(``jamba-1.5-mini`` / ``jamba-1.5-large``) and the Jamba 1.6 generation
(``jamba-mini-1.6`` / ``jamba-large-1.6``), all with a 256k-token context
window.

AI21 exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.ai21.com/studio/v1``. Because of that compatibility this
component simply extends :class:`OpenAIStyleLLM` and only needs to wire up
the correct default environment variables, the AI21 API base URL and the
per-model maximum context-length table. Streaming, tool calling, the async
interface and the Langchain bridge are inherited unchanged.
"""

import re
from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by the models
# currently available on the AI21 API. The values are sourced from the
# official AI21 models documentation (https://docs.ai21.com/jamba/model
# specifications) and are indicative: every Jamba 1.5 and Jamba 1.6 model
# advertises a 256k-token context window (256000 following AI21's decimal
# convention). When AI21 ships a new model it is sufficient to add an entry
# here, the rest of the component keeps working unchanged.
AI21_MAX_CONTEXT_LENGTH = {
    # ---- Jamba 1.5 generation (hybrid SSM-Transformer, MoE) ----
    "jamba-1.5-mini": 256000,
    "jamba-1.5-large": 256000,
    # ---- Jamba 1.6 generation ----
    "jamba-mini-1.6": 256000,
    "jamba-large-1.6": 256000,
}

# Sensible default context length returned for models that are not yet listed
# in the table above. A conservative 8k window keeps prompt-budget checks on
# the safe side for freshly announced Jamba models and dated or aliased
# releases whose base entry cannot be resolved.
AI21_DEFAULT_CONTEXT_LENGTH = 8192

# AI21 publishes dated snapshot ids for every release, e.g.
# ``jamba-mini-1.6-20250310`` or ``jamba-1.5-mini-20250812``. The trailing
# ``-YYYYMMDD`` segment is stripped before the second lookup attempt so such
# snapshots resolve to the base model's context window.
_AI21_DATE_SUFFIX_RE = re.compile(r"-\d{8}$")


class AI21LLM(OpenAIStyleLLM):
    """AI21 Jamba LLM, an OpenAI-compatible wrapper around the AI21 API.

    AI21 serves its Jamba family of models (jamba-1.5-mini/large and
    jamba-mini/large-1.6) through an API that is fully OpenAI-compatible.
    Therefore this class only customises the credential/base-url plumbing
    and the model context-length lookup table while inheriting the complete
    request, streaming and langchain-bridge implementation from
    :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: AI21 API key. Loaded from the ``AI21_API_KEY`` environment
            variable when not provided explicitly. Create one at
            https://platform.ai21.com.
        api_base: AI21 OpenAI-compatible API base URL. Defaults to
            ``https://api.ai21.com/studio/v1`` unless overridden through the
            ``AI21_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("AI21_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("AI21_API_BASE") or
                                    "https://api.ai21.com/studio/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("AI21_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the AI21 chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the AI21 API
        base URL.

        Args:
            messages (list): The chat messages to send to AI21.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the AI21 chat completions endpoint.

        Args:
            messages (list): The chat messages to send to AI21.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'AI21LLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied ``ai21_llm.yaml.example``
        with a missing ``AI21_API_KEY`` / ``AI21_PROXY`` would otherwise
        assign ``''`` over the class defaults. That is worse than it sounds:
        the OpenAI client only rejects a *missing* key, so an empty key is
        silently sent upstream and surfaces as an opaque 401, and an empty
        ``api_base`` makes the client fall back to ``https://api.openai.com/v1``
        — sending AI21 credentials to the wrong endpoint. Normalizing the
        empty values here makes an unset variable behave exactly like an
        omitted key: ``api_key`` / ``proxy`` fall back to ``None`` and
        ``api_base`` to the AI21 endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            AI21LLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("AI21_API_BASE") or \
                "https://api.ai21.com/studio/v1"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Jamba model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name is looked up in
           :data:`AI21_MAX_CONTEXT_LENGTH`. AI21 documents dated snapshot ids
           (``<modelname>-YYYYMMDD``) alongside the stable aliases, so a
           trailing ``-YYYYMMDD`` date suffix is stripped before the second
           lookup attempt.
        3. As a last resort :data:`AI21_DEFAULT_CONTEXT_LENGTH` is returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        if self.model_name in AI21_MAX_CONTEXT_LENGTH:
            return AI21_MAX_CONTEXT_LENGTH[self.model_name]
        if self.model_name:
            base_name = _AI21_DATE_SUFFIX_RE.sub('', self.model_name)
            if base_name != self.model_name and base_name in AI21_MAX_CONTEXT_LENGTH:
                return AI21_MAX_CONTEXT_LENGTH[base_name]
        return AI21_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Jamba models use AI21's own tokenizer, which is not registered in
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
            # Jamba models are not registered in tiktoken by name;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
