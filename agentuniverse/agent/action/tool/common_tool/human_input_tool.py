# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: human_input_tool.py

from typing import Optional

from agentuniverse.agent.action.tool.tool import Tool

# Alias to avoid shadowing by the 'input' parameter name
_builtin_input = input


class HumanInputTool(Tool):
    """Prompt the user for text input via the terminal."""

    prompt_text: Optional[str] = "Please provide input:"

    def execute(self, input: str = "", **kwargs) -> str:
        if input:
            print(input)
        return _builtin_input(f"{self.prompt_text} ")
