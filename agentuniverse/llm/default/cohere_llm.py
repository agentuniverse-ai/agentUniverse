# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19 20:00
# @Author  : agentuniverse
# @FileName: cohere_llm.py

"""
Cohere LLM.

Cohere (https://cohere.com) is the enterprise-LLM company behind the
**Command** family of large language models. The portfolio spans the
flagship **command-a** generation (command-a-03-2025), the workhorse
**command-r-plus** and **command-r** retrieval-augmented models, and the
cost-efficient **command-r7b** variant - all with a strong focus on
agentic workflows, tool use and multilingual RAG.

Cohere exposes a fully **OpenAI-compatible** Chat Completions API at
``https://api.cohere.com/compatibility/v1``. Because of that
compatibility this component simply extends :class:`OpenAIStyleLLM` and
only needs to wire up the correct default environment variables, the
Cohere compatibility API base URL and the per-model maximum
context-length table. Streaming, tool calling, the async interface and
the Langchain bridge are inherited unchanged.

Note: this endpoint is the OpenAI-style *compatibility* surface of Cohere
and is intentionally independent from the native Cohere platform API
(e.g. the one used by the Cohere rerank document processor). The
``COHERE_API_BASE`` variable configured here only affects this LLM
component.
"""

import re
from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by the chat
# models currently available on the Cohere compatibility API. The values are
# indicative and sourced from the official Cohere docs (docs.cohere.com,
# "Models" page): the command-a generation ships a 256k-token context window
# while the command-r generation models (command-r-plus, command-r and the
# command-r7b variant) each support 128k tokens. Cohere also publishes dated
# releases of the same families (e.g. command-r-plus-08-2024,
# command-r7b-12-2024); a trailing ``-(m)m-yyyy`` date suffix is resolved to
# the base family entry by :meth:`CohereLLM.max_context_length`, so a dated
# variant does not need its own row here. When Cohere ships a new model it is
# sufficient to add an entry to this table, the rest of the component keeps
# working unchanged.
COHERE_MAX_CONTEXT_LENGTH = {
    # ---- Flagship command-a generation ----
    "command-a-03-2025": 256000,
    # ---- command-r generation ----
    "command-r-plus": 128000,
    "command-r": 128000,
    "command-r7b": 128000,
}

# Sensible default context length returned for models that are not yet listed
# in the table above. A conservative 8k window keeps prompt-budget checks on
# the safe side for freshly announced Cohere models, preview aliases and
# experimental checkpoints whose base entry cannot be resolved.
COHERE_DEFAULT_CONTEXT_LENGTH = 8192

# Cohere's dated release convention: ``<family>-<month>-<year>`` (e.g.
# command-r-plus-08-2024, command-a-03-2025). Used to strip the suffix and
# retry the lookup with the base family name.
_COHERE_DATED_SUFFIX_RE = re.compile(r'-\d{2}-\d{4}$')


class CohereLLM(OpenAIStyleLLM):
    """Cohere LLM, an OpenAI-compatible wrapper around the Cohere API.

    Cohere serves its Command family of chat models (command-a-03-2025,
    command-r-plus, command-r and command-r7b) through an OpenAI-compatible
    Chat Completions endpoint. Therefore this class only customises the
    credential/base-url plumbing and the model context-length lookup table
    while inheriting the complete request, streaming and langchain-bridge
    implementation from :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Cohere API key. Loaded from the ``COHERE_API_KEY``
            environment variable when not provided explicitly. Create one in
            the Cohere dashboard at https://dashboard.cohere.com/api-keys.
        api_base: Cohere OpenAI-compatible API base URL. Defaults to
            ``https://api.cohere.com/compatibility/v1`` unless overridden
            through the ``COHERE_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("COHERE_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("COHERE_API_BASE") or
                                    "https://api.cohere.com/compatibility/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("COHERE_PROXY"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the Cohere chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the Cohere
        compatibility API base URL.

        Args:
            messages (list): The chat messages to send to Cohere.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the Cohere chat completions endpoint.

        Args:
            messages (list): The chat messages to send to Cohere.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'CohereLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied ``cohere_llm.yaml.example``
        with a missing ``COHERE_API_KEY`` / ``COHERE_PROXY`` would otherwise
        assign ``''`` over the class defaults. That is worse than it sounds:
        the OpenAI client only rejects a *missing* key, so an empty key is
        silently sent upstream and surfaces as an opaque 401, and an empty
        ``api_base`` makes the client fall back to
        ``https://api.openai.com/v1`` - sending Cohere credentials to the
        wrong endpoint. Normalizing the empty values here makes an unset
        variable behave exactly like an omitted key: ``api_key`` / ``proxy``
        fall back to ``None`` and ``api_base`` to the Cohere compatibility
        endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            CohereLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("COHERE_API_BASE") or \
                "https://api.cohere.com/compatibility/v1"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Cohere model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name is looked up in
           :data:`COHERE_MAX_CONTEXT_LENGTH`.
        3. Cohere publishes dated releases of every family
           (``<modelname>-<month>-<year>`` such as command-r-plus-08-2024),
           so when the exact name is not listed the trailing date suffix is
           stripped and the base family entry is used for the second lookup
           attempt.
        4. As a last resort :data:`COHERE_DEFAULT_CONTEXT_LENGTH` is
           returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        if self.model_name in COHERE_MAX_CONTEXT_LENGTH:
            return COHERE_MAX_CONTEXT_LENGTH[self.model_name]
        if self.model_name:
            base_name = _COHERE_DATED_SUFFIX_RE.sub('', self.model_name)
            if base_name != self.model_name and base_name in COHERE_MAX_CONTEXT_LENGTH:
                return COHERE_MAX_CONTEXT_LENGTH[base_name]
        return COHERE_DEFAULT_CONTEXT_LENGTH

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Cohere models use Cohere's own tokenizer, which is not registered in
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
            # Cohere models are not registered in tiktoken by name;
            # cl100k_base is a robust generic fallback.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
