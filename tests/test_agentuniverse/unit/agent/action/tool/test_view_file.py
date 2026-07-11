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

from agentuniverse.agent.action.tool.common_tool.view_file_tool import ViewFileTool


class ViewFileToolTest(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.mkdtemp()
        self.tool = ViewFileTool()
        # Functional tests operate within an explicit workspace.
        self.tool.base_dir = self.workspace
        self.temp_file_path = os.path.join(self.workspace, 'sample.txt')

        test_content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
        with open(self.temp_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)

    def tearDown(self):
        shutil.rmtree(self.workspace, ignore_errors=True)

    def test_view_entire_file(self):
        result_json = self.tool.execute(file_path=self.temp_file_path)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['file_path'], self.temp_file_path)
        self.assertEqual(result['content'],
                         "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
        self.assertEqual(result['total_lines'], 5)

    def test_view_specific_lines(self):
        result_json = self.tool.execute(file_path=self.temp_file_path,
                                        start_line=1,
                                        end_line=3)
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['content'], "Line 2\nLine 3\n")
        self.assertEqual(result['start_line'], 1)
        self.assertEqual(result['end_line'], 2)

    def test_invalid_file_path(self):
        # A relative path inside the workspace that does not exist.
        result_json = self.tool.execute(file_path='nonexistent.txt')
        result = json.loads(result_json)

        self.assertEqual(result['status'], 'error')
        self.assertIn('File not found', result['error'])

    # ------------------------------------------------------------------ #
    # workspace confinement (issue #571)
    # ------------------------------------------------------------------ #

    def test_configured_workspace_allows_read_inside(self):
        inside = os.path.join(self.workspace, 'inside.txt')
        with open(inside, 'w', encoding='utf-8') as f:
            f.write('inside content')

        result = json.loads(self.tool.execute(file_path=inside))

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['content'], 'inside content')

    def test_configured_workspace_rejects_read_outside(self):
        # A real, readable file that lives outside the workspace.
        outside_handle = tempfile.NamedTemporaryFile(delete=False)
        outside_handle.write(b'secret')
        outside_handle.close()
        outside = outside_handle.name
        self.addCleanup(lambda p=outside: os.path.exists(p) and os.unlink(p))

        result = json.loads(self.tool.execute(file_path=outside))

        self.assertEqual(result['status'], 'error')
        self.assertIn('workspace', result['error'])

    def test_default_workspace_rejects_path_outside(self):
        # With base_dir unset the default workspace is the current working
        # directory; a file outside it must be rejected.
        original_cwd = os.getcwd()
        workspace = tempfile.mkdtemp()
        outside_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, workspace, ignore_errors=True)
        self.addCleanup(shutil.rmtree, outside_dir, ignore_errors=True)
        self.addCleanup(lambda: os.chdir(original_cwd))
        os.chdir(workspace)
        tool = ViewFileTool()  # base_dir left at its default

        target = os.path.join(outside_dir, 'secret.txt')
        with open(target, 'w', encoding='utf-8') as f:
            f.write('secret')

        result = json.loads(tool.execute(file_path=target))

        self.assertEqual(result['status'], 'error')
        self.assertIn('workspace', result['error'])

    def test_default_workspace_blocks_symlink_escape(self):
        # A symlink inside the workspace that points outside must be rejected.
        original_cwd = os.getcwd()
        workspace = tempfile.mkdtemp()
        outside_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, workspace, ignore_errors=True)
        self.addCleanup(shutil.rmtree, outside_dir, ignore_errors=True)
        self.addCleanup(lambda: os.chdir(original_cwd))
        target = os.path.join(outside_dir, 'secret.txt')
        with open(target, 'w', encoding='utf-8') as f:
            f.write('secret')
        os.chdir(workspace)
        os.symlink(target, os.path.join(workspace, 'link.txt'))
        tool = ViewFileTool()  # base_dir left at its default

        result = json.loads(tool.execute(file_path='link.txt'))

        self.assertEqual(result['status'], 'error')
        self.assertIn('workspace', result['error'])


if __name__ == '__main__':
    unittest.main()
