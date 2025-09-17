# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/28 10:51
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: dashscope_llm_channel.py
from typing import Optional

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel


class DashscopeLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def _initialize_by_component_configer(self, component_configer: ComponentConfiger) -> "DashscopeLLMChannel":
        super()._initialize_by_component_configer(component_configer)
        return self
