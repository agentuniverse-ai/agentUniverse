# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: python_repl.py

import re
from typing import List, Optional

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from langchain_community.utilities import PythonREPL
from pydantic import Field

_DEFAULT_BLOCKED_PATTERNS = [
    r"__import__\s*\(",
    r"\bimport\s+os\b",
    r"\bfrom\s+os\b",
    r"\bimport\s+subprocess\b",
    r"\bfrom\s+subprocess\b",
    r"\bimport\s+shutil\b",
    r"\bfrom\s+shutil\b",
    r"\bimport\s+socket\b",
    r"\bfrom\s+socket\b",
    r"\bimport\s+ctypes\b",
    r"\bfrom\s+ctypes\b",
    r"\bimport\s+sys\b",
    r"\bfrom\s+sys\b",
    r"\bopen\s*\([^)]*['\"]?[/~]",
    r"os\.system\s*\(",
    r"os\.popen\s*\(",
    r"subprocess\.",
    r"eval\s*\(",
    r"exec\s*\(",
    r"compile\s*\(",
    r"globals\s*\(\s*\)",
    r"locals\s*\(\s*\)",
    r"getattr\s*\(",
    r"setattr\s*\(",
    r"delattr\s*\(",
]


class PythonREPLTool(Tool):
    """Python REPL tool that executes Python code.

    By default, a lightweight input-level sandbox blocks dangerous
    patterns (e.g. ``__import__``, ``os.system``, ``subprocess``).
    Set ``sandbox_enabled=False`` to disable it.

    Warning:
        Even with the sandbox enabled, this tool still uses ``exec()``
        and is not safe for untrusted input.  Consider running it in a
        separate subprocess or container with restricted permissions.
    """

    client: PythonREPL = Field(default_factory=lambda: PythonREPL())
    sandbox_enabled: bool = True
    blocked_patterns: List[str] = Field(
        default_factory=lambda: list(_DEFAULT_BLOCKED_PATTERNS)
    )

    def _check_safety(self, code: str) -> Optional[str]:
        """Return a reason string if the code is blocked, else None."""
        for pattern in self.blocked_patterns:
            if re.search(pattern, code):
                return f"Blocked by sandbox pattern: {pattern}"
        return None

    def execute(self, input: str):
        """Execute Python code extracted from the input string."""
        pattern = re.compile(r"```python(.*?)``", re.DOTALL)
        matches = pattern.findall(input)
        if len(matches) == 0:
            pattern = re.compile(r"```py(.*?)``", re.DOTALL)
            matches = pattern.findall(input)
        code = matches[0] if matches else input

        if self.sandbox_enabled:
            reason = self._check_safety(code)
            if reason:
                return f"ERROR: Code execution blocked by sandbox. {reason}"

        res = self.client.run(code)
        if res == "" or res is None:
            return "ERROR: 你的python代码中没有使用print输出任何内容，请参考工具示例"
        return res
