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

from agentuniverse.agent.action.tool.common_tool.write_file_tool import WriteFileTool


class WriteFileToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = WriteFileTool()
        self.temp_dir = tempfile.mkdtemp()
        # Functional tests operate within an explicit workspace.
        self.tool.base_dir = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_write_new_file(self):
        file_path = os.path.join(self.temp_dir, 'test_new.txt')
        content = "This is a test file content"

        result_json = self.tool.execute(file_path=file_path, content=content)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['file_path'], file_path)
        self.assertTrue(os.path.exists(file_path))

        with open(file_path, 'r') as f:
            self.assertEqual(f.read(), content)

    def test_append_to_file(self):
        file_path = os.path.join(self.temp_dir, 'test_append.txt')

        initial_content = "Initial content\n"
        self.tool.execute(file_path=file_path, content=initial_content)

        append_content = "Appended content"
        result_json = self.tool.execute(file_path=file_path,
                                        content=append_content,
                                        append=True)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['append_mode'], True)

        with open(file_path, 'r') as f:
            self.assertEqual(f.read(), initial_content + append_content)

    def test_create_directory_structure(self):
        file_path = os.path.join(self.temp_dir, 'nested/dir/structure/test.txt')
        content = "Test content in nested directory"

        result_json = self.tool.execute(file_path=file_path, content=content)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'success')
        self.assertTrue(os.path.exists(file_path))

        self.assertTrue(os.path.isdir(os.path.join(self.temp_dir, 'nested/dir/structure')))

    # ------------------------------------------------------------------ #
    # workspace confinement (issue #571)
    # ------------------------------------------------------------------ #

    def test_configured_workspace_allows_path_inside(self):
        file_path = os.path.join(self.temp_dir, 'inside.txt')

        result = json.loads(self.tool.execute(file_path=file_path, content='hello'))

        self.assertEqual(result['status'], 'success')
        self.assertTrue(os.path.exists(file_path))

    def test_configured_workspace_allows_relative_path(self):
        result = json.loads(self.tool.execute(file_path='rel.txt', content='hi'))

        self.assertEqual(result['status'], 'success')
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'rel.txt')))

    def test_configured_workspace_rejects_absolute_path_outside(self):
        outside = os.path.join(os.path.dirname(self.temp_dir), 'au_outside_test.txt')
        self.addCleanup(lambda p=outside: os.path.exists(p) and os.remove(p))

        result = json.loads(self.tool.execute(file_path=outside, content='x'))

        self.assertEqual(result['status'], 'error')
        self.assertIn('workspace', result['error'])
        self.assertFalse(os.path.exists(outside))

    def test_configured_workspace_rejects_traversal(self):
        traversal = os.path.join(self.temp_dir, '..', '..', 'au_evil_test.txt')
        target = os.path.realpath(traversal)
        self.addCleanup(lambda p=target: os.path.exists(p) and os.remove(p))

        result = json.loads(self.tool.execute(file_path=traversal, content='x'))

        self.assertEqual(result['status'], 'error')
        self.assertIn('workspace', result['error'])
        self.assertFalse(os.path.exists(target))

    def test_default_workspace_rejects_path_outside(self):
        # With base_dir unset the default workspace is the current working
        # directory; a write outside it must be rejected.
        original_cwd = os.getcwd()
        workspace = tempfile.mkdtemp()
        outside_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, workspace, ignore_errors=True)
        self.addCleanup(shutil.rmtree, outside_dir, ignore_errors=True)
        self.addCleanup(lambda: os.chdir(original_cwd))
        os.chdir(workspace)
        tool = WriteFileTool()  # base_dir left at its default

        target = os.path.join(outside_dir, 'evil.txt')

        result = json.loads(tool.execute(file_path=target, content='x'))

        self.assertEqual(result['status'], 'error')
        self.assertIn('workspace', result['error'])
        self.assertFalse(os.path.exists(target))

    def test_default_workspace_blocks_symlink_escape(self):
        # A symlink inside the workspace that points outside must be rejected
        # and the target must not be modified.
        original_cwd = os.getcwd()
        workspace = tempfile.mkdtemp()
        outside_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, workspace, ignore_errors=True)
        self.addCleanup(shutil.rmtree, outside_dir, ignore_errors=True)
        self.addCleanup(lambda: os.chdir(original_cwd))
        target = os.path.join(outside_dir, 'secret.txt')
        with open(target, 'w', encoding='utf-8') as f:
            f.write('original')
        os.chdir(workspace)
        os.symlink(target, os.path.join(workspace, 'link.txt'))
        tool = WriteFileTool()  # base_dir left at its default

        result = json.loads(tool.execute(file_path='link.txt', content='pwned'))

        self.assertEqual(result['status'], 'error')
        self.assertIn('workspace', result['error'])
        with open(target, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), 'original')


if __name__ == '__main__':
    unittest.main()
