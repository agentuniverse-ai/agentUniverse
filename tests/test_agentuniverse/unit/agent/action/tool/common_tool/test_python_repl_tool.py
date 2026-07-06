import unittest
from unittest.mock import patch, MagicMock

from agentuniverse.agent.action.tool.common_tool.python_repl import (
    PythonREPLTool,
)
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.base.config.application_configer.app_configer import AppConfiger


class TestPythonREPLTool(unittest.TestCase):
    def setUp(self):
        app_configer = AppConfiger()
        ApplicationConfigManager().app_configer = app_configer
        self.tool = PythonREPLTool()
        self.tool.client = MagicMock()
        self.tool.client.run = MagicMock(side_effect=lambda x: x)

    def test_normal_execution(self):
        """Test that normal Python code executes fine."""
        result = self.tool.execute("print('hello')")
        self.assertNotIn("ERROR", result)

    def test_code_block_extraction(self):
        """Test that code is extracted from markdown code blocks."""
        self.tool.client.run = MagicMock(return_value="42")
        result = self.tool.execute("```python\nprint(42)\n```")
        self.tool.client.run.assert_called_once()
        self.assertEqual(result, "42")

    def test_py_block_extraction(self):
        """Test that ```py blocks are also supported."""
        self.tool.client.run = MagicMock(return_value="42")
        result = self.tool.execute("```py\nprint(42)\n```")
        self.tool.client.run.assert_called_once()
        self.assertEqual(result, "42")

    def test_empty_output(self):
        """Test that empty output gives a helpful error."""
        self.tool.client.run = MagicMock(return_value="")
        result = self.tool.execute("x = 1")
        self.assertIn("ERROR", result)

    def test_blocks_import_os(self):
        """Test that 'import os' is blocked by sandbox."""
        result = self.tool.execute("import os\nos.system('id')")
        self.assertIn("ERROR", result)
        self.assertIn("Blocked", result)
        self.tool.client.run.assert_not_called()

    def test_blocks_subprocess(self):
        """Test that subprocess usage is blocked."""
        result = self.tool.execute("import subprocess\nsubprocess.run(['id'])")
        self.assertIn("ERROR", result)
        self.assertIn("Blocked", result)

    def test_blocks_dunder_import(self):
        """Test that __import__ is blocked."""
        result = self.tool.execute("__import__('os').system('id')")
        self.assertIn("ERROR", result)
        self.assertIn("Blocked", result)

    def test_blocks_open_absolute_path(self):
        """Test that opening absolute paths is blocked."""
        result = self.tool.execute("open('/etc/passwd').read()")
        self.assertIn("ERROR", result)
        self.assertIn("Blocked", result)

    def test_blocks_eval(self):
        """Test that eval() is blocked."""
        result = self.tool.execute("eval('1+1')")
        self.assertIn("ERROR", result)

    def test_sandbox_disabled_allows_dangerous(self):
        """Test that disabling sandbox allows dangerous code."""
        self.tool.sandbox_enabled = False
        self.tool.client.run = MagicMock(return_value="ok")
        result = self.tool.execute("import os\nos.system('echo hi')")
        self.tool.client.run.assert_called_once()
        self.assertNotIn("ERROR", result)

    def test_safe_code_passes_sandbox(self):
        """Test that safe code passes the sandbox check."""
        self.tool.client.run = MagicMock(return_value="4")
        result = self.tool.execute("print(2+2)")
        self.assertEqual(result, "4")
        self.tool.client.run.assert_called_once()

    def test_custom_blocked_patterns(self):
        """Test that custom patterns can be added."""
        self.tool.blocked_patterns = [r"for\s+.*\s+in\s+"]
        result = self.tool.execute("for i in range(10):\n    print(i)")
        self.assertIn("ERROR", result)
        self.assertIn("Blocked", result)


if __name__ == "__main__":
    unittest.main()
