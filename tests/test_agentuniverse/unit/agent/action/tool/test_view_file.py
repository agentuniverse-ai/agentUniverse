# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/22 19:16
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: test_view_file.py

import os
import json
import tempfile
import unittest

from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.view_file_tool import ViewFileTool


class ViewFileToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = ViewFileTool()
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file_path = self.temp_file.name

        test_content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
        self.temp_file.write(test_content.encode('utf-8'))
        self.temp_file.close()

    def tearDown(self):
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)

    def test_view_entire_file(self):
        tool_input = ToolInput({
            'file_path': self.temp_file_path
        })

        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['file_path'], self.temp_file_path)
        self.assertEqual(result['content'],
                         "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
        self.assertEqual(result['total_lines'], 5)

    def test_view_specific_lines(self):
        tool_input = ToolInput({
            'file_path': self.temp_file_path,
            'start_line': 2,
            'end_line': 4
        })

        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['content'], "Line 2\nLine 3\nLine 4\n")
        self.assertEqual(result['start_line'], 1)
        self.assertEqual(result['end_line'], 2)

    def test_invalid_file_path(self):
        tool_input = ToolInput({
            'file_path': '/path/to/nonexistent/file.txt'
        })

        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'error')
        self.assertIn('File not found', result['error'])


if __name__ == '__main__':
    unittest.main()
