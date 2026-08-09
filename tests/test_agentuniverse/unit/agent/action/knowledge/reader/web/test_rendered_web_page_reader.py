import contextlib
import io
import unittest
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.web.rendered_web_page_reader import (
    RenderedWebPageReader,
)


class TestRenderedWebPageReader(unittest.TestCase):

    def test_load_data_does_not_print_debug_output(self):
        reader = RenderedWebPageReader()
        stdout = io.StringIO()

        with patch.object(reader, "_render_and_get_html", return_value="<html></html>"), \
                patch(
                    "agentuniverse.agent.action.knowledge.reader.web.web_page_reader"
                    ".WebPageReader._extract_main_text",
                    return_value=("content", {"extractor": "mock"}),
                ), \
                contextlib.redirect_stdout(stdout):
            documents = reader._load_data("https://example.com")

        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(documents[0].text, "content")
        self.assertTrue(documents[0].metadata["rendered"])


if __name__ == "__main__":
    unittest.main()
