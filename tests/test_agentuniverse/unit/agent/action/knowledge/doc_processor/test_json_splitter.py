#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for JsonSplitter DocProcessor."""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.json_splitter import \
    JsonSplitter
from agentuniverse.agent.action.knowledge.store.document import Document


class TestJsonSplitter(unittest.TestCase):

    def _split(self, json_text, **kwargs):
        proc = JsonSplitter(**kwargs)
        return proc.process_docs([Document(text=json_text)], None)

    def test_flat_object(self):
        docs = self._split('{"name": "Alice", "age": 30}')
        paths = {d.metadata["json_path"] for d in docs}
        self.assertIn("root > name", paths)
        self.assertIn("root > age", paths)
        texts = {d.text for d in docs}
        self.assertIn("Alice", texts)
        self.assertIn("30", texts)

    def test_nested_object(self):
        docs = self._split('{"user": {"name": "Bob", "city": "NYC"}}')
        paths = {d.metadata["json_path"] for d in docs}
        self.assertIn("root > user > name", paths)
        self.assertIn("root > user > city", paths)

    def test_array(self):
        docs = self._split('{"items": ["a", "b", "c"]}')
        paths = {d.metadata["json_path"] for d in docs}
        self.assertIn("root > items > [0]", paths)
        self.assertIn("root > items > [1]", paths)
        self.assertIn("root > items > [2]", paths)

    def test_max_depth_limits_traversal(self):
        docs = self._split('{"a": {"b": {"c": "deep"}}}', max_depth=2)
        # At depth 2, {"c": "deep"} is serialised as JSON text.
        self.assertEqual(len(docs), 1)
        self.assertIn("c", docs[0].text)
        self.assertIn("deep", docs[0].text)

    def test_null_value_dropped_by_default(self):
        docs = self._split('{"x": null, "y": "present"}', drop_empty=True)
        texts = [d.text for d in docs]
        self.assertNotIn("", texts)
        self.assertIn("present", texts)

    def test_null_value_kept_when_drop_empty_false(self):
        docs = self._split('{"x": null}', drop_empty=False)
        self.assertTrue(any(d.text == "" for d in docs))

    def test_boolean_value(self):
        docs = self._split('{"flag": true}')
        self.assertEqual(docs[0].text, "true")

    def test_non_json_returned_unchanged(self):
        docs = self._split("not json at all")
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].text, "not json at all")
        self.assertNotIn("json_path", docs[0].metadata or {})

    def test_empty_input_returns_empty(self):
        proc = JsonSplitter()
        self.assertEqual(proc.process_docs([], None), [])

    def test_max_value_length_truncates(self):
        long_val = "x" * 200
        docs = self._split(f'{{"k": "{long_val}"}}', max_value_length=10)
        self.assertLessEqual(len(docs[0].text), 10)

    def test_custom_path_key(self):
        docs = self._split('{"a": 1}', path_key="my_path")
        self.assertIn("my_path", docs[0].metadata)

    def test_preserves_original_metadata(self):
        doc = Document(text='{"a": 1}', metadata={"source": "api"})
        proc = JsonSplitter()
        docs = proc.process_docs([doc], None)
        self.assertEqual(docs[0].metadata["source"], "api")
        self.assertIn("json_path", docs[0].metadata)

    def test_mixed_array_of_objects(self):
        json_text = '{"users": [{"name": "A"}, {"name": "B"}]}'
        docs = self._split(json_text)
        paths = {d.metadata["json_path"] for d in docs}
        self.assertIn("root > users > [0] > name", paths)
        self.assertIn("root > users > [1] > name", paths)


if __name__ == "__main__":
    unittest.main(verbosity=2)
