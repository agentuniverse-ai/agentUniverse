"""Regression tests for ViewFileTool line bounds and bounded-memory reads."""

import builtins
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from agentuniverse.agent.action.tool.common_tool.view_file_tool import ViewFileTool
from agentuniverse.agent.action.tool.tool import ToolInput

_READLINES_ERROR = "ViewFileTool must not call readlines()"


class _NoReadlinesFile:
    """File wrapper that fails if the implementation buffers the whole file."""

    def __init__(self, file_object) -> None:
        self._file_object = file_object

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._file_object.close()
        return False

    def __iter__(self):
        return iter(self._file_object)

    def readlines(self, *args, **kwargs):
        raise AssertionError(_READLINES_ERROR)


class ViewFileBoundsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.tool = ViewFileTool(base_dir=self.temp_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def write_file(self, name: str, content: str) -> str:
        path = os.path.join(self.temp_dir, name)
        with open(path, "w", encoding="utf-8", newline="") as output:
            output.write(content)
        return path

    def execute(self, **kwargs) -> dict:
        return json.loads(self.tool.execute(**kwargs))

    def test_negative_start_line_is_rejected(self) -> None:
        self.write_file("sample.txt", "one\ntwo\nthree\n")

        result = self.execute(file_path="sample.txt", start_line=-1)

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"], "start_line must be greater than or equal to 0")

    def test_negative_end_line_is_rejected_even_when_start_is_negative(self) -> None:
        self.write_file("sample.txt", "one\ntwo\nthree\n")

        result = self.execute(file_path="sample.txt", start_line=-2, end_line=-1)

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"], "start_line must be greater than or equal to 0")

    def test_negative_end_line_is_rejected_on_its_own(self) -> None:
        self.write_file("sample.txt", "one\ntwo\nthree\n")

        result = self.execute(file_path="sample.txt", end_line=-1)

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"], "end_line must be greater than or equal to 0")

    def test_empty_file_returns_an_empty_success(self) -> None:
        self.write_file("empty.txt", "")

        result = self.execute(file_path="empty.txt")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], "")
        self.assertEqual(result["total_lines"], 0)
        self.assertEqual(result["start_line"], 0)
        self.assertEqual(result["end_line"], 0)

    def test_file_without_trailing_newline_keeps_the_last_line(self) -> None:
        self.write_file("sample.txt", "one\ntwo\nthree")

        result = self.execute(file_path="sample.txt", start_line=2)

        self.assertEqual(result["content"], "three")
        self.assertEqual(result["total_lines"], 3)
        self.assertEqual(result["end_line"], 2)

    def test_start_beyond_eof_returns_an_empty_result(self) -> None:
        self.write_file("sample.txt", "one\ntwo\nthree\n")

        result = self.execute(file_path="sample.txt", start_line=99)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], "")
        self.assertEqual(result["total_lines"], 3)
        self.assertEqual(result["start_line"], 99)

    def test_end_beyond_eof_is_clamped_to_the_last_line(self) -> None:
        self.write_file("sample.txt", "one\ntwo\nthree\n")

        result = self.execute(file_path="sample.txt", start_line=1, end_line=99)

        self.assertEqual(result["content"], "two\nthree\n")
        self.assertEqual(result["end_line"], 2)
        self.assertEqual(result["total_lines"], 3)

    def test_equal_bounds_return_no_content(self) -> None:
        self.write_file("sample.txt", "one\ntwo\nthree\n")

        result = self.execute(file_path="sample.txt", start_line=2, end_line=2)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], "")
        self.assertEqual(result["start_line"], 2)
        self.assertEqual(result["end_line"], 1)

    def test_range_from_a_large_file_returns_only_that_range(self) -> None:
        lines = [f"line {number}\n" for number in range(1, 50001)]
        self.write_file("large.log", "".join(lines))

        result = self.execute(file_path="large.log", start_line=49990)

        self.assertEqual(result["total_lines"], 50000)
        self.assertEqual(result["content"], "".join(lines[49990:]))
        self.assertTrue(result["content"].startswith("line 49991\n"))

    def test_preview_does_not_buffer_the_whole_file(self) -> None:
        self.write_file("sample.txt", "one\ntwo\nthree\n")
        real_open = builtins.open

        def guarded_open(*args, **kwargs):
            return _NoReadlinesFile(real_open(*args, **kwargs))

        with patch("builtins.open", guarded_open):
            result = self.execute(file_path="sample.txt", start_line=1, end_line=2)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], "two\n")

    def test_invalid_utf8_is_reported_with_the_byte_offset(self) -> None:
        path = os.path.join(self.temp_dir, "binary.dat")
        with open(path, "wb") as output:
            output.write(b"ok\n\xffbad\n")

        result = self.execute(file_path="binary.dat")

        self.assertEqual(result["status"], "error")
        self.assertIn("not valid UTF-8", result["error"])
        self.assertIn("byte offset", result["error"])

    def test_tool_input_without_a_path_returns_an_error(self) -> None:
        result = json.loads(self.tool.execute(ToolInput({})))

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"], "file_path must be a non-empty string")

    def test_directory_is_not_treated_as_a_file(self) -> None:
        result = self.execute(file_path=".")

        self.assertEqual(result["status"], "error")
        self.assertIn("File not found", result["error"])


if __name__ == "__main__":
    unittest.main()
