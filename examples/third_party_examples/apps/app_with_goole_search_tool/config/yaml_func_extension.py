# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/28 17:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: yaml_func_extension.py
import os
from enum import Enum
from functools import lru_cache


class LLMModelEnum(Enum):
    QWEN = "qwen"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    CLAUDE = "claude"
    KIMI = "kimi"
    ZHIPU = "zhipu"
    BAICHUAN = "baichuan"
    GEMINI = "gemini"
    WENXIN = "wenxin"


class YamlFuncExtension:
    """
   This class is a yaml function extension class that allows users to define custom functions in YAML configuration.
   During the startup of the agentUniverse, all functions in this class will be registered.

    Usage:
    1. Syntax in YAML: @FUNC(function_name(args))
    2. agentUniverse will automatically parse @FUNC annotation and execute corresponding function
    3. The execution result will replace the original annotation content

    Example:
       - In YAML configuration: `@FUNC(load_api_key('qwen'))`
       - The framework will call the `load_api_key` method with the argument `'qwen'`,
         and replace the annotation with the returned API key.


    Important Notes:
    - @FUNC parsing is triggered each time configuration is read, consider performance impact
    - Must implement appropriate caching strategies for database or external service calls!
   """

    @lru_cache(maxsize=10)
    def load_api_key(self, model_name: str):
        """
       Load the API key for the specified model from environment variables.

       Args:
           model_name (str): The name of the model for which the API key is required.

       Returns:
           str: The API key for the specified model if found; otherwise, an empty string.
       """
        if model_name == LLMModelEnum.QWEN.value:
            return os.getenv("DASHSCOPE_API_KEY")
        elif model_name == LLMModelEnum.DEEPSEEK.value:
            return os.getenv("DEEPSEEK_API_KEY")
        elif model_name == LLMModelEnum.OPENAI.value:
            return os.getenv("OPENAI_API_KEY")
        elif model_name == LLMModelEnum.CLAUDE.value:
            return os.getenv("ANTHROPIC_API_KEY")
        elif model_name == LLMModelEnum.KIMI.value:
            return os.getenv("KIMI_API_KEY")
        elif model_name == LLMModelEnum.ZHIPU.value:
            return os.getenv("ZHIPU_API_KEY")
        elif model_name == LLMModelEnum.BAICHUAN.value:
            return os.getenv("BAICHUAN_API_KEY")
        elif model_name == LLMModelEnum.GEMINI.value:
            return os.getenv("GEMINI_API_KEY")
        elif model_name == LLMModelEnum.WENXIN.value:
            return os.getenv("QIANFAN_AK")
        else:
            return ""
