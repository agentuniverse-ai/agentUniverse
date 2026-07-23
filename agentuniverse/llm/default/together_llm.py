# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : agentuniverse
# @FileName: together_llm.py

"""
Together AI LLM.

Together AI (https://www.together.ai) is a hosted inference platform that
serves 200+ open-source large language models - including Llama, Mixtral,
Qwen, DeepSeek, DBRX, Falcon and many others - through a single,
OpenAI-compatible Chat Completions API exposed at
``https://api.together.xyz/v1``.

Because the API is OpenAI-compatible, this component only needs to extend
:class:`OpenAIStyleLLM` and wire up the Together credentials, the API base
URL and a per-model maximum context length table. Streaming, tool calling,
the async interface and the LangChain bridge are all inherited unchanged
from the parent class.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.annotation.trace import trace_llm
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by a selection
# of the most popular models hosted on Together AI. Together constantly adds
# new models; when a model you rely on is missing simply add an entry here.
# The values are taken from the official Together models catalogue
# (https://docs.together.ai/docs/inference-models).
TOGETHER_MAX_CONTEXT_LENGTH = {
    # ---- Meta Llama family ----
    "meta-llama/Llama-3.3-70B-Instruct-Turbo": 131072,
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo": 131072,
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo": 131072,
    "meta-llama/Meta-Llama-3-70B-Instruct-Lite": 8192,
    "meta-llama/Meta-Llama-3-8B-Instruct-Lite": 8192,
    "meta-llama/Llama-2-70b-chat-hf": 4096,
    "meta-llama/Llama-2-13b-chat-hf": 4096,
    "meta-llama/Llama-2-7b-chat-hf": 4096,
    # ---- Mistral / Mixtral family ----
    "mistralai/Mixtral-8x7B-Instruct-v0.1": 32768,
    "mistralai/Mistral-7B-Instruct-v0.1": 4096,
    "mistralai/Mistral-7B-Instruct-v0.2": 32768,
    "mistralai/Mistral-7B-Instruct-v0.3": 32768,
    "mistralai/Mistral-Large-Instruct-2411": 131072,
    # ---- Qwen family ----
    "Qwen/Qwen2.5-72B-Instruct-Turbo": 131072,
    "Qwen/Qwen2.5-7B-Instruct-Turbo": 131072,
    "Qwen/Qwen1.5-110B-Chat": 32768,
    "Qwen/Qwen1.5-72B-Chat": 32768,
    # ---- DeepSeek family ----
    "deepseek-ai/DeepSeek-V3": 131072,
    "deepseek-ai/DeepSeek-R1": 131072,
    # ---- databricks / NVIDIA ----
    "databricks/dbrx-instruct": 32768,
    "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF": 131072,
}

# Conservative fallback returned for models that are not yet listed in the
# table above. The majority of Together-hosted models expose at least an 8k
# window, so 8192 is a safe default.
TOGETHER_DEFAULT_CONTEXT_LENGTH = 8192


class TogetherLLM(OpenAIStyleLLM):
    """Together AI LLM, an OpenAI-compatible wrapper around the Together API.

    Together AI hosts 200+ open-source models (Llama, Mixtral, Qwen,
    DeepSeek, ...) behind a single OpenAI-compatible endpoint. This class
    therefore only customises the credential/base-url plumbing and the model
    context-length lookup table while inheriting the full request,
    streaming and langchain-bridge implementation from
    :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: Together AI API key. Loaded from the ``TOGETHER_API_KEY``
            environment variable when not supplied explicitly. Generate one
            at https://api.together.ai/settings/api-keys.
        api_base: Together OpenAI-compatible API base URL. Defaults to
            ``https://api.together.xyz/v1`` unless overridden through the
            ``TOGETHER_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
        organization: Optional organization id forwarded to the client.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("TOGETHER_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("TOGETHER_API_BASE") or
                                    "https://api.together.xyz/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("TOGETHER_PROXY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("TOGETHER_ORGANIZATION"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the Together chat completions endpoint.

        Users may override this method to customise the interaction; the
        default implementation delegates to the OpenAI-style parent which
        builds and dispatches the request against the Together API base URL.

        Args:
            messages (list): The chat messages to send to Together AI.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the Together chat completions endpoint.

        Args:
            messages (list): The chat messages to send to Together AI.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Together model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name is looked up in
           :data:`TOGETHER_MAX_CONTEXT_LENGTH`.
        3. As a last resort :data:`TOGETHER_DEFAULT_CONTEXT_LENGTH` is
           returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        return TOGETHER_MAX_CONTEXT_LENGTH.get(self.model_name, TOGETHER_DEFAULT_CONTEXT_LENGTH)

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        Together AI serves a heterogeneous catalogue of open-weight models,
        each with its own tokenizer. Because those tokenizers are not always
        registered in ``tiktoken`` by name, we fall back to the widely used
        ``cl100k_base`` encoding which yields a good approximation suitable
        for prompt-window budgeting.

        Args:
            text: The raw string to tokenize.

        Returns:
            The integer number of tokens the text would be encoded into.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # Together models (llama, mixtral, qwen, ...) are generally not
            # registered in tiktoken by name; cl100k_base is a robust generic
            # fallback that is accurate enough for budget checks.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
