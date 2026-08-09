import importlib
import io
import sys
import types
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch


class _BrokenComponent:
    @property
    def component_type(self):
        raise RuntimeError("bad component")


def _install_component_stubs():
    component_base_module = types.SimpleNamespace(ComponentBase=object)
    component_enum_module = types.SimpleNamespace(
        ComponentEnum=types.SimpleNamespace(
            LLM=types.SimpleNamespace(value="llm"),
            TOOL=types.SimpleNamespace(value="tool"),
        )
    )
    return patch.dict(
        sys.modules,
        {
            "agentuniverse.base.component.component_base": component_base_module,
            "agentuniverse.base.component.component_enum": component_enum_module,
        },
    )


class SystemUtilLoggingTest(unittest.TestCase):

    def test_is_system_builtin_error_does_not_print_to_stdout(self):
        with _install_component_stubs():
            system_util = importlib.import_module("agentuniverse.base.util.system_util")

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            result = system_util.is_system_builtin(_BrokenComponent())

        self.assertFalse(result)
        self.assertEqual("", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
