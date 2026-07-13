# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/22 19:16
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: test_write_file.py

import os
import json
import shutil
import tempfile
import unittest

from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.write_file_tool import WriteFileTool


class WriteFileToolTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.tool = WriteFileTool(base_dir=self.temp_dir)
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_write_new_file(self):
        file_path = os.path.join(self.temp_dir, 'test_new.txt')
        content = "This is a test file content"
        
        tool_input = ToolInput({
            'file_path': file_path,
            'content': content
        })
        
        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['file_path'], os.path.realpath(file_path))
        self.assertTrue(os.path.exists(file_path))
        
        with open(file_path, 'r') as f:
            self.assertEqual(f.read(), content)
    
    def test_append_to_file(self):
        file_path = os.path.join(self.temp_dir, 'test_append.txt')
        
        initial_content = "Initial content\n"
        tool_input = ToolInput({
            'file_path': file_path,
            'content': initial_content
        })
        self.tool.execute(tool_input)
        
        append_content = "Appended content"
        tool_input = ToolInput({
            'file_path': file_path,
            'content': append_content,
            'append': True
        })
        
        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['append_mode'], True)
        
        with open(file_path, 'r') as f:
            self.assertEqual(f.read(), initial_content + append_content)
    
    def test_create_directory_structure(self):
        file_path = os.path.join(self.temp_dir, 'nested/dir/structure/test.txt')
        content = "Test content in nested directory"
        
        tool_input = ToolInput({
            'file_path': file_path,
            'content': content
        })
        
        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(os.path.exists(file_path))
        
        self.assertTrue(os.path.isdir(os.path.join(self.temp_dir, 'nested/dir/structure')))

    def test_write_relative_path_under_base_dir(self):
        result_json = self.tool.execute(
            file_path='relative/test.txt',
            content='relative content'
        )
        result = json.loads(result_json)

        expected_path = os.path.join(self.temp_dir, 'relative', 'test.txt')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['file_path'], os.path.realpath(expected_path))
        self.assertTrue(os.path.exists(expected_path))

    def test_reject_path_traversal(self):
        outside_name = f"{os.path.basename(self.temp_dir)}_outside.txt"
        outside_path = os.path.join(os.path.dirname(self.temp_dir), outside_name)
        self.addCleanup(lambda: os.path.exists(outside_path) and os.unlink(outside_path))

        result_json = self.tool.execute(
            file_path=f'../{outside_name}',
            content='should not be written'
        )
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'error')
        self.assertIn('escapes the allowed directory', result['error'])
        self.assertFalse(os.path.exists(outside_path))


if __name__ == '__main__':
    unittest.main()
