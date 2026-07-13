# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_python_repl.py

import os
import tempfile
import unittest

from agentuniverse.agent.action.tool.common_tool.python_repl import PythonREPLTool
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer


def _repo_root() -> str:
    """Walk up from this test file to the repository root.

    The repository root is the closest ancestor that contains both the
    ``agentuniverse`` package and the ``examples`` directory.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    current = here
    while True:
        if os.path.isdir(os.path.join(current, "agentuniverse")) and os.path.isdir(os.path.join(current, "examples")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            # Unreachable for files checked into this repo; kept as a guard.
            raise RuntimeError
        current = parent


# Built-in tool YAMLs that ship the common PythonREPLTool. These demo apps
# exist to showcase code execution, so they are expected to opt in.
_OPT_IN_BUILTIN_YAMLS = [
    os.path.join(
        _repo_root(), "examples/sample_standard_app/intelligence/agentic/tool/buildin/" "python_repl_tool.yaml"
    ),
    os.path.join(_repo_root(), "examples/sample_apps/difizen_app/intelligence/agentic/tool/" "python_repl_tool.yaml"),
    os.path.join(
        _repo_root(),
        "examples/third_party_examples/apps/app_with_goole_search_tool/"
        "intelligence/agentic/tool/buildin/python_repl_tool.yaml",
    ),
]


def _tool_from_yaml(path: str) -> PythonREPLTool:
    """Build a PythonREPLTool from a tool yaml through the real config path."""
    configer = Configer(path).load()
    tool_configer = ToolConfiger(configer).load_by_configer(configer)
    tool = PythonREPLTool()
    tool.initialize_by_component_configer(tool_configer)
    return tool


class PythonREPLToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = PythonREPLTool()

    def test_disabled_by_default(self):
        # By default the tool must refuse to execute code (issue #570).
        result = self.tool.execute("print('pwned')")

        self.assertIsInstance(result, str)
        self.assertIn("allow_code_execution", result)
        self.assertIn("disabled", result.lower())

    def test_opt_in_executes(self):
        self.tool.allow_code_execution = True
        result = self.tool.execute("print(2 ** 10)")

        # When opted in the code actually runs and prints 1024.
        self.assertNotIn("disabled", result.lower())
        self.assertIn("1024", str(result))


class PythonREPLToolConfigTest(unittest.TestCase):
    """Config-level tests: the opt-in flag must flow from yaml -> tool."""

    def test_default_config_is_disabled(self):
        # A yaml without allow_code_execution must leave the tool disabled.
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "python_repl_tool.yaml")
            with open(path, "w", encoding="utf-8") as f:
                f.write(
                    "name: 'python_runner'\n"
                    "description: 'demo'\n"
                    "tool_type: 'api'\n"
                    "input_keys: ['input']\n"
                    "metadata:\n"
                    "  type: 'TOOL'\n"
                    "  module: "
                    "'agentuniverse.agent.action.tool.common_tool.python_repl'\n"
                    "  class: 'PythonREPLTool'\n"
                )
            tool = _tool_from_yaml(path)

        self.assertFalse(tool.allow_code_execution)
        result = tool.execute("print('pwned')")
        self.assertIsInstance(result, str)
        self.assertIn("allow_code_execution", result)
        self.assertIn("disabled", result.lower())

    def test_config_opt_in_executes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "python_repl_tool.yaml")
            with open(path, "w", encoding="utf-8") as f:
                f.write(
                    "name: 'python_runner'\n"
                    "description: 'demo'\n"
                    "tool_type: 'api'\n"
                    "input_keys: ['input']\n"
                    "allow_code_execution: true\n"
                    "metadata:\n"
                    "  type: 'TOOL'\n"
                    "  module: "
                    "'agentuniverse.agent.action.tool.common_tool.python_repl'\n"
                    "  class: 'PythonREPLTool'\n"
                )
            tool = _tool_from_yaml(path)

        self.assertTrue(tool.allow_code_execution)
        result = tool.execute("print(2 + 3)")
        self.assertNotIn("disabled", result.lower())
        self.assertIn("5", str(result))

    def test_builtin_demo_yamls_opt_in(self):
        # Regression guard: the shipped built-in python_runner yamls must keep
        # the policy explicit by opting in, so the demos keep working instead of
        # silently returning the disabled error.
        self.assertTrue(_OPT_IN_BUILTIN_YAMLS, "expected at least one built-in yaml to be checked")
        for path in _OPT_IN_BUILTIN_YAMLS:
            with self.subTest(yaml=path):
                self.assertTrue(os.path.isfile(path), f"missing built-in yaml: {path}")
                tool = _tool_from_yaml(path)
                self.assertTrue(
                    tool.allow_code_execution, f"{path} must set allow_code_execution: true to keep the " "demo working"
                )
                result = tool.execute("print(7 * 6)")
                self.assertNotIn("disabled", result.lower())
                self.assertIn("42", str(result))


if __name__ == '__main__':
    unittest.main()
