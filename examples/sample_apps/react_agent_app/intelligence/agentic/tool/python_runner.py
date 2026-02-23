# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/12 16:36
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: python_runner.py

import re
import subprocess
import sys
import tempfile

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class PythonRunner(Tool):
    """Python code execution tool.

    Executes Python code snippets and returns the output.
    Supports extracting code from markdown code blocks.
    """

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
        pattern = re.compile(r"```python(.*?)``", re.DOTALL)
        matches = pattern.findall(input)
        if len(matches) == 0:
            pattern = re.compile(r"```py(.*?)``", re.DOTALL)
            matches = pattern.findall(input)
        if len(matches) == 0:
            res = self._run_code(input)
        else:
            res = self._run_code(matches[0])
        if res == "" or res is None:
            return "ERROR: 你的python代码中没有使用print输出任何内容，请参考工具示例"
        else:
            return res
