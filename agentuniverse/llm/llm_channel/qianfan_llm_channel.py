# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/28 10:51
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: qianfan_llm_channel.py
from typing import Optional

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel


class QianfanLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "https://qianfan.baidubce.com/v2/"

    def _initialize_by_component_configer(self, component_configer: ComponentConfiger) -> "QianfanLLMChannel":
        super()._initialize_by_component_configer(component_configer)
        return self
