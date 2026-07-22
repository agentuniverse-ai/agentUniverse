import io
import sys
import types
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.cloud.confluence_reader import ConfluenceReader


class _FakeConfluence:
    def __init__(self, *args, **kwargs):
        pass

    def get_page_by_id(self, *args, **kwargs):
        return {
            "title": "Demo",
            "version": {"number": 1},
            "body": {"view": {"value": "<p>Hello</p>"}},
        }


class ConfluenceReaderTest(unittest.TestCase):

    def test_load_data_does_not_print_page_id(self):
        reader = ConfluenceReader()
        stdout = io.StringIO()
        atlassian_module = types.SimpleNamespace(Confluence=_FakeConfluence)

        with patch.object(reader, "_resolve_cred", return_value=("https://example.com", "user", "token")), \
                patch.object(reader, "_html_to_text", return_value="Hello"), \
                patch.dict(sys.modules, {"atlassian": atlassian_module}), \
                redirect_stdout(stdout):
            documents = reader._load_data("secret-page-id")

        self.assertEqual("Hello", documents[0].text)
        self.assertNotIn("secret-page-id", stdout.getvalue())
        self.assertEqual("", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
