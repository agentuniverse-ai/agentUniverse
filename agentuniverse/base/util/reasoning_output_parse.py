# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/14 14:47
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: reasoning_output_parse.py

from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers.base import T
from langchain_core.outputs import Generation


class ReasoningOutputParser(StrOutputParser):
    def parse_result(self, result: List[Generation], *, partial: bool = False) -> T:
        if not result:
            return ""

        generation = result[0]
        message = getattr(generation, "message", None)
        additional_kwargs = getattr(message, "additional_kwargs", None)
        if additional_kwargs:
            reasoning_text = additional_kwargs.get("reasoning_content", "")
            return {
                "text": generation.text,
                "reasoning_content": reasoning_text
            }
        return {
            "text": generation.text,
        }
