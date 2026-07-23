import io
import unittest
from contextlib import redirect_stdout

from agentuniverse.base.config.custom_configer.default_llm_configer import DefaultLLMConfiger


class DefaultLLMConfigerTest(unittest.TestCase):

    def test_missing_config_does_not_print_to_stdout(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            configer = DefaultLLMConfiger("missing_default_llm.toml")

        self.assertIsNone(configer.default_llm)
        self.assertEqual("", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
