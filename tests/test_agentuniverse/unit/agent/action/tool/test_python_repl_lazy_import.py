#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

from agentuniverse.agent.action.tool.common_tool import python_repl as repl_module
from agentuniverse.agent.action.tool.common_tool.python_repl import PythonREPLTool


class FakePythonREPL:
    def __init__(self):
        self.inputs = []

    def run(self, code):
        self.inputs.append(code)
        return "ok"


class TestPythonREPLLazyImport(unittest.TestCase):
    def test_disabled_tool_does_not_load_python_repl(self):
        tool = PythonREPLTool(allow_code_execution=False)

        with patch.object(
            repl_module,
            "_get_python_repl",
            side_effect=AssertionError("client should not be loaded"),
        ):
            result = tool.execute("print('hello')")

        self.assertIn("disabled by default", result)

    def test_enabled_tool_loads_client_lazily(self):
        fake_client = FakePythonREPL()
        tool = PythonREPLTool(allow_code_execution=True)

        with patch.object(
            repl_module,
            "_get_python_repl",
            return_value=fake_client,
        ) as load_client:
            result = tool.execute("print('hello')")

        load_client.assert_called_once_with()
        self.assertEqual(result, "ok")
        self.assertEqual(fake_client.inputs, ["print('hello')"])

    def test_existing_client_is_reused(self):
        fake_client = FakePythonREPL()
        tool = PythonREPLTool(client=fake_client, allow_code_execution=True)

        with patch.object(
            repl_module,
            "_get_python_repl",
            side_effect=AssertionError("existing client should be reused"),
        ):
            result = tool.execute("```python\nprint('hello')\n```")

        self.assertEqual(result, "ok")
        self.assertEqual(fake_client.inputs, ["\nprint('hello')\n"])


if __name__ == "__main__":
    unittest.main()
