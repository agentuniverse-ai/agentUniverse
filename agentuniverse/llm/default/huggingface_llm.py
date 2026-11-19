# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/05
# @FileName: huggingface_llm.py

"""HuggingFace LLM implementation built on the native `huggingface_hub` interfaces.

The OpenAI compatible route is already covered by `OpenAIStyleLLM`, so this component
deliberately uses the native `huggingface_hub` client instead:

- `InferenceClient.chat_completion` / `AsyncInferenceClient.chat_completion` for the
  conversational task, it also carries the inference provider routing of the HF hub.
- `InferenceClient.text_generation` / `AsyncInferenceClient.text_generation` for the
  native TGI generation task, which exposes the parameters that do not exist in the
  chat schema, such as `top_k`, `repetition_penalty`, `do_sample` or `watermark`.

It supports the HF Inference Providers router, dedicated Inference Endpoints and self
hosted TGI servers.
"""

import json
from typing import Any, AsyncIterator, Iterator, List, Optional, Union

from langchain_core.language_models import BaseLanguageModel
from pydantic import Field

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.system_util import process_yaml_func
from agentuniverse.llm.huggingface_langchain_instance import HuggingFaceLangchainInstance
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput, TokenUsage

CHAT_TASK = 'chat'
TEXT_GENERATION_TASK = 'text_generation'

# Common HuggingFace hosted model context lengths.
# Self hosted deployments may differ, use `max_context_length` in the yaml to override.
HUGGINGFACE_MAX_CONTEXT_LENGTH = {
    # Llama models
    "meta-llama/Llama-3.1-8B-Instruct": 131072,
    "meta-llama/Llama-3.1-70B-Instruct": 131072,
    "meta-llama/Llama-3.1-405B-Instruct": 131072,
    "meta-llama/Llama-3.2-1B-Instruct": 131072,
    "meta-llama/Llama-3.2-3B-Instruct": 131072,
    "meta-llama/Llama-3.3-70B-Instruct": 131072,
    "meta-llama/Meta-Llama-3-8B-Instruct": 8192,
    "meta-llama/Meta-Llama-3-70B-Instruct": 8192,
    # Mistral models
    "mistralai/Mistral-7B-Instruct-v0.2": 32768,
    "mistralai/Mistral-7B-Instruct-v0.3": 32768,
    "mistralai/Mixtral-8x7B-Instruct-v0.1": 32768,
    "mistralai/Mixtral-8x22B-Instruct-v0.1": 65536,
    "mistralai/Mistral-Nemo-Instruct-2407": 131072,
    # Qwen models
    "Qwen/Qwen2-7B-Instruct": 32768,
    "Qwen/Qwen2-72B-Instruct": 32768,
    "Qwen/Qwen2.5-0.5B-Instruct": 32768,
    "Qwen/Qwen2.5-7B-Instruct": 32768,
    "Qwen/Qwen2.5-32B-Instruct": 32768,
    "Qwen/Qwen2.5-72B-Instruct": 32768,
    "Qwen/Qwen2.5-Coder-32B-Instruct": 32768,
    # DeepSeek models
    "deepseek-ai/DeepSeek-V3": 65536,
    "deepseek-ai/DeepSeek-R1": 65536,
    # Google models
    "google/gemma-2-9b-it": 8192,
    "google/gemma-2-27b-it": 8192,
    # Microsoft models
    "microsoft/Phi-3-mini-4k-instruct": 4096,
    "microsoft/Phi-3.5-mini-instruct": 131072,
    # Default fallback
    "default": 4096,
}


class HuggingFaceLLM(LLM):
    """The HuggingFace LLM class based on the native `huggingface_hub` client.

    Attributes:
        huggingface_api_key (Optional[str]): HuggingFace access token, read from the
            `HUGGINGFACE_API_KEY` or `HF_TOKEN` environment variable by default.
        huggingface_base_url (Optional[str]): Url of a dedicated Inference Endpoint or of a
            self hosted TGI server. When it is set the client targets that url directly,
            while `model_name` is still sent as the payload model field.
        provider (Optional[str]): HuggingFace inference provider routing, such as `auto`,
            `hf-inference`, `together` or `fireworks-ai`.
        task (str): `chat` uses `chat_completion`, `text_generation` uses the native TGI
            `text_generation` route which supports the extra sampling parameters below.
        top_k (Optional[int]): Keep only the top k highest probability tokens.
        top_p (Optional[float]): Nucleus sampling probability.
        repetition_penalty (Optional[float]): Penalty applied to repeated tokens.
        do_sample (Optional[bool]): Whether to use sampling instead of greedy decoding.
        seed (Optional[int]): Random seed used for reproducible generation.
        best_of (Optional[int]): Generate `best_of` sequences and return the most likely one.
        typical_p (Optional[float]): Typical decoding mass.
        watermark (Optional[bool]): Enable watermarking.

    Note:
        `top_k`, `repetition_penalty`, `do_sample`, `best_of`, `typical_p` and `watermark`
        do not exist in the chat completions schema. With `task: 'chat'` they are sent
        through `extra_body`, which strict backends such as TGI reject with a HTTP 422.
        Use `task: 'text_generation'` to pass them natively.

    Environment Variables:
        HUGGINGFACE_API_KEY / HF_TOKEN: HuggingFace access token.
        HUGGINGFACE_BASE_URL: Inference Endpoint or self hosted TGI url.
        HUGGINGFACE_PROVIDER: Inference provider used by the HF router.
    """

    huggingface_api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("HUGGINGFACE_API_KEY") or get_from_env("HF_TOKEN"))
    huggingface_base_url: Optional[str] = Field(
        default_factory=lambda: get_from_env("HUGGINGFACE_BASE_URL"))
    provider: Optional[str] = Field(
        default_factory=lambda: get_from_env("HUGGINGFACE_PROVIDER"))

    task: str = CHAT_TASK

    # Native generation parameters of the huggingface_hub client.
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    repetition_penalty: Optional[float] = None
    do_sample: Optional[bool] = None
    seed: Optional[int] = None
    best_of: Optional[int] = None
    typical_p: Optional[float] = None
    watermark: Optional[bool] = None

    def _client_args(self) -> dict:
        """Build the arguments shared by the sync and the async huggingface clients."""
        if not self.huggingface_base_url and not self.model_name:
            raise ValueError("either model_name or huggingface_base_url is required")

        # `model` and `base_url` are mutually exclusive in the huggingface inference client.
        if self.huggingface_base_url:
            client_args = {"base_url": self.huggingface_base_url}
        else:
            client_args = {"model": self.model_name}
            if self.provider:
                client_args["provider"] = self.provider
        client_args["api_key"] = self.huggingface_api_key
        if self.request_timeout:
            client_args["timeout"] = self.request_timeout
        return client_args

    def _new_client(self):
        """Initialize the huggingface sync inference client."""
        if self.client:
            return self.client
        try:
            from huggingface_hub import InferenceClient
        except ImportError:
            raise ImportError(
                "huggingface_hub is required. Install with: pip install huggingface_hub")
        self.client = InferenceClient(**self._client_args())
        return self.client

    def _new_async_client(self):
        """Initialize the huggingface async inference client."""
        if self.async_client:
            return self.async_client
        try:
            from huggingface_hub import AsyncInferenceClient
        except ImportError:
            raise ImportError(
                "huggingface_hub is required. Install with: pip install huggingface_hub")
        self.async_client = AsyncInferenceClient(**self._client_args())
        return self.async_client

    def _native_params(self) -> dict:
        """Collect the native generation parameters explicitly set on the component."""
        params = {
            'top_k': self.top_k,
            'repetition_penalty': self.repetition_penalty,
            'do_sample': self.do_sample,
            'best_of': self.best_of,
            'typical_p': self.typical_p,
            'watermark': self.watermark,
        }
        return {key: value for key, value in params.items() if value is not None}

    def _chat_args(self, stop: Optional[List[str]], streaming: bool, kwargs: dict) -> dict:
        """Build the `chat_completion` arguments."""
        native_params = {**self._native_params(), **(kwargs.pop('extra_body', None) or {})}
        chat_args = {
            'stream': streaming,
            'max_tokens': kwargs.pop('max_tokens', self.max_tokens),
            'temperature': kwargs.pop('temperature', self.temperature),
            'top_p': kwargs.pop('top_p', self.top_p),
            'seed': kwargs.pop('seed', self.seed),
            'stop': stop,
        }
        if native_params:
            # not part of the chat schema, only strict backends will reject them.
            chat_args['extra_body'] = native_params
        # `huggingface_hub` falls back to the base url as the payload `model` field, which
        # strict backends reject, so the real model name is always sent when it is known.
        model_name = kwargs.pop('model', self.model_name)
        if model_name:
            chat_args['model'] = model_name
        chat_args.update(kwargs)
        return {key: value for key, value in chat_args.items() if value is not None}

    def _text_generation_args(self, stop: Optional[List[str]], streaming: bool,
                              kwargs: dict) -> dict:
        """Build the native `text_generation` arguments."""
        generation_args = {
            'stream': streaming,
            'max_new_tokens': kwargs.pop('max_tokens', self.max_tokens),
            'temperature': kwargs.pop('temperature', self.temperature),
            'top_p': kwargs.pop('top_p', self.top_p),
            'seed': kwargs.pop('seed', self.seed),
            'stop': stop,
            **self._native_params(),
        }
        if not self.huggingface_base_url:
            generation_args['model'] = kwargs.pop('model', self.model_name)
        else:
            kwargs.pop('model', None)
        generation_args.update(kwargs)
        return {key: value for key, value in generation_args.items() if value is not None}

    @staticmethod
    def as_prompt(messages: list) -> str:
        """Flatten a message list into a prompt for the native text generation task."""
        parts = []
        for message in messages:
            if isinstance(message, str):
                parts.append(message)
                continue
            content = message.get('content') if isinstance(message, dict) else None
            if content:
                parts.append(str(content))
        return "\n".join(parts)

    def _call(self, messages: list, stop: Optional[List[str]] = None,
              **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Run the HuggingFace LLM through the native huggingface_hub client."""
        streaming = kwargs.pop('streaming', self.streaming)
        if 'stream' in kwargs:
            streaming = kwargs.pop('stream')
        client = self._new_client()

        if self.task == TEXT_GENERATION_TASK:
            result = client.text_generation(
                self.as_prompt(messages), **self._text_generation_args(stop, streaming, kwargs))
            if streaming:
                return self.generate_text_stream_result(result)
            return self.parse_text_generation_result(result)

        result = client.chat_completion(
            messages=messages, **self._chat_args(stop, streaming, kwargs))
        if streaming:
            return self.generate_stream_result(result)
        return self.parse_chat_result(result)

    async def _acall(self, messages: list, stop: Optional[List[str]] = None,
                     **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronously run the HuggingFace LLM through the native huggingface_hub client."""
        streaming = kwargs.pop('streaming', self.streaming)
        if 'stream' in kwargs:
            streaming = kwargs.pop('stream')
        client = self._new_async_client()

        if self.task == TEXT_GENERATION_TASK:
            result = await client.text_generation(
                self.as_prompt(messages), **self._text_generation_args(stop, streaming, kwargs))
            if streaming:
                return self.agenerate_text_stream_result(result)
            return self.parse_text_generation_result(result)

        result = await client.chat_completion(
            messages=messages, **self._chat_args(stop, streaming, kwargs))
        if streaming:
            return self.agenerate_stream_result(result)
        return self.parse_chat_result(result)

    @staticmethod
    def _raw(output: Any) -> str:
        """Serialize a huggingface output object, it is a dataclass like dict subclass."""
        try:
            return json.dumps(output, default=lambda value: getattr(value, '__dict__', str(value)))
        except (TypeError, ValueError):
            return str(output)

    @classmethod
    def _usage(cls, output: Any) -> Optional[TokenUsage]:
        usage = getattr(output, 'usage', None)
        if not usage:
            return None
        return TokenUsage.from_openai({
            'prompt_tokens': getattr(usage, 'prompt_tokens', 0),
            'completion_tokens': getattr(usage, 'completion_tokens', 0),
        })

    @classmethod
    def parse_chat_result(cls, output: Any) -> LLMOutput:
        """Convert a `chat_completion` output into an aU LLMOutput."""
        choice = output.choices[0]
        text = choice.message.content or ''
        return LLMOutput(text=text, raw=cls._raw(output), usage=cls._usage(output),
                         message=Message(content=text, type=choice.message.role or 'assistant'))

    @classmethod
    def parse_chat_chunk(cls, chunk: Any) -> LLMOutput:
        """Convert a `chat_completion` stream chunk into an aU LLMOutput."""
        choices = getattr(chunk, 'choices', None)
        text = ''
        if choices:
            text = getattr(choices[0].delta, 'content', None) or ''
        return LLMOutput(type='stream', text=text, raw=cls._raw(chunk), usage=cls._usage(chunk),
                         message=Message(content=text, type='assistant'))

    @classmethod
    def parse_text_generation_result(cls, output: Any) -> LLMOutput:
        """Convert a native `text_generation` output into an aU LLMOutput."""
        text = output if isinstance(output, str) else getattr(output, 'generated_text', '') or ''
        return LLMOutput(text=text, raw=cls._raw(output),
                         message=Message(content=text, type='assistant'))

    @classmethod
    def parse_text_generation_chunk(cls, chunk: Any) -> LLMOutput:
        """Convert a native `text_generation` stream chunk into an aU LLMOutput."""
        text = chunk if isinstance(chunk, str) else getattr(chunk, 'token', None)
        if not isinstance(text, str):
            text = getattr(text, 'text', '') if text is not None else ''
        return LLMOutput(type='stream', text=text or '', raw=cls._raw(chunk),
                         message=Message(content=text or '', type='assistant'))

    def generate_stream_result(self, stream) -> Iterator[LLMOutput]:
        for chunk in stream:
            yield self.parse_chat_chunk(chunk)

    async def agenerate_stream_result(self, stream) -> AsyncIterator[LLMOutput]:
        async for chunk in stream:
            yield self.parse_chat_chunk(chunk)

    def generate_text_stream_result(self, stream) -> Iterator[LLMOutput]:
        for chunk in stream:
            yield self.parse_text_generation_chunk(chunk)

    async def agenerate_text_stream_result(self, stream) -> AsyncIterator[LLMOutput]:
        async for chunk in stream:
            yield self.parse_text_generation_chunk(chunk)

    def as_langchain(self) -> BaseLanguageModel:
        """Convert the aU HuggingFace llm class to a langchain chat model."""
        self.init_channel()
        if self._channel_instance:
            return self._channel_instance.as_langchain()
        return HuggingFaceLangchainInstance(self)

    def set_by_agent_model(self, **kwargs) -> None:
        """Assign the agent configuration values to the HuggingFace llm model."""
        copied_obj = super().set_by_agent_model(**kwargs)
        if 'huggingface_api_key' in kwargs and kwargs['huggingface_api_key']:
            copied_obj.huggingface_api_key = kwargs['huggingface_api_key']
        if 'huggingface_base_url' in kwargs and kwargs['huggingface_base_url']:
            copied_obj.huggingface_base_url = kwargs['huggingface_base_url']
        if 'provider' in kwargs and kwargs['provider']:
            copied_obj.provider = kwargs['provider']
        if 'task' in kwargs and kwargs['task']:
            copied_obj.task = kwargs['task']
        return copied_obj

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'LLM':
        """Initialize the HuggingFace llm by the LLMConfiger object."""
        super().initialize_by_component_configer(component_configer)
        config_value = component_configer.configer.value
        for yaml_key in ['huggingface_api_key', 'huggingface_base_url', 'provider']:
            if yaml_key in config_value:
                setattr(self, yaml_key,
                        process_yaml_func(config_value.get(yaml_key),
                                          component_configer.yaml_func_instance))
        if 'huggingface_api_key_env' in config_value:
            self.huggingface_api_key = get_from_env(config_value.get('huggingface_api_key_env'))
        if 'task' in config_value:
            self.task = config_value.get('task')
        if 'max_context_length' in config_value:
            self._max_context_length = config_value.get('max_context_length')
        for yaml_key in ['top_k', 'top_p', 'repetition_penalty', 'do_sample', 'seed',
                         'best_of', 'typical_p', 'watermark']:
            if yaml_key in config_value:
                setattr(self, yaml_key, config_value.get(yaml_key))
        return self

    def get_num_tokens(self, text: str) -> int:
        """Return the number of tokens present in the text."""
        import tiktoken
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def max_context_length(self) -> int:
        """Return the maximum length of the context."""
        if super().max_context_length():
            return super().max_context_length()
        return HUGGINGFACE_MAX_CONTEXT_LENGTH.get(self.model_name,
                                                  HUGGINGFACE_MAX_CONTEXT_LENGTH['default'])
