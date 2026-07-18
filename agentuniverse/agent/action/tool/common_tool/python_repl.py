# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: python_repl.py

import re
from typing import Any

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from loguru import logger
from pydantic import Field


def _get_python_repl():
    try:
        from langchain_community.utilities import PythonREPL
    except ImportError as exc:
        raise ImportError(
            "langchain-community is required to use PythonREPLTool. "
            "Install it with `pip install langchain-community`."
        ) from exc
    return PythonREPL()


class PythonREPLTool(Tool):
    """Tool that executes Python code provided by an agent.

    .. warning::
        **Security:** this tool runs **arbitrary Python code on the host**
        through ``exec``. It performs **no** sandboxing, subprocess isolation,
        or resource limiting. A prompt injection that reaches this tool
        escalates directly to arbitrary code execution and full host compromise.

        Because of that, the tool is **disabled by default**. Set
        ``allow_code_execution: True`` (e.g. in the tool yaml) to opt in, and
        only do so in a fully trusted, isolated environment. Do not equip an
        agent that processes untrusted input (documents, web pages, chat
        messages) with this tool.

    Attributes:
        allow_code_execution (bool): Explicit opt-in flag. Defaults to ``False``
            so the tool refuses to execute code until an integrator acknowledges
            the risk above.
    """

    client: Any = Field(default=None)
    allow_code_execution: bool = False

    def _get_client(self):
        if self.client is None:
            self.client = _get_python_repl()
        return self.client

    def execute(self, input: str):
        """Execute the Python code extracted from ``input``.

        Refuses to run unless ``allow_code_execution`` is ``True``.
        """
        if not self.allow_code_execution:
            logger.warning(
                "PythonREPLTool.execute is disabled (allow_code_execution=False). "
                "It runs arbitrary code via exec() with no sandboxing; set "
                "allow_code_execution=True to opt in only for trusted environments."
            )
            return ("ERROR: PythonREPLTool is disabled by default because it "
                    "executes arbitrary code on the host without sandboxing. Set "
                    "`allow_code_execution: True` to opt in, and only do so in a "
                    "trusted, isolated environment.")

        pattern = re.compile(r"```python(.*?)``", re.DOTALL)
        matches = pattern.findall(input)
        if len(matches) == 0:
            pattern = re.compile(r"```py(.*?)``", re.DOTALL)
            matches = pattern.findall(input)
        client = self._get_client()
        if len(matches) == 0:
            return client.run(input)
        res = client.run(matches[0])
        if res == "" or res is None:
            return "ERROR: 你的python代码中没有使用print输出任何内容，请参考工具示例"
        else:
            return res
