#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for PythonCodeTextSplitter DocProcessor."""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.python_code_text_splitter \
    import PythonCodeTextSplitter
from agentuniverse.agent.action.knowledge.store.document import Document


SAMPLE_CODE = '''
import os
import sys

CONSTANT = 42


def greet(name: str) -> str:
    """Greet a user."""
    return f"Hello, {name}!"


class Calculator:
    """A simple calculator."""

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b


@decorator
def decorated():
    pass
'''


class TestPythonCodeTextSplitter(unittest.TestCase):

    def _split(self, code, **kwargs):
        proc = PythonCodeTextSplitter(**kwargs)
        return proc.process_docs([Document(text=code)], None)

    def test_splits_into_module_function_class(self):
        docs = self._split(SAMPLE_CODE)
        types = {d.metadata["code_unit_type"] for d in docs}
        self.assertIn("module", types)
        self.assertIn("function", types)
        self.assertIn("class", types)

    def test_function_name_recorded(self):
        docs = self._split(SAMPLE_CODE)
        names = {d.metadata["code_unit_name"] for d in docs
                 if d.metadata["code_unit_type"] == "function"}
        self.assertIn("greet", names)
        self.assertIn("decorated", names)

    def test_class_name_recorded(self):
        docs = self._split(SAMPLE_CODE)
        class_names = {d.metadata["code_unit_name"] for d in docs
                       if d.metadata["code_unit_type"] == "class"}
        self.assertIn("Calculator", class_names)

    def test_class_chunk_includes_methods(self):
        docs = self._split(SAMPLE_CODE)
        calc = next(d for d in docs
                    if d.metadata["code_unit_name"] == "Calculator")
        self.assertIn("def add", calc.text)
        self.assertIn("def subtract", calc.text)

    def test_decorator_included_in_source(self):
        docs = self._split(SAMPLE_CODE)
        decorated = next(d for d in docs
                         if d.metadata["code_unit_name"] == "decorated")
        self.assertIn("@decorator", decorated.text)

    def test_module_level_includes_imports(self):
        docs = self._split(SAMPLE_CODE)
        module = next(d for d in docs
                      if d.metadata["code_unit_type"] == "module")
        self.assertIn("import os", module.text)
        self.assertIn("CONSTANT", module.text)

    def test_module_level_can_be_excluded(self):
        docs = self._split(SAMPLE_CODE, include_module_level=False)
        types = {d.metadata["code_unit_type"] for d in docs}
        self.assertNotIn("module", types)

    def test_invalid_python_returned_as_module(self):
        docs = self._split("this is not valid python {{{")
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].metadata["code_unit_type"], "module")

    def test_empty_input_returns_empty(self):
        proc = PythonCodeTextSplitter()
        self.assertEqual(proc.process_docs([], None), [])

    def test_preserves_original_metadata(self):
        doc = Document(text="def f(): pass", metadata={"source": "test"})
        proc = PythonCodeTextSplitter()
        docs = proc.process_docs([doc], None)
        self.assertEqual(docs[0].metadata["source"], "test")

    def test_only_module_level_code(self):
        docs = self._split("x = 1\ny = 2\n")
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].metadata["code_unit_type"], "module")

    def test_custom_keys(self):
        docs = self._split("def f(): pass",
                           name_key="unit", type_key="kind")
        self.assertIn("unit", docs[0].metadata)
        self.assertIn("kind", docs[0].metadata)

    def test_async_function(self):
        docs = self._split("async def fetch():\n    return 1\n")
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].metadata["code_unit_type"], "function")
        self.assertIn("async def", docs[0].text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
