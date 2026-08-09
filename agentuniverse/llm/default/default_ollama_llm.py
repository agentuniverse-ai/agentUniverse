import json
from typing import Any, Union, AsyncIterator, Iterator, Optional, List, Sequence

import tiktoken
from langchain_core.language_models import BaseLanguageModel
from ollama import Options
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.system_util import process_yaml_func
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.ollama_langchain_instance import OllamaLangchainInstance


def _extract_ollama_message(response: Any) -> dict:
    """Return the ``message`` dict from an Ollama chat response.

    Ollama returns a top-level ``error`` field instead of ``message`` when the
    model is missing, the request is malformed, or the server hits an internal
    error. The previous code did ``res.get("message").get("content")``, which
    crashed with ``AttributeError: 'NoneType' object has no attribute 'get'``
    in that case — masking the real cause (often a model-not-found or context
    overflow) behind a generic NoneType error.

    This helper surfaces the Ollama error verbatim when present and only falls
    back to a clear ValueError when the response shape is unexpected, so
    callers see an actionable error instead of a NoneType crash.
    """
    if not isinstance(response, dict):
        raise ValueError(
            f"Ollama returned an unexpected response type {type(response).__name__}; "
            f"expected a dict, got {response!r}.")
    if "error" in response:
        raise RuntimeError(
            f"Ollama chat call failed: {response['error']}")
    message = response.get("message")
    if not isinstance(message, dict):
        raise ValueError(
            f"Ollama response is missing the 'message' object; "
            f"got response: {str(response)[:200]}.")
    return message


class OllamaLLM(LLM):
    base_url: Optional[str] = Field(
        default_factory=lambda: get_from_env("OLLAMA_BASE_URL") if get_from_env(
            "OLLAMA_BASE_URL") else "http://localhost:11434")
    """Base url the model is hosted under."""

    streaming: bool = True

    def _new_client(self):
        if self.client:
            return self.client
        from ollama import Client
        return Client(
            host=self.base_url,
        )

    def _new_async_client(self):
        if self.async_client:
            return self.async_client
        from ollama import AsyncClient
        return AsyncClient(
            host=self.base_url,
        )

    def _options(self):
        return Options(**{
            "num_ctx": self.max_context_length(),
            "num_predict": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.request_timeout,
            **(self.ext_info if self.ext_info else {}),
        })

    def _call(self, messages, stop=None, **kwargs) -> Union[LLMOutput, Iterator[LLMOutput]]:
        should_stream = kwargs.pop("stream", self.streaming)
        client = self._new_client()
        options = self._options()
        options.setdefault("stop", stop)
        res = client.chat(model=self.model_name, messages=messages, options=options, stream=should_stream)
        if should_stream:
            return self.generate_result(res)
        else:
            message = _extract_ollama_message(res)
            return LLMOutput(text=message.get('content', ''), raw=json.dumps(res))

    async def _acall(self, messages, stop=None, **kwargs) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        client = self._new_async_client()
        should_stream = kwargs.pop("stream", self.streaming)
        options = self._options()
        options.setdefault("stop", stop)
        res = await client.chat(model=self.model_name, messages=messages, options=options, stream=should_stream)
        if not should_stream:
            message = _extract_ollama_message(res)
            return LLMOutput(text=message.get('content', ''), raw=json.dumps(res))
        if should_stream:
            return self.agenerate_result(res)

    def generate_result(self, data):
        for line in data:
            message = _extract_ollama_message(line)
            yield LLMOutput(text=message.get('content', ''), raw=json.dumps(line))

    async def agenerate_result(self, data):
        async for line in data:
            message = _extract_ollama_message(line)
            yield LLMOutput(text=message.get('content', ''), raw=json.dumps(line))

    def as_langchain(self) -> BaseLanguageModel:
        self.init_channel()
        if self._channel_instance:
            return self._channel_instance.as_langchain()
        return OllamaLangchainInstance(
            self
        )

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'LLM':
        super().initialize_by_component_configer(component_configer)
        if 'base_url' in component_configer.configer.value:
            base_url = component_configer.configer.value['base_url']
            self.base_url = process_yaml_func(base_url, component_configer.yaml_func_instance)
        if 'max_context_length' in component_configer.configer.value:
            self._max_context_length = component_configer.configer.value['max_context_length']
        return self

    def get_num_tokens(self, text: str) -> int:
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
