import os
import json
import tempfile
import unittest
from agentuniverse.agent.action.tool.common_tool.write_word_tool import WriteWordDocumentTool


class WriteWordDocumentToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = WriteWordDocumentTool()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.unlink(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_write_new_word_file(self):
        file_path = os.path.join(self.temp_dir, "test_new.docx")
        content = "***This is a test paragraph.***"

        result_json = self.tool.execute(file_path=file_path, content=content, append=False)
        result = json.loads(result_json)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["file_path"], file_path)
        self.assertTrue(os.path.exists(file_path))

    def test_append_to_word_file(self):
        file_path = os.path.join(self.temp_dir, "test_append.docx")

        initial_content = "Initial paragraph."
        self.tool.execute(file_path=file_path, content=initial_content, append=False)

        append_content = "Appended paragraph."
        result_json = self.tool.execute(file_path=file_path, content=append_content, append=True)
        result = json.loads(result_json)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["append_mode"], True)

    def test_invalid_file_extension(self):
        file_path = os.path.join(self.temp_dir, "invalid_file.txt")
        content = "This should fail."

        result_json = self.tool.execute(file_path=file_path, content=content, append=False)
        result = json.loads(result_json)

        self.assertEqual(result["status"], "error")
        self.assertIn("The target file must have a .docx extension.", result["error"])

    def test_create_directory_structure(self):
        file_path = os.path.join(self.temp_dir, "nested/dir/structure/test.docx")
        content = "Test content in nested directory."

        result_json = self.tool.execute(file_path=file_path, content=content, append=False)
        result = json.loads(result_json)

        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(os.path.isdir(os.path.join(self.temp_dir, "nested/dir/structure")))

    def test_missing_dependency(self):
        original_import = __import__

        def mock_import(name, *args):
            if name == "docx":
                raise ImportError("No module named 'docx'")
            return original_import(name, *args)

        try:
            __builtins__["__import__"] = mock_import
            file_path = os.path.join(self.temp_dir, "test_missing_dependency.docx")
            content = "This should fail due to missing dependency."

            result_json = self.tool.execute(file_path=file_path, content=content, append=False)
            result = json.loads(result_json)

            self.assertEqual(result["status"], "error")
            self.assertIn("python-docx is required to write Word documents", result["error"])
        finally:
            __builtins__["__import__"] = original_import


if __name__ == "__main__":
    unittest.main()