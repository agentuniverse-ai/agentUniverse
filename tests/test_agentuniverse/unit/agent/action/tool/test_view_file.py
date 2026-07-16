# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/22 19:16
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: test_view_file.py

import os
import json
import shutil
import tempfile
import unittest

from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.view_file_tool import ViewFileTool


class ViewFileToolTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.tool = ViewFileTool(base_dir=self.temp_dir)
        self.temp_file_path = os.path.join(self.temp_dir, 'test.txt')

        test_content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
        with open(self.temp_file_path, 'w', encoding='utf-8') as temp_file:
            temp_file.write(test_content)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_view_entire_file(self):
        tool_input = ToolInput({
            'file_path': self.temp_file_path
        })

        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['file_path'], os.path.realpath(self.temp_file_path))
        self.assertEqual(result['content'],
                         "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
        self.assertEqual(result['total_lines'], 5)

    def test_view_specific_lines(self):
        tool_input = ToolInput({
            'file_path': self.temp_file_path,
            'start_line': 1,
            'end_line': 3
        })

        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['content'], "Line 2\nLine 3\n")
        self.assertEqual(result['start_line'], 1)
        self.assertEqual(result['end_line'], 2)

    def test_view_specific_lines_with_string_numbers(self):
        tool_input = ToolInput({
            'file_path': self.temp_file_path,
            'start_line': '1',
            'end_line': '3'
        })

        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['content'], "Line 2\nLine 3\n")
        self.assertEqual(result['start_line'], 1)
        self.assertEqual(result['end_line'], 2)

    def test_invalid_line_number_returns_error(self):
        result_json = self.tool.execute(
            file_path=self.temp_file_path,
            start_line='first'
        )
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'error')
        self.assertIn('start_line must be an integer', result['error'])

    def test_fractional_line_number_returns_error(self):
        result_json = self.tool.execute(
            file_path=self.temp_file_path,
            start_line=1.9
        )
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'error')
        self.assertIn('start_line must be an integer', result['error'])

    def test_fractional_line_number_string_returns_error(self):
        result_json = self.tool.execute(
            file_path=self.temp_file_path,
            start_line='1.9'
        )
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'error')
        self.assertIn('start_line must be an integer', result['error'])

    def test_boolean_line_number_returns_error(self):
        result_json = self.tool.execute(
            file_path=self.temp_file_path,
            start_line=True
        )
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'error')
        self.assertIn('start_line must be an integer', result['error'])

    def test_non_canonical_integer_string_returns_error(self):
        result_json = self.tool.execute(
            file_path=self.temp_file_path,
            start_line='01'
        )
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'error')
        self.assertIn('start_line must be a canonical integer string', result['error'])

    def test_invalid_file_path(self):
        tool_input = ToolInput({
            'file_path': 'nonexistent/file.txt'
        })

        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'error')
        self.assertIn('File not found', result['error'])

    def test_reject_path_traversal(self):
        outside_file = tempfile.NamedTemporaryFile(delete=False)
        outside_file.write(b'secret')
        outside_file.close()
        self.addCleanup(lambda: os.path.exists(outside_file.name) and os.unlink(outside_file.name))

        result_json = self.tool.execute(file_path=outside_file.name)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'error')
        self.assertIn('escapes the allowed directory', result['error'])


if __name__ == '__main__':
    unittest.main()
