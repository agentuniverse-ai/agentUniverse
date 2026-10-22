"""Fenced Python must not end at a pair of backticks inside its source."""

from unittest.mock import Mock

import pytest

from agentuniverse.agent.action.tool.common_tool.python_repl import PythonREPLTool


@pytest.mark.parametrize("language", ["python", "py"])
@pytest.mark.parametrize("code", ['print("``")', 'value = "a``b"\nprint(value)', 'print(42)'])
def test_fenced_code_requires_three_closing_backticks(language, code):
    tool = PythonREPLTool(allow_code_execution=True)
    client = Mock()
    client.run.return_value = "output"
    tool.client = client
    assert tool.execute(f"Explanation\n```{language}\n{code}\n```\nAfter") == "output"
    client.run.assert_called_once_with(f"\n{code}\n")


def test_plain_source_passes_through_unchanged():
    tool = PythonREPLTool(allow_code_execution=True)
    client = Mock()
    client.run.return_value = "raw output"
    tool.client = client
    assert tool.execute('print("``")') == "raw output"
    client.run.assert_called_once_with('print("``")')


def test_first_matching_block_policy_is_unchanged():
    tool = PythonREPLTool(allow_code_execution=True)
    client = Mock()
    client.run.return_value = "first"
    tool.client = client
    tool.execute('```python\nprint(1)\n```\n```python\nprint(2)\n```')
    client.run.assert_called_once_with('\nprint(1)\n')


def test_default_disabled_gate_does_not_invoke_client():
    tool = PythonREPLTool()
    client = Mock()
    tool.client = client
    assert "disabled" in tool.execute('```python\nprint("``")\n```')
    client.run.assert_not_called()
