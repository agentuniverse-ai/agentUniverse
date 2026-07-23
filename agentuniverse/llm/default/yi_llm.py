# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : agentuniverse
# @FileName: yi_llm.py

"""
01.AI (零一万物) Yi series LLM.

01.AI (https://www.01.ai) is the artificial intelligence company founded by
Kai-Fu Lee whose flagship product line is the **Yi** family of foundation
large language models (Yi-Large, Yi-Medium, Yi-Small, Yi-Vision, ...).

The Yi models are exposed through a fully **OpenAI-compatible** Chat
Completions API at ``https://api.01.ai/v1``. Because of that compatibility
this component only needs to extend :class:`OpenAIStyleLLM` and wire up the
correct default environment variables, the 01.AI API base URL and the
per-model maximum context length table. Streaming, tool calling, the async
interface and the LangChain bridge all work out of the box.
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import tiktoken
from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# The maximum context length (input + output tokens) supported by the Yi
# models currently available on the 01.AI platform. Values are taken from
# the official 01.AI documentation (https://platform.lingyiwanhu.com).
# When 01.AI releases a new model it is sufficient to add an entry here,
# the rest of the component keeps working unchanged.
YI_MAX_CONTEXT_LENGTH = {
    # ---- Flagship large model ----
    "yi-large": 32768,
    "yi-large-turbo": 32768,
    "yi-large-rag": 32768,
    # ---- Mid-size model ----
    "yi-medium": 16384,
    "yi-medium-200k": 204800,
    # ---- Small / fast model ----
    "yi-small": 16384,
    "yi-spark": 16384,
    # ---- Vision model ----
    "yi-vision": 16384,
    "yi-vision-plus": 16384,
}

# Sensible default context length returned for models that are not yet listed
# in the table above. The Yi family commonly exposes a 16k window, so 16384
# is a safe conservative fallback.
YI_DEFAULT_CONTEXT_LENGTH = 16384


class YiLLM(OpenAIStyleLLM):
    """01.AI Yi series LLM, an OpenAI-compatible wrapper around the Yi API.

    01.AI runs the Yi family of foundation models behind an
    OpenAI-compatible endpoint. Because the wire protocol is identical to
    OpenAI's, this class only customises the credential/base-url plumbing
    and the model context-length lookup table while inheriting the complete
    request, streaming and langchain-bridge implementation from
    :class:`OpenAIStyleLLM`.

    Attributes:
        api_key: 01.AI API key. Loaded from the ``YI_API_KEY`` environment
            variable when not provided explicitly. Create one at
            https://platform.lingyiwanhu.com.
        api_base: 01.AI OpenAI-compatible API base URL. Defaults to
            ``https://api.01.ai/v1`` unless overridden through the
            ``YI_API_BASE`` environment variable.
        proxy: Optional HTTP(S) proxy used for outbound requests.
        organization: Optional organization id forwarded to the client.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("YI_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("YI_API_BASE") or
                                    "https://api.01.ai/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("YI_PROXY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("YI_ORGANIZATION"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call to the 01.AI chat completions endpoint.

        Users may override this method to customise the interaction, the
        default implementation simply delegates to the OpenAI-style parent
        which constructs and dispatches the request against the 01.AI API
        base URL.

        Args:
            messages (list): The chat messages to send to the Yi model.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                client, e.g. ``temperature``, ``top_p``, ``max_tokens`` ...

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an iterator of
            :class:`LLMOutput` chunks when ``stream=True`` is supplied.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call to the 01.AI chat completions endpoint.

        Args:
            messages (list): The chat messages to send to the Yi model.
            **kwargs: Arbitrary keyword arguments forwarded to the OpenAI
                async client.

        Returns:
            An :class:`LLMOutput` for non-streaming calls, or an async
            iterator of :class:`LLMOutput` chunks when ``stream=True``.
        """
        return await super()._acall(messages, **kwargs)

    def max_context_length(self) -> int:
        """Return the maximum context length for the configured Yi model.

        The combined length of the input prompt and the generated completion
        must fit within this window. The value is resolved in the following
        order:

        1. If a context length was explicitly injected through the YAML
           configuration (``max_context_length`` field) that value wins.
        2. Otherwise the model name is looked up in
           :data:`YI_MAX_CONTEXT_LENGTH`.
        3. As a last resort :data:`YI_DEFAULT_CONTEXT_LENGTH` is returned.
        """
        if super().max_context_length():
            return super().max_context_length()
        return YI_MAX_CONTEXT_LENGTH.get(self.model_name, YI_DEFAULT_CONTEXT_LENGTH)

    def get_num_tokens(self, text: str) -> int:
        """Estimate the number of tokens that ``text`` will consume.

        The Yi model family does not ship a public tokenizer registered in
        ``tiktoken`` by name, so we fall back to the widely used
        ``cl100k_base`` encoding which gives a good approximation suitable
        for budget / prompt-window checks.

        Args:
            text: The raw string to tokenize.

        Returns:
            The integer number of tokens the text would be encoded into.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # Yi models are not registered in tiktoken by name; cl100k_base
            # is a robust generic fallback for modern LLM tokenizers.
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
