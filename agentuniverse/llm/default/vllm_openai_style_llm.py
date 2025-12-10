#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/16
# @Author  : kaichuan
# @FileName: vllm_openai_style_llm.py

"""
vLLM OpenAI-Style LLM implementation.

This module provides integration with vLLM servers using OpenAI-compatible API.
vLLM is a fast and easy-to-use library for LLM inference and serving, offering:
- High throughput serving (up to 24x faster than HuggingFace Transformers)
- Efficient memory management with PagedAttention
- Continuous batching for improved throughput
- OpenAI-compatible API endpoint

For more information, visit: https://docs.vllm.ai/
"""

from typing import Optional

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# Common vLLM model context lengths
# Note: These are typical values. Actual limits depend on your vLLM server configuration
VLLM_MAX_CONTEXT_LENGTH = {
    # Llama models
    "meta-llama/Llama-2-7b-chat-hf": 4096,
    "meta-llama/Llama-2-13b-chat-hf": 4096,
    "meta-llama/Llama-2-70b-chat-hf": 4096,
    "meta-llama/Llama-3.1-8B-Instruct": 131072,
    "meta-llama/Llama-3.1-70B-Instruct": 131072,
    "meta-llama/Llama-3.1-405B-Instruct": 131072,
    "meta-llama/Llama-3.2-1B-Instruct": 131072,
    "meta-llama/Llama-3.2-3B-Instruct": 131072,
    # Mistral models
    "mistralai/Mistral-7B-Instruct-v0.1": 8192,
    "mistralai/Mistral-7B-Instruct-v0.2": 32768,
    "mistralai/Mistral-7B-Instruct-v0.3": 32768,
    "mistralai/Mixtral-8x7B-Instruct-v0.1": 32768,
    "mistralai/Mixtral-8x22B-Instruct-v0.1": 65536,
    # Qwen models
    "Qwen/Qwen2-7B-Instruct": 32768,
    "Qwen/Qwen2-72B-Instruct": 32768,
    "Qwen/Qwen2.5-7B-Instruct": 32768,
    "Qwen/Qwen2.5-72B-Instruct": 32768,
    # Yi models
    "01-ai/Yi-6B-Chat": 4096,
    "01-ai/Yi-34B-Chat": 4096,
    # DeepSeek models
    "deepseek-ai/deepseek-llm-7b-chat": 4096,
    "deepseek-ai/deepseek-llm-67b-chat": 4096,
    # Phi models
    "microsoft/phi-2": 2048,
    "microsoft/Phi-3-mini-4k-instruct": 4096,
    "microsoft/Phi-3-medium-4k-instruct": 4096,
    # Default fallback
    "default": 4096,
}


class VLLMOpenAIStyleLLM(OpenAIStyleLLM):
    """
    vLLM LLM implementation using OpenAI-compatible API.

    This class provides integration with vLLM servers through their OpenAI-compatible
    API endpoint. vLLM is a high-performance inference engine that offers significant
    speed improvements over traditional serving methods.

    vLLM Features:
        - Fast inference: Up to 24x throughput improvement over HuggingFace Transformers
        - Memory efficiency: PagedAttention reduces memory usage by 50-70%
        - Continuous batching: Automatic request batching for higher throughput
        - Quantization support: GPTQ, AWQ, SqueezeLLM for reduced memory footprint
        - Tensor parallelism: Multi-GPU support for large models
        - Streaming support: Real-time token generation
        - OpenAI compatibility: Drop-in replacement for OpenAI API

    Deployment Options:
        1. Self-hosted single server:
           python -m vllm.entrypoints.openai.api_server \\
               --model meta-llama/Llama-3.1-8B-Instruct \\
               --port 8000

        2. Docker deployment:
           docker run --gpus all -p 8000:8000 \\
               vllm/vllm-openai:latest \\
               --model meta-llama/Llama-3.1-8B-Instruct

        3. Production stack with monitoring:
           Use vLLM Production Stack for advanced features

    Configuration Example:
        ```yaml
        name: 'vllm-llama-3.1-8b'
        description: 'Llama 3.1 8B via vLLM'
        model_name: 'meta-llama/Llama-3.1-8B-Instruct'
        api_base: 'http://localhost:8000/v1'
        api_key: 'EMPTY'  # vLLM doesn't require API key by default
        max_tokens: 2048
        temperature: 0.7
        streaming: true
        meta_class: 'agentuniverse.llm.default.vllm_openai_style_llm.VLLMOpenAIStyleLLM'
        ```

    Attributes:
        api_base (str): vLLM server endpoint URL (default: http://localhost:8000/v1)
        api_key (str): API key (default: "EMPTY" - vLLM doesn't require auth by default)
        model_name (str): Model identifier hosted on vLLM server
        use_beam_search (bool): Enable beam search for generation (vLLM-specific)
        best_of (Optional[int]): Number of sequences to generate and return the best
        length_penalty (float): Length penalty for beam search
        early_stopping (bool): Stop generation when all beams are finished

    Environment Variables:
        VLLM_API_BASE: Base URL for vLLM server (default: http://localhost:8000/v1)
        VLLM_API_KEY: API key if authentication is enabled (default: EMPTY)

    Performance Tips:
        - Use quantization (GPTQ/AWQ) for memory-constrained environments
        - Enable tensor parallelism for large models across multiple GPUs
        - Tune max_num_seqs and max_num_batched_tokens for your workload
        - Use continuous batching for higher throughput with varying request sizes

    For more information:
        - Documentation: https://docs.vllm.ai/
        - GitHub: https://github.com/vllm-project/vllm
        - Production Stack: https://github.com/vllm-project/production-stack
    """

    # Override default API base to point to vLLM server
    api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("VLLM_API_BASE") or "http://localhost:8000/v1"
    )

    # vLLM typically doesn't require authentication by default
    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("VLLM_API_KEY") or "EMPTY"
    )

    # vLLM-specific parameters for advanced generation control
    # These are optional and will be passed to the vLLM server if provided
    use_beam_search: Optional[bool] = None
    best_of: Optional[int] = None
    length_penalty: Optional[float] = None
    early_stopping: Optional[bool] = None

    def _call(self, messages: list, **kwargs):
        """
        Call the vLLM server.

        This method adds vLLM-specific parameters to the request if they are configured.
        All standard OpenAI parameters are supported since vLLM is API-compatible.

        Args:
            messages (list): List of message dictionaries with 'role' and 'content'
            **kwargs: Additional generation parameters

        Returns:
            LLMOutput or Iterator[LLMOutput]: Response from vLLM server
        """
        # Add vLLM-specific parameters if configured
        extra_params = {}
        if self.use_beam_search is not None:
            extra_params['use_beam_search'] = self.use_beam_search
        if self.best_of is not None:
            extra_params['best_of'] = self.best_of
        if self.length_penalty is not None:
            extra_params['length_penalty'] = self.length_penalty
        if self.early_stopping is not None:
            extra_params['early_stopping'] = self.early_stopping

        # Merge with user-provided kwargs (user kwargs take precedence)
        kwargs = {**extra_params, **kwargs}

        # Call parent implementation with merged parameters
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs):
        """
        Async call to vLLM server.

        Args:
            messages (list): List of message dictionaries
            **kwargs: Additional generation parameters

        Returns:
            LLMOutput or AsyncIterator[LLMOutput]: Response from vLLM server
        """
        # Add vLLM-specific parameters if configured
        extra_params = {}
        if self.use_beam_search is not None:
            extra_params['use_beam_search'] = self.use_beam_search
        if self.best_of is not None:
            extra_params['best_of'] = self.best_of
        if self.length_penalty is not None:
            extra_params['length_penalty'] = self.length_penalty
        if self.early_stopping is not None:
            extra_params['early_stopping'] = self.early_stopping

        # Merge with user-provided kwargs (user kwargs take precedence)
        kwargs = {**extra_params, **kwargs}

        # Call parent implementation with merged parameters
        return await super()._acall(messages, **kwargs)

    def max_context_length(self) -> int:
        """
        Return the maximum context length for the model.

        Returns:
            int: Maximum context length in tokens

        Note:
            The actual context length depends on your vLLM server configuration.
            You can configure this with --max-model-len when starting vLLM server.
        """
        if self._max_context_length:
            return self._max_context_length

        # Try to get context length from known models
        if self.model_name in VLLM_MAX_CONTEXT_LENGTH:
            return VLLM_MAX_CONTEXT_LENGTH[self.model_name]

        # Return default if model not in our list
        return VLLM_MAX_CONTEXT_LENGTH["default"]
