import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.cloud_file_reader.feishu_reader import PublicFeishuReader


class _FailingDriver:
    def get(self, url):
        raise RuntimeError("network unavailable")


class PublicFeishuReaderTest(unittest.TestCase):

    def test_fetch_document_failure_does_not_print_to_stdout(self):
        reader = object.__new__(PublicFeishuReader)
        reader.driver = _FailingDriver()
        stdout = io.StringIO()

        with patch("time.sleep", return_value=None), redirect_stdout(stdout):
            content = reader._fetch_document_content("https://example.feishu.cn/docx/demo")

        self.assertEqual("", content)
        self.assertEqual("", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
