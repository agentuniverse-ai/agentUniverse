# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: kimi_openai_style_llm.py
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: kimi_openai_style_llm.py
import logging
from typing import Optional, Any, Union, Iterator, AsyncIterator

import requests
from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

KIMI_Max_CONTEXT_LENGTH = {
    "moonshot-v1-8k": 8000,
    "moonshot-v1-32k": 32000,
    "moonshot-v1-128k": 128000
}

# Default per-request timeout (seconds) for the Kimi tokenizer endpoint.
# Kimi's tokenizer is a small synchronous HTTP call on the hot path of context
# budgeting; without a timeout a stalled endpoint hangs the whole LLM call.
KIMI_TOKENIZER_TIMEOUT_SECONDS = 30

logger = logging.getLogger(__name__)


class KIMIOpenAIStyleLLM(OpenAIStyleLLM):
    """
        KIMI's OpenAI Style LLM
        Attributes:
            api_key (Optional[str]): The API key to use for authentication. Defaults to None.
            api_base (Optional[str]): The base URL to use for the API. Defaults to None.
    """
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("KIMI_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env(
        "KIMI_API_BASE") or "https://api.moonshot.cn/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("KIMI_PROXY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("KIMI_ORGANIZATION"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """ The call method of the LLM.

        Users can customize how the model interacts by overriding call method of the LLM class.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """ The async call method of the LLM.

        Users can customize how the model interacts by overriding acall method of the LLM class.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return await super()._acall(messages, **kwargs)

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return KIMI_Max_CONTEXT_LENGTH.get(self.model_name, 8000)

    def get_num_tokens(self, text: str) -> int:
        """Estimate the token count for ``text`` via Kimi's tokenizer endpoint.

        Bounded and explicit about failure modes so a stalled or malformed
        response surfaces a clear error instead of hanging the LLM call or
        crashing deep in a ``None.get`` chain:

        - ``requests.post`` now carries a timeout, so a non-responsive
          tokenizer cannot hang context budgeting indefinitely.
        - A non-2xx response is raised via ``raise_for_status`` with the URL
          and status, instead of letting ``res.json()`` fail later with a
          cryptic ``JSONDecodeError``.
        - The ``data`` / ``total_tokens`` fields are read defensively; a
          response that is valid JSON but missing those fields raises a
          clear ``RuntimeError`` instead of ``AttributeError: 'NoneType'
          object has no attribute 'get'``.
        """
        messages = [{"role": "user", "content": text}]
        body = {"model": self.model_name, "messages": messages}
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.api_key}'}
        url = f"{self.api_base}/tokenizers/estimate-token-count"
        res = requests.post(url, headers=headers, json=body,
                            timeout=KIMI_TOKENIZER_TIMEOUT_SECONDS)
        if not res.ok:
            raise RuntimeError(
                f"Kimi tokenizer request to {url} failed with status "
                f"{res.status_code}: {res.text[:200]}") from None
        try:
            payload = res.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Kimi tokenizer at {url} returned a non-JSON body "
                f"({exc}).") from exc
        data = payload.get('data') if isinstance(payload, dict) else None
        if not isinstance(data, dict) or 'total_tokens' not in data:
            raise RuntimeError(
                f"Kimi tokenizer at {url} returned an unexpected payload; "
                f"missing data.total_tokens in {str(payload)[:200]}.")
        total_tokens = data.get('total_tokens')
        if not isinstance(total_tokens, int):
            raise RuntimeError(
                f"Kimi tokenizer at {url} returned non-integer total_tokens "
                f"{total_tokens!r}.")
        return total_tokens
