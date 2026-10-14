#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/15
# @Author  : dxz0069
# @FileName: test_sensitive_word_filter.py

import os
import tempfile
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.sensitive_word_filter import (
    HITS_METADATA_KEY,
    SensitiveWordFilter,
)
from agentuniverse.agent.action.knowledge.store.document import Document


def _doc(text, doc_id="1", metadata=None):
    return Document(id=doc_id, text=text, metadata=metadata)


class TestSensitiveWordFilter(unittest.TestCase):
    """Test suite for the sensitive word filter."""

    def setUp(self):
        self.filter = SensitiveWordFilter(words=["敏感词", "banned", "secret key"])

    def test_mask_mode_replaces_matches(self):
        result = self.filter.process_docs([
            _doc("this contains 敏感词 and a banned word", "d1"),
        ])
        self.assertEqual(result[0].text, "this contains *** and a ****** word")

    def test_mask_mode_keeps_documents(self):
        result = self.filter.process_docs([_doc("敏感词", "d1"), _doc("clean", "d2")])
        self.assertEqual(len(result), 2)

    def test_mask_resolves_overlapping_matches_left_to_right(self):
        word_filter = SensitiveWordFilter(words=["abcd", "cdef"])
        result = word_filter.process_docs([_doc("xabcdefy", "d1")])
        self.assertEqual(result[0].text, "x******y")

    def test_block_mode_drops_documents(self):
        block_filter = SensitiveWordFilter(words=["敏感词"], mode="block")
        result = block_filter.process_docs([
            _doc("clean document", "d1"),
            _doc("contains 敏感词 here", "d2"),
        ])
        self.assertEqual([doc.id for doc in result], ["d1"])
        self.assertEqual(result[0].text, "clean document")

    def test_block_threshold(self):
        block_filter = SensitiveWordFilter(
            words=["banned", "secret key"], mode="block", block_threshold=2)
        result = block_filter.process_docs([
            _doc("one banned hit only", "d1"),
            _doc("banned and secret key both", "d2"),
        ])
        self.assertEqual([doc.id for doc in result], ["d1"])

    def test_case_insensitive_by_default(self):
        result = self.filter.process_docs([_doc("BANNED and Secret Key", "d1")])
        self.assertEqual(result[0].text, "****** and **********")

    def test_case_sensitive_option(self):
        case_filter = SensitiveWordFilter(words=["banned"], case_sensitive=True)
        result = case_filter.process_docs([_doc("BANNED banned", "d1")])
        self.assertEqual(result[0].text, "BANNED ******")

    def test_hits_recorded_in_metadata(self):
        result = self.filter.process_docs([_doc("banned and secret key", "d1")])
        self.assertEqual(
            result[0].metadata[HITS_METADATA_KEY], ["banned", "secret key"])

    def test_no_hits_leave_text_and_metadata_untouched(self):
        result = self.filter.process_docs([_doc("clean text", "d1", {"k": "v"})])
        self.assertEqual(result[0].text, "clean text")
        self.assertEqual(result[0].metadata, {"k": "v"})

    def test_word_file_loading(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as file:
            file.write("# comment line\nwordone\nwordtwo\n\nwordone\n")
            path = file.name
        try:
            file_filter = SensitiveWordFilter(word_file=path)
            result = file_filter.process_docs([_doc("a wordtwo b wordone c", "d1")])
            self.assertEqual(result[0].text, "a ******* b ******* c")
            self.assertEqual(
                result[0].metadata[HITS_METADATA_KEY], ["wordone", "wordtwo"])
        finally:
            os.unlink(path)

    def test_multi_char_mask_and_chinese_words(self):
        cn_filter = SensitiveWordFilter(words=["违规内容"], mask_char="#")
        result = cn_filter.process_docs([_doc("前缀违规内容后缀", "d1")])
        self.assertEqual(result[0].text, "前缀####后缀")

    def test_no_words_configured_raises(self):
        with self.assertRaises(ValueError):
            SensitiveWordFilter().process_docs([_doc("text", "d1")])

    def test_invalid_mode_raises_on_init(self):
        from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
        from agentuniverse.base.config.configer import Configer
        configer = Configer()
        configer.value = {"name": "f", "description": "d", "words": ["w"], "mode": "wrong"}
        doc_configer = ComponentConfiger().load_by_configer(configer)
        with self.assertRaises(ValueError):
            SensitiveWordFilter().initialize_by_component_configer(doc_configer)

    def test_missing_word_file_raises_on_init(self):
        from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
        from agentuniverse.base.config.configer import Configer
        configer = Configer()
        configer.value = {"name": "f", "description": "d", "word_file": "./no/such/file.txt"}
        doc_configer = ComponentConfiger().load_by_configer(configer)
        with self.assertRaises(ValueError):
            SensitiveWordFilter().initialize_by_component_configer(doc_configer)

    def test_empty_docs_passthrough(self):
        self.assertEqual(self.filter.process_docs([]), [])


if __name__ == "__main__":
    unittest.main()
