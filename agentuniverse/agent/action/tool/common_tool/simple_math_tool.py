# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: simple_math_tool.py


from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class AddTool(Tool):
    """adds two numbers parsed from a comma-separated input string."""
    def execute(self, input: str):
        """Parse 'a,b' from the input string, add the numbers and return the sum."""
        a, b = input.split(',')
        result = float(a) + float(b)
        return result

    async def async_execute(self, input: str):
        """Parse 'a,b' from the input string, add the numbers and return the sum."""
        a, b = input.split(',')
        result = float(a) + float(b)
        return result


class SubtractTool(Tool):
    """subtracts the second number from the first, both parsed from a comma-separated input string."""
    def execute(self, input: str):
        a, b = input.split(',')
        result = float(a) - float(b)
        return result

    async def async_execute(self, input: str):
        a, b = input.split(',')
        result = float(a) - float(b)
        return result


class MultiplyTool(Tool):
    """multiplies two numbers parsed from a comma-separated input string."""
    def execute(self, input: str):
        a, b = input.split(',')
        result = float(a) * float(b)
        return result

    async def async_execute(self, input: str):
        a, b = input.split(',')
        result = float(a) * float(b)
        return result


class DivideTool(Tool):
    """divides the first number by the second, both parsed from a comma-separated input string."""
    def execute(self, input: str):
        a, b = input.split(',')
        result = float(a) / float(b)
        return result

    async def async_execute(self, input: str):
        a, b = input.split(',')
        result = float(a) / float(b)
        return result