# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: runcrate_openai_style_llm.py
from typing import Optional

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM


class DefaultRuncrateLLM(OpenAIStyleLLM):
    """Runcrate's OpenAI Style LLM.

    Runcrate serves open models through an OpenAI-compatible API. The model ids are the ones
    listed at https://api.runcrate.ai/v1/models.

    Attributes:
        api_key (Optional[str]): The API key to use for authentication. Defaults to the RUNCRATE_API_KEY environment variable.
        api_base (Optional[str]): The base URL to use for the API. Defaults to the RUNCRATE_API_BASE environment
            variable, then to https://api.runcrate.ai/v1.
        proxy (Optional[str]): The proxy to use for the API. Defaults to the RUNCRATE_PROXY environment variable.
        organization (Optional[str]): The organization to use for the API. Defaults to the RUNCRATE_ORGANIZATION
            environment variable.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("RUNCRATE_API_KEY"))
    api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("RUNCRATE_API_BASE") or "https://api.runcrate.ai/v1")
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("RUNCRATE_PROXY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("RUNCRATE_ORGANIZATION"))
