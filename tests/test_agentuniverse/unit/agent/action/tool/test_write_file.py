# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/22 19:16
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: test_write_file.py

import os
import json
import tempfile
import unittest

from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.write_file_tool import WriteFileTool


class WriteFileToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = WriteFileTool()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        import shutil  
        shutil.rmtree(self.temp_dir)
    
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
        self.assertEqual(result['file_path'], file_path)
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


if __name__ == '__main__':
    unittest.main()
