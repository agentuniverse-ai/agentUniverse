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
    """Output parser that extracts both the generated text and the model reasoning content from generation results.
    """
    def parse_result(self, result: List[Generation], *, partial: bool = False) -> T:
        """Parse generation results into a dict with the text and, when present, the reasoning content.

        Args:
            result(List[Generation]): The generation results to parse.
            partial(bool): Whether partial output should be parsed.

        Returns:
            A dict containing the text and optionally the reasoning_content, or an empty string when no result is given.
        """
        if not result:
            return ""

        reasoning_text = ""
        if result[0].message.additional_kwargs:
            additional_kwargs = getattr(result[0].message, "additional_kwargs")
            if additional_kwargs and "reasoning_content" in additional_kwargs:
                reasoning_text = result[0].message.additional_kwargs.get("reasoning_content")
            return {
                "text": result[0].text,
                "reasoning_content": reasoning_text
            }
        return {
            "text": result[0].text,
        }
