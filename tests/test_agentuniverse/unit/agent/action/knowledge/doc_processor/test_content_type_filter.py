#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for ContentTypeFilter DocProcessor."""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.content_type_filter \
    import ContentTypeFilter
from agentuniverse.agent.action.knowledge.store.document import Document


def _doc(text, content_type=None, key="content_type"):
    metadata = {} if content_type is None else {key: content_type}
    return Document(text=text, metadata=metadata)


class ContentTypeFilterTest(unittest.TestCase):
    def _filter(self, docs, allowed, **kwargs):
        proc = ContentTypeFilter(allowed_types=set(allowed), **kwargs)
        return proc.process_docs(docs, None)

    def test_keeps_allowed_type(self):
        docs = [_doc("hello", "text")]
        result = self._filter(docs, {"text"})
        self.assertEqual(len(result), 1)

    def test_drops_disallowed_type(self):
        docs = [_doc("hello", "text"), _doc("x=1", "code")]
        result = self._filter(docs, {"text"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata["content_type"], "text")

    def test_multiple_allowed_types(self):
        docs = [
            _doc("hello", "text"),
            _doc("x=1", "code"),
            _doc("| a | b |", "table"),
        ]
        result = self._filter(docs, {"text", "code"})
        self.assertEqual(len(result), 2)

    def test_missing_type_kept_by_default(self):
        docs = [_doc("no metadata here")]
        result = self._filter(docs, {"text"})
        self.assertEqual(len(result), 1)

    def test_missing_type_dropped_when_policy_drop(self):
        docs = [_doc("no metadata here")]
        result = self._filter(docs, {"text"}, default_policy="drop")
        self.assertEqual(len(result), 0)

    def test_empty_allowed_keeps_all(self):
        docs = [_doc("a", "text"), _doc("b", "code"), _doc("c", "table")]
        result = self._filter(docs, set())
        self.assertEqual(len(result), 3)

    def test_empty_input(self):
        proc = ContentTypeFilter(allowed_types={"text"})
        self.assertEqual(proc.process_docs([], None), [])

    def test_case_insensitive_by_default(self):
        docs = [_doc("Hello", "TEXT"), _doc("Bye", "text")]
        result = self._filter(docs, {"text"})
        self.assertEqual(len(result), 2)

    def test_case_sensitive_mode(self):
        docs = [_doc("Hello", "TEXT"), _doc("Bye", "text")]
        result = self._filter(docs, {"TEXT"}, case_sensitive=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata["content_type"], "TEXT")

    def test_custom_type_key(self):
        docs = [_doc("hello", "text", key="kind")]
        result = self._filter(docs, {"text"}, type_key="kind")
        self.assertEqual(len(result), 1)

    def test_whitespace_in_type_is_stripped(self):
        docs = [_doc("hello", "  text  ")]
        result = self._filter(docs, {"text"})
        self.assertEqual(len(result), 1)

    def test_numeric_content_type_coerced(self):
        docs = [_doc("hello", 1)]
        result = self._filter(docs, {"1"})
        self.assertEqual(len(result), 1)

    def test_invalid_default_policy_raises(self):
        proc = ContentTypeFilter(allowed_types={"text"}, default_policy="maybe")
        with self.assertRaises(ValueError):
            proc.process_docs([_doc("hi", "text")], None)

    def test_blank_type_treated_as_missing(self):
        # A whitespace-only content type is treated as missing.
        docs = [_doc("hello", "   ")]
        kept = self._filter(docs, {"text"})
        self.assertEqual(len(kept), 1)  # default policy keep
        dropped = self._filter(docs, {"text"}, default_policy="drop")
        self.assertEqual(len(dropped), 0)


if __name__ == "__main__":
    unittest.main()
