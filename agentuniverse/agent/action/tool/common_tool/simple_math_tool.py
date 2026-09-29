# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: simple_math_tool.py


from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class AddTool(Tool):
    """A tool that computes the sum of two numbers.

    The input is expected to be a string of two comma-separated numbers,
    e.g. "1,2".
    """

    def execute(self, input: str):
        """Add two comma-separated numbers.

        Args:
            input: A string of two comma-separated numbers, e.g. "1,2".

        Returns:
            The sum of the two numbers as a float.
        """
        a, b = input.split(',')
        result = float(a) + float(b)
        return result

    async def async_execute(self, input: str):
        """Asynchronously add two comma-separated numbers.

        Args:
            input: A string of two comma-separated numbers, e.g. "1,2".

        Returns:
            The sum of the two numbers as a float.
        """
        a, b = input.split(',')
        result = float(a) + float(b)
        return result


class SubtractTool(Tool):
    """A tool that subtracts the second number from the first.

    The input is expected to be a string of two comma-separated numbers,
    e.g. "5,2".
    """

    def execute(self, input: str):
        """Subtract the second number from the first.

        Args:
            input: A string of two comma-separated numbers, e.g. "5,2".

        Returns:
            The difference of the two numbers as a float.
        """
        a, b = input.split(',')
        result = float(a) - float(b)
        return result

    async def async_execute(self, input: str):
        """Asynchronously subtract the second number from the first.

        Args:
            input: A string of two comma-separated numbers, e.g. "5,2".

        Returns:
            The difference of the two numbers as a float.
        """
        a, b = input.split(',')
        result = float(a) - float(b)
        return result


class MultiplyTool(Tool):
    """A tool that computes the product of two numbers.

    The input is expected to be a string of two comma-separated numbers,
    e.g. "3,4".
    """

    def execute(self, input: str):
        """Multiply two comma-separated numbers.

        Args:
            input: A string of two comma-separated numbers, e.g. "3,4".

        Returns:
            The product of the two numbers as a float.
        """
        a, b = input.split(',')
        result = float(a) * float(b)
        return result

    async def async_execute(self, input: str):
        """Asynchronously multiply two comma-separated numbers.

        Args:
            input: A string of two comma-separated numbers, e.g. "3,4".

        Returns:
            The product of the two numbers as a float.
        """
        a, b = input.split(',')
        result = float(a) * float(b)
        return result


class DivideTool(Tool):
    """A tool that divides the first number by the second.

    The input is expected to be a string of two comma-separated numbers,
    e.g. "8,2".
    """

    def execute(self, input: str):
        """Divide the first number by the second.

        Args:
            input: A string of two comma-separated numbers, e.g. "8,2".

        Returns:
            The quotient of the two numbers as a float.

        Raises:
            ZeroDivisionError: If the second number is zero.
        """
        a, b = input.split(',')
        result = float(a) / float(b)
        return result

    async def async_execute(self, input: str):
        """Asynchronously divide the first number by the second.

        Args:
            input: A string of two comma-separated numbers, e.g. "8,2".

        Returns:
            The quotient of the two numbers as a float.

        Raises:
            ZeroDivisionError: If the second number is zero.
        """
        a, b = input.split(',')
        result = float(a) / float(b)
        return result
