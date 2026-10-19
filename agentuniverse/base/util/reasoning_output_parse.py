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
        """Extract the first generation's text and optional chat reasoning.

        Text generations have no message and produce a text-only mapping.
        Chat generations retain the existing additional-kwargs behavior.

        Args:
            result: Candidate text or chat generations, including chunks.
            partial: Whether the result is partial; extraction is unchanged.

        Returns:
            A mapping containing text and, when chat additional kwargs are
            present, reasoning_content. An empty candidate list returns "".
        """
        if not result:
            return ""

        reasoning_text = ""
        message = getattr(result[0], "message", None)
        additional_kwargs = getattr(message, "additional_kwargs", None)
        if additional_kwargs:
            if "reasoning_content" in additional_kwargs:
                reasoning_text = additional_kwargs.get("reasoning_content")
            return {
                "text": result[0].text,
                "reasoning_content": reasoning_text
            }
        return {
            "text": result[0].text,
        }
