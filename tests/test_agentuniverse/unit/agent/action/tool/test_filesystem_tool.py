#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for FileSystemTool."""

import os
import tempfile
import unittest

from agentuniverse.agent.action.tool.common_tool.filesystem_tool import \
    FileSystemTool


class TestFileSystemTool(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tool = FileSystemTool(base_dir=self.tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_mkdir_and_list(self):
        result = self.tool.execute(mode="mkdir", path="subdir")
        self.assertEqual(result["status"], "success")
        result = self.tool.execute(mode="list", path=".")
        self.assertEqual(result["status"], "success")
        names = [e["name"] for e in result["entries"]]
        self.assertIn("subdir", names)

    def test_copy_file(self):
        # Create a source file.
        src = os.path.join(self.tmp, "src.txt")
        with open(src, "w") as f:
            f.write("hello")
        result = self.tool.execute(mode="copy", path="src.txt", target="dst.txt")
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "dst.txt")))

    def test_move_file(self):
        src = os.path.join(self.tmp, "a.txt")
        with open(src, "w") as f:
            f.write("data")
        result = self.tool.execute(mode="move", path="a.txt", target="b.txt")
        self.assertEqual(result["status"], "success")
        self.assertFalse(os.path.exists(src))
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "b.txt")))

    def test_delete_file(self):
        f = os.path.join(self.tmp, "del.txt")
        with open(f, "w") as fh:
            fh.write("x")
        result = self.tool.execute(mode="delete", path="del.txt")
        self.assertTrue(result["deleted"])
        self.assertFalse(os.path.exists(f))

    def test_delete_nonexistent(self):
        result = self.tool.execute(mode="delete", path="nope.txt")
        self.assertEqual(result["status"], "success")
        self.assertFalse(result["deleted"])

    def test_exists(self):
        result = self.tool.execute(mode="exists", path=".")
        self.assertTrue(result["exists"])
        result = self.tool.execute(mode="exists", path="nonexistent")
        self.assertFalse(result["exists"])

    def test_info(self):
        f = os.path.join(self.tmp, "info.txt")
        with open(f, "w") as fh:
            fh.write("content")
        result = self.tool.execute(mode="info", path="info.txt")
        self.assertEqual(result["type"], "file")
        self.assertEqual(result["size"], 7)

    def test_tree(self):
        os.makedirs(os.path.join(self.tmp, "a", "b", "c"))
        result = self.tool.execute(mode="tree", path=".")
        self.assertEqual(result["status"], "success")
        names = [e["name"] for e in result["entries"]]
        self.assertTrue(any("a" in n for n in names))

    def test_path_escape_rejected(self):
        result = self.tool.execute(mode="exists", path="../../../etc")
        self.assertEqual(result["status"], "error")

    def test_unknown_mode(self):
        result = self.tool.execute(mode="invalid", path=".")
        self.assertEqual(result["status"], "error")

    def test_list_truncates_at_max_entries(self):
        self.tool.max_list_entries = 3
        for i in range(10):
            open(os.path.join(self.tmp, f"f{i}.txt"), "w").close()
        result = self.tool.execute(mode="list", path=".")
        self.assertTrue(result["truncated"])
        self.assertEqual(result["count"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
