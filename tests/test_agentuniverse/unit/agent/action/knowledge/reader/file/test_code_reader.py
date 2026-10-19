# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/4 15:16
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: test_code_reader.py

import os
from pydoc import doc
import tempfile
import unittest

from agentuniverse.agent.action.knowledge.reader.file.code_reader import CodeReader


class TestCodeReader(unittest.TestCase):
    """Unit tests for CodeReader loading source files of several languages."""

    def setUp(self):
        """Create a fresh CodeReader, temp dir, and sample source files for each test."""
        self.reader = CodeReader()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.py_code: str = '''
class FileProcessor:
    DEFAULT_FORMAT = "txt"

    def __init__(self, file_path):
        self.file_path = file_path
        self.processed = False

    def process(self):
        self.processed = True
        return f"Processed {self.file_path}"
        '''

        self.java_code: str = '''
package com.example.service;

import java.util.List;

public class UserService {

    private String serviceName;

    public UserService(String name) {
        this.serviceName = name;
    }

    public String getServiceName() {
        return this.serviceName;
    }

    public boolean createUser(String username) {
        return true;
    }
}
        '''
        self.rs_code: str = '''
pub struct Config {
    name: String,
    value: i32,
}

impl Config {
    pub fn new(name: &str, value: i32) -> Self {
        Config {
            name: name.to_string(),
            value,
        }
    }

    pub fn get_name(&self) -> &str {
        &self.name
    }

    pub fn get_value(&self) -> i32 {
        self.value
    }
}
        '''
        with open(os.path.join(self.temp_dir.name, "test.py"), 'w', encoding='utf-8') as f:
            f.write(self.py_code)
        with open(os.path.join(self.temp_dir.name, "test.java"), 'w', encoding='utf-8') as f:
            f.write(self.java_code)
        with open(os.path.join(self.temp_dir.name, "test.rs"), 'w', encoding='utf-8') as f:
            f.write(self.rs_code)

    def tearDown(self):
        """Remove the temporary directory created in setUp."""
        self.temp_dir.cleanup()

    def test_load_python(self):
        """A .py file loads as one document with python language metadata."""
        docs = self.reader._load_data(os.path.join(self.temp_dir.name, "test.py"))
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].text, self.py_code)
        self.assertEqual(docs[0].metadata["language"], "python")
        self.assertEqual(docs[0].metadata["file_suffix"], ".py")
        self.assertEqual(docs[0].metadata["file_name"], "test.py")

    def test_load_java(self):
        """A .java file loads as one document with java language metadata."""
        docs = self.reader._load_data(os.path.join(self.temp_dir.name, "test.java"))
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].text, self.java_code)
        self.assertEqual(docs[0].metadata["language"], "java")
        self.assertEqual(docs[0].metadata["file_suffix"], ".java")
        self.assertEqual(docs[0].metadata["file_name"], "test.java")

    def test_load_rust(self):
        """A .rs file loads as one document with rust language metadata."""
        docs = self.reader._load_data(os.path.join(self.temp_dir.name, "test.rs"))
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].text, self.rs_code)
        self.assertEqual(docs[0].metadata["language"], "rust")
        self.assertEqual(docs[0].metadata["file_suffix"], ".rs")
        self.assertEqual(docs[0].metadata["file_name"], "test.rs")


if __name__ == "__main__":
    unittest.main()
