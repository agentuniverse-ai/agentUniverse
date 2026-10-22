# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/22 19:16
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: test_write_file.py

import os
import json
import stat
import shutil
import tempfile
import unittest

from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.write_file_tool import WriteFileTool


class WriteFileToolTest(unittest.TestCase):
    """Tests for the WriteFileTool covering file writing and path validation."""

    def setUp(self):
        """Create a WriteFileTool bound to a scratch temp directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.tool = WriteFileTool(base_dir=self.temp_dir)

    def tearDown(self):
        """Remove the scratch temp directory after the test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_write_new_file(self):
        """Verify a new file is written with the given content."""
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
        """Verify content is appended when append mode is enabled."""
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

    def test_string_false_append_value_overwrites_file(self):
        """Verify the string 'false' append value overwrites the existing file."""
        file_path = os.path.join(self.temp_dir, 'test_append_string_false.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('old content')

        tool_input = ToolInput({
            'file_path': file_path,
            'content': 'new content',
            'append': 'false'
        })

        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['append_mode'], False)
        with open(file_path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), 'new content')

    def test_failed_overwrite_preserves_existing_file(self):
        file_path = os.path.join(self.temp_dir, 'important.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('keep me')

        result = json.loads(self.tool.execute(file_path, 'invalid surrogate: \ud800'))

        self.assertEqual(result['status'], 'error')
        with open(file_path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), 'keep me')
        self.assertEqual(os.listdir(self.temp_dir), ['important.txt'])

    def test_typo_append_value_returns_error_without_writing(self):
        """Verify a misspelled append value errors without modifying the file."""
        file_path = os.path.join(self.temp_dir, 'test_append_typo.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('old content')

        tool_input = ToolInput({
            'file_path': file_path,
            'content': 'new content',
            'append': 'flase'
        })

        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'error')
        self.assertIn('append must be a boolean value', result['error'])
        with open(file_path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), 'old content')

    def test_failed_overwrite_preserves_existing_file(self):
        """A failed UTF-8 write must not truncate the existing destination."""
        file_path = os.path.join(self.temp_dir, 'test_atomic_overwrite.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('old content')

        result = json.loads(self.tool.execute(
            file_path=file_path,
            content='invalid surrogate: \ud800',
        ))

        self.assertEqual(result['status'], 'error')
        with open(file_path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), 'old content')
        self.assertEqual(
            [name for name in os.listdir(self.temp_dir)
             if name.startswith('.test_atomic_overwrite.txt.')],
            [],
        )

    @unittest.skipIf(os.name == 'nt', 'Windows does not expose POSIX permission bits')
    def test_overwrite_preserves_existing_file_permissions(self):
        """Atomic replacement must retain the destination mode."""
        file_path = os.path.join(self.temp_dir, 'test_permissions.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('old content')
        os.chmod(file_path, 0o640)

        result = json.loads(self.tool.execute(
            file_path=file_path,
            content='new content',
        ))

        self.assertEqual(result['status'], 'success')
        self.assertEqual(stat.S_IMODE(os.stat(file_path).st_mode), 0o640)

    def test_new_overwrite_uses_normal_creation_permissions(self):
        """A new atomic write must follow the platform's normal create mode."""
        reference_path = os.path.join(self.temp_dir, 'normal_create_mode.txt')
        with open(reference_path, 'w', encoding='utf-8') as f:
            f.write('reference')
        expected_mode = stat.S_IMODE(os.stat(reference_path).st_mode)

        file_path = os.path.join(self.temp_dir, 'new_atomic_file.txt')
        result = json.loads(self.tool.execute(
            file_path=file_path,
            content='new content',
        ))

        self.assertEqual(result['status'], 'success')
        self.assertEqual(stat.S_IMODE(os.stat(file_path).st_mode), expected_mode)

    def test_non_binary_numeric_append_value_returns_error_without_writing(self):
        """Verify a non-binary numeric append value errors without writing."""
        file_path = os.path.join(self.temp_dir, 'test_append_numeric.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('old content')

        tool_input = ToolInput({
            'file_path': file_path,
            'content': 'new content',
            'append': 2
        })

        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'error')
        self.assertIn('append numeric value must be 0 or 1', result['error'])
        with open(file_path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), 'old content')

    def test_create_directory_structure(self):
        """Verify missing parent directories are created for the target path."""
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
        """Verify a relative path is resolved under the configured base directory."""
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
        """Verify paths escaping the base directory are rejected."""
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
