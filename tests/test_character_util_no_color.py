import io
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from agentuniverse.base.util.character_util import print_gradient_text


class TestNoColor(unittest.TestCase):
    def render(self, value):
        with patch.dict(os.environ):
            os.environ.pop("NO_COLOR", None)
            if value is not None:
                os.environ["NO_COLOR"] = value

            output = io.StringIO()
            with redirect_stdout(output):
                print_gradient_text("hello", [33])
            return output.getvalue()

    def test_nonempty_no_color_outputs_plain_text(self):
        for value in ("1", "0", "true"):
            with self.subTest(value=value):
                self.assertEqual(self.render(value), "hello\n")

    def test_unset_or_empty_keeps_color(self):
        for value in (None, ""):
            with self.subTest(value=value):
                self.assertIn("\033[38;5;33m", self.render(value))


if __name__ == "__main__":
    unittest.main()
