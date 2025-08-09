# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/12 16:36
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: python_runner.py

import re

from langchain_community.utilities import PythonREPL
from pydantic import Field
from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class PythonRunner(Tool):
    """The mock search tool.

    In this tool, we mocked the search engine's answers to search for information about BYD and Warren Buffett.

    Note:
        The tool is only suitable for users searching for Buffett or BYD related queries.
        We recommend that you configure your `SERPER_API_KEY` and use google_search_tool to get information.
    """
    client: PythonREPL = Field(default_factory=lambda: PythonREPL())

    def execute(self, input: str):
        """Demonstrates the execute method of the Tool class."""
        pattern = re.compile(r"```python(.*?)``", re.DOTALL)
        matches = pattern.findall(input)
        if len(matches) == 0:
            pattern = re.compile(r"```py(.*?)``", re.DOTALL)
            matches = pattern.findall(input)
        if len(matches) == 0:
            return self.client.run(input)
        res = self.client.run(matches[0])
        if res == "" or res is None:
            return "ERROR: 你的python代码中没有使用print输出任何内容，请参考工具示例"
        else:
            return res
