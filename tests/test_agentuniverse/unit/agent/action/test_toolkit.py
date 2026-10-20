import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from agentuniverse.agent.action.toolkit.toolkit import Toolkit


class _BrokenValue:
    def items(self):
        raise RuntimeError("bad config")


class _TestToolkit(Toolkit):
    def _initialize_by_component_configer(self, component_configer):
        return self


class ToolkitTest(unittest.TestCase):

    def test_initialize_config_error_does_not_print_to_stdout(self):
        toolkit = _TestToolkit()
        configer = SimpleNamespace(
            configer=SimpleNamespace(value=_BrokenValue()),
            name="toolkit",
            description="description",
            include=[],
        )
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            toolkit.initialize_by_component_configer(configer)

        self.assertEqual("", stdout.getvalue())
        self.assertEqual("toolkit", toolkit.name)


if __name__ == "__main__":
    unittest.main()
