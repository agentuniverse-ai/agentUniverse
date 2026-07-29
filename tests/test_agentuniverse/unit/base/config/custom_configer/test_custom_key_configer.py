import io
import unittest
from contextlib import redirect_stdout

from agentuniverse.base.config.custom_configer.custom_key_configer import CustomKeyConfiger


class CustomKeyConfigerTest(unittest.TestCase):

    def test_missing_config_does_not_print_to_stdout(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            configer = CustomKeyConfiger("missing_custom_key.toml")

        self.assertEqual({}, configer.value)
        self.assertEqual("", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
