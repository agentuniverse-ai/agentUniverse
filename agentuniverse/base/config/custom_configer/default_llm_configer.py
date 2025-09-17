# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/28 19:49
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: default_llm_configer.py
from typing import Optional

from agentuniverse.base.annotation.singleton import singleton
from ..configer import Configer


@singleton
class DefaultLLMConfiger(Configer):
    """
    A singleton class responsible for managing the default LLM configuration
    used in the agent system.

    This class reads and parses a TOML configuration file to determine the default LLM instance
    that will be used in the agent when no specific model is manually designated.
    """

    default_llm: Optional[str] = None

    def __init__(self, config_path: str = None):
        super().__init__(config_path)
        if config_path:
            try:
                self.load()
            except FileNotFoundError as e:
                print(
                    f"Configuration file not found at path: {config_path}. "
                    f"The default LLM configuration will not be loaded. "
                    f"Error is {str(e)}"
                )
        if self.value:
            self.default_llm = self.value.get("DEFAULT", {}).get("default_llm", None)
