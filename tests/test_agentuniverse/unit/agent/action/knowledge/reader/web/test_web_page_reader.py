import contextlib
import io
import unittest
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.web.web_page_reader import WebPageReader


class TestWebPageReader(unittest.TestCase):

    def test_load_data_does_not_print_debug_output(self):
        reader = WebPageReader()
        stdout = io.StringIO()

        with patch.object(reader, "_fetch_html", return_value="<html></html>"), \
                patch.object(reader, "_extract_main_text", return_value=("content", {})), \
                contextlib.redirect_stdout(stdout):
            documents = reader._load_data("https://example.com")

        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(documents[0].text, "content")


if __name__ == "__main__":
    unittest.main()
