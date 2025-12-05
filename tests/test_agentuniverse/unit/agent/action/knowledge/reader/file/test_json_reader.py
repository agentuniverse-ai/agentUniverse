# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import json
import tempfile
import unittest

from agentuniverse.agent.action.knowledge.reader.file.json_reader import JsonReader


class TestJsonReader(unittest.TestCase):

    def setUp(self):
        self.reader = JsonReader()
        self.temp_dir = tempfile.TemporaryDirectory()

        # Test data: JSON object
        self.json_object = {
            "name": "agentUniverse",
            "version": "0.0.19",
            "features": ["knowledge", "reader", "json"],
            "config": {
                "enabled": True,
                "max_size": 1024
            }
        }

        # Test data: JSON array
        self.json_array = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"}
        ]

        # Test data: JSON primitive
        self.json_primitive = "simple string value"

        # Test data: Complex nested JSON
        self.json_complex = {
            "metadata": {
                "author": "测试作者",
                "date": "2025-12-05",
                "tags": ["AI", "知识库", "agentUniverse"]
            },
            "data": {
                "items": [
                    {"key": "value1", "count": 10},
                    {"key": "value2", "count": 20}
                ]
            },
            "unicode": "支持中文字符 🎉"
        }

        # Create test files
        self.object_file = os.path.join(self.temp_dir.name, "test_object.json")
        with open(self.object_file, 'w', encoding='utf-8') as f:
            json.dump(self.json_object, f, ensure_ascii=False, indent=2)

        self.array_file = os.path.join(self.temp_dir.name, "test_array.json")
        with open(self.array_file, 'w', encoding='utf-8') as f:
            json.dump(self.json_array, f, ensure_ascii=False, indent=2)

        self.primitive_file = os.path.join(self.temp_dir.name, "test_primitive.json")
        with open(self.primitive_file, 'w', encoding='utf-8') as f:
            json.dump(self.json_primitive, f, ensure_ascii=False)

        self.complex_file = os.path.join(self.temp_dir.name, "test_complex.json")
        with open(self.complex_file, 'w', encoding='utf-8') as f:
            json.dump(self.json_complex, f, ensure_ascii=False, indent=2)

        # Create invalid JSON file
        self.invalid_file = os.path.join(self.temp_dir.name, "invalid.json")
        with open(self.invalid_file, 'w', encoding='utf-8') as f:
            f.write('{"invalid": json syntax}')

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_json_object(self):
        """Test loading JSON object file"""
        docs = self.reader._load_data(self.object_file)

        self.assertEqual(len(docs), 1)
        self.assertIsNotNone(docs[0].text)

        # Verify the text can be parsed back to original JSON
        parsed = json.loads(docs[0].text)
        self.assertEqual(parsed, self.json_object)

        # Verify metadata
        self.assertEqual(docs[0].metadata["file_name"], "test_object.json")
        self.assertEqual(docs[0].metadata["json_type"], "object")
        self.assertIn("file_path", docs[0].metadata)

    def test_load_json_array(self):
        """Test loading JSON array file"""
        docs = self.reader._load_data(self.array_file)

        self.assertEqual(len(docs), 1)

        # Verify the text can be parsed back to original JSON
        parsed = json.loads(docs[0].text)
        self.assertEqual(parsed, self.json_array)

        # Verify metadata
        self.assertEqual(docs[0].metadata["file_name"], "test_array.json")
        self.assertEqual(docs[0].metadata["json_type"], "array")

    def test_load_json_primitive(self):
        """Test loading JSON primitive value"""
        docs = self.reader._load_data(self.primitive_file)

        self.assertEqual(len(docs), 1)

        # Verify the text can be parsed back to original JSON
        parsed = json.loads(docs[0].text)
        self.assertEqual(parsed, self.json_primitive)

        # Verify metadata
        self.assertEqual(docs[0].metadata["json_type"], "primitive")

    def test_load_complex_json_with_unicode(self):
        """Test loading complex JSON with Unicode characters"""
        docs = self.reader._load_data(self.complex_file)

        self.assertEqual(len(docs), 1)

        # Verify Unicode is preserved
        parsed = json.loads(docs[0].text)
        self.assertEqual(parsed["unicode"], "支持中文字符 🎉")
        self.assertIn("测试作者", docs[0].text)

        # Verify metadata
        self.assertEqual(docs[0].metadata["file_name"], "test_complex.json")
        self.assertEqual(docs[0].metadata["json_type"], "object")

    def test_load_with_ext_info(self):
        """Test loading JSON with extra metadata"""
        ext_info = {"source": "test_suite", "priority": "high"}
        docs = self.reader._load_data(self.object_file, ext_info=ext_info)

        self.assertEqual(len(docs), 1)

        # Verify ext_info is merged into metadata
        self.assertEqual(docs[0].metadata["source"], "test_suite")
        self.assertEqual(docs[0].metadata["priority"], "high")
        self.assertEqual(docs[0].metadata["file_name"], "test_object.json")

    def test_load_invalid_json(self):
        """Test loading invalid JSON raises error"""
        with self.assertRaises(json.JSONDecodeError):
            self.reader._load_data(self.invalid_file)

    def test_load_nonexistent_file(self):
        """Test loading non-existent file raises error"""
        nonexistent = os.path.join(self.temp_dir.name, "nonexistent.json")
        with self.assertRaises(FileNotFoundError):
            self.reader._load_data(nonexistent)

    def test_str_path_input(self):
        """Test that string path input works"""
        docs = self.reader._load_data(self.object_file)
        self.assertEqual(len(docs), 1)
        self.assertIsNotNone(docs[0].text)

    def test_formatted_output(self):
        """Test that output is formatted with indentation"""
        docs = self.reader._load_data(self.object_file)

        # Check that the text has indentation (formatted)
        self.assertIn("\n", docs[0].text)
        self.assertIn("  ", docs[0].text)  # Should have 2-space indentation


if __name__ == "__main__":
    unittest.main()
