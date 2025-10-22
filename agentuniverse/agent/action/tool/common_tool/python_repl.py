# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: python_repl.py

import re

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from langchain_community.utilities import PythonREPL
from pydantic import Field


class PythonREPLTool(Tool):
    """Python REPL (Read-Eval-Print Loop) tool for executing Python code.

    This tool allows execution of Python code snippets and returns the output.
    It can handle both raw Python code and code wrapped in markdown code blocks.
    
    Note:
        The tool is designed for executing Python code snippets safely.
        Make sure to use print() statements to see output from your code.
        
    Attributes:
        client: PythonREPL instance for code execution
    """
    client: PythonREPL = Field(default_factory=lambda: PythonREPL())

    def execute(self, input: str):
        """Execute Python code and return the output.
        
        Args:
            input (str): Python code to execute (can be raw code or markdown wrapped)
            
        Returns:
            str: Output from the Python code execution or error message
        """
        pattern = re.compile(r"```python(.*?)``", re.DOTALL)
        matches = pattern.findall(input)
        if len(matches) == 0:
            pattern = re.compile(r"```py(.*?)``", re.DOTALL)
            matches = pattern.findall(input)
        if len(matches) == 0:
            return self.client.run(input)
        res = self.client.run(matches[0])
        if res == "" or res is None:
            return "ERROR: Your Python code did not print any output. Please refer to the tool example."
        else:
            return res
