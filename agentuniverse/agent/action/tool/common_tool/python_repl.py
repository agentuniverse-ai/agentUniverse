# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: python_repl.py

import asyncio
import re
import subprocess
import sys
import tempfile

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class PythonREPLTool(Tool):
    """Python code execution tool.

    Executes Python code snippets and returns the output.
    Supports extracting code from markdown code blocks.
    """

    def _extract_code(self, input_str: str) -> str:
        pattern = re.compile(r"```python(.*?)``", re.DOTALL)
        matches = pattern.findall(input_str)
        if len(matches) == 0:
            pattern = re.compile(r"```py(.*?)``", re.DOTALL)
            matches = pattern.findall(input_str)
        if len(matches) == 0:
            return input_str
        return matches[0]

    @staticmethod
    def _run_code(code: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=True) as f:
            f.write(code)
            f.flush()
            try:
                result = subprocess.run(
                    [sys.executable, f.name],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                output = result.stdout
                if result.returncode != 0:
                    output += result.stderr
                return output.strip()
            except subprocess.TimeoutExpired:
                return "ERROR: Code execution timed out (30s limit)"
            except Exception as e:
                return f"ERROR: {str(e)}"

    def execute(self, input: str):
        """Executes Python code and returns the output."""
        code = self._extract_code(input)
        res = self._run_code(code)
        if res == "" or res is None:
            return "ERROR: 你的python代码中没有使用print输出任何内容，请参考工具示例"
        return res

    async def async_execute(self, input: str):
        """Asynchronously executes Python code and returns the output."""
        code = self._extract_code(input)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=True) as f:
            f.write(code)
            f.flush()
            try:
                proc = await asyncio.create_subprocess_exec(
                    sys.executable, f.name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                try:
                    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
                except asyncio.TimeoutError:
                    proc.kill()
                    return "ERROR: Code execution timed out (30s limit)"
                output = stdout.decode()
                if proc.returncode != 0:
                    output += stderr.decode()
                res = output.strip()
            except Exception as e:
                return f"ERROR: {str(e)}"
        if res == "" or res is None:
            return "ERROR: 你的python代码中没有使用print输出任何内容，请参考工具示例"
        return res
