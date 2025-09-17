# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/13 12:01
# @Author  : jerry.zzw
# @Email   : jerry.zzw@antgroup.com
# @FileName: llm_configer.py
from typing import Optional
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class LLMConfiger(ComponentConfiger):
    """The LLMConfiger class, which is used to load and manage the LLM configuration."""

    def __init__(self, configer: Optional[Configer] = None):
        """Initialize the LLMConfiger."""
        super().__init__(configer)
        self.__name: Optional[str] = None
        self.__description: Optional[str] = None
        self.__model_name: Optional[str] = None
        self.__temperature: Optional[float] = None
        self.__request_timeout: Optional[int] = None
        self.__max_tokens: Optional[int] = None
        self.__max_retries: Optional[int] = None
        self.__streaming: Optional[bool] = None
        self.__ext_info: Optional[dict] = None
        self.__max_context_length: Optional[int] = None
        self.__tracing: Optional[bool] = None

    @property
    def name(self) -> Optional[str]:
        """Return the name of the LLM."""
        return self.__name

    @property
    def description(self) -> Optional[str]:
        """Return the description of the LLM."""
        return self.__description

    @property
    def model_name(self) -> Optional[str]:
        return self.__model_name

    @property
    def temperature(self) -> Optional[float]:
        """Return the temperature of the LLM."""
        return self.__temperature

    @property
    def request_timeout(self) -> Optional[int]:
        return self.__request_timeout

    @property
    def max_tokens(self) -> Optional[int]:
        return self.__max_tokens

    @property
    def max_retries(self) -> Optional[int]:
        return self.__max_retries

    @property
    def streaming(self) -> Optional[bool]:
        return self.__streaming

    @property
    def ext_info(self) -> Optional[dict]:
        return self.__ext_info

    @property
    def max_content_length(self) -> Optional[int]:
        return self.__max_context_length

    @property
    def tracing(self) -> Optional[bool]:
        return self.__tracing

    def load(self) -> "LLMConfiger":
        """Load the configuration by the Configer object.
        Returns:
            LLMConfiger: the LLMConfiger object
        """
        return self.load_by_configer(self.__configer)

    def load_by_configer(self, configer: Configer) -> "LLMConfiger":
        """Load the configuration by the Configer object.
        Args:
            configer(Configer): the Configer object
        Returns:
            LLMConfiger: the LLMConfiger object
        """
        super().load_by_configer(configer)

        try:
            self.__name = configer.value.get("name")
            self.__description = configer.value.get("description")
            self.__model_name = configer.value.get("model_name")
            self.__temperature = configer.value.get("temperature")
            self.__request_timeout = configer.value.get("request_timeout")
            self.__max_tokens = configer.value.get("max_tokens")
            self.__max_retries = configer.value.get("max_retries")
            self.__streaming = configer.value.get("streaming")
            self.__ext_info = configer.value.get("ext_info")
            self.__max_context_length = configer.value.get("max_context_length")
            self.__tracing = configer.value.get("tracing")
        except Exception as e:
            raise Exception(f"Failed to parse the LLM configuration: {e}")
        return self
