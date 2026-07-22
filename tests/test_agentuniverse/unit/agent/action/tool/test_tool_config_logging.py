import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from agentuniverse.agent.action.tool.tool import Tool


class _BrokenValue:
    def items(self):
        raise RuntimeError("bad config")


class _TestTool(Tool):
    def execute(self, **kwargs):
        return kwargs


class ToolConfigLoggingTest(unittest.TestCase):

    def test_initialize_config_error_does_not_print_to_stdout(self):
        tool = _TestTool()
        configer = SimpleNamespace(
            configer=SimpleNamespace(value=_BrokenValue()),
            name="tool",
            description="description",
            tool_type=None,
            input_keys=[],
        )
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            tool.initialize_by_component_configer(configer)

        self.assertEqual("", stdout.getvalue())
        self.assertEqual("tool", tool.name)


if __name__ == "__main__":
    unittest.main()
