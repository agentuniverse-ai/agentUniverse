# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/4 15:47
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: test_code_ast_processor.py

import json
import os
import tempfile
import unittest
from pathlib import Path

from agentuniverse.agent.action.knowledge.doc_processor.code_ast_processor import CodeAstProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class TestCodeAstProcessor(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.py_code = '''
class FileProcessor:
    DEFAULT_FORMAT = "txt"

    def __init__(self, file_path):
        self.file_path = file_path
        self.processed = False

    def process(self):
        self.processed = True
        return f"Processed {self.file_path}"
        '''

        self.java_code = '''
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

        self.cpp_code = '''
class Config {
private:
    std::string name;
    int value;

public:
    Config(const std::string& name, int value)
        : name(name), value(value) {}

    std::string getName() const {
        return name;
    }

    int getValue() const {
        return value;
    }
};
        '''

        with open(os.path.join(self.temp_dir.name, "test.py"), 'w', encoding='utf-8') as f:
            f.write(self.py_code)
        with open(os.path.join(self.temp_dir.name, "test.java"), 'w', encoding='utf-8') as f:
            f.write(self.java_code)
        with open(os.path.join(self.temp_dir.name, "test.cpp"), 'w', encoding='utf-8') as f:
            f.write(self.cpp_code)

        self.processor = CodeAstProcessor()
        configer = ComponentConfiger()
        configer.name = 'code_ast_processor'
        configer.description = 'code_ast_processor'
        configer.language_dir = str(Path(__file__).parent / "tree_sitter_libs")
        configer.max_depth = 8
        configer.max_node_len = 100
        configer.chunk_size = 1000
        configer.chunk_overlap = 200
        self.processor._initialize_by_component_configer(configer)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_process_python(self):
        doc = Document(
            text=self.py_code,
            metadata={"language": "python", "file_name": "test.py"}
        )
        result_docs = self.processor._process_docs([doc])

        self.assertEqual(len(result_docs), 1)
        ast_doc = result_docs[0]
        content = json.loads(ast_doc.text)

        self.assertIn("ast", content)
        self.assertIn("features", content)
        self.assertEqual(content["language"], "python")

        features = content["features"]
        print(f'ast_doc: {ast_doc}\nfeatures: {features}\n\n')
        print(f'result: {result_docs[0].text}')

    def test_process_java(self):
        doc = Document(
            text=self.java_code,
            metadata={"language": "java", "file_name": "test.java"}
        )
        result_docs = self.processor._process_docs([doc])

        self.assertEqual(len(result_docs), 1)
        ast_doc = result_docs[0]
        content = json.loads(ast_doc.text)

        self.assertIn("ast", content)
        self.assertIn("features", content)
        self.assertEqual(content["language"], "java")

        features = content["features"]
        # print(f'ast_doc: {ast_doc}\nfeatures: {features}\n')

    def test_process_cpp(self):
        doc = Document(
            text=self.cpp_code,
            metadata={"language": "cpp", "file_name": "test.cpp"}
        )
        result_docs = self.processor._process_docs([doc])

        self.assertEqual(len(result_docs), 1)
        ast_doc = result_docs[0]
        content = json.loads(ast_doc.text)

        self.assertIn("ast", content)
        self.assertIn("features", content)
        self.assertEqual(content["language"], "cpp")

        features = content["features"]
        # print(f'ast_doc: {ast_doc}\nfeatures: {features}\n')

    def test_code_metrics(self):
        for code, language in [
            (self.py_code, "python"),
            (self.java_code, "java"),
            (self.cpp_code, "cpp")
        ]:
            metrics = self.processor._calculate_code_metrics(code, language)
            self.assertGreater(metrics["line_count"], 0)
            self.assertGreater(metrics["code_line_count"], 0)
            self.assertGreater(metrics["avg_line_length"], 0)
            self.assertEqual(metrics["character_count"], len(code))


if __name__ == "__main__":
    unittest.main()
