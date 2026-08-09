#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for LanguageFilter DocProcessor."""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.language_filter \
    import LanguageFilter
from agentuniverse.agent.action.knowledge.store.document import Document


class TestLanguageFilterScriptMode(unittest.TestCase):
    """Script-based detection (no langdetect dependency)."""

    def _filter(self, docs, allowed, **kwargs):
        kwargs.setdefault("use_langdetect", False)
        proc = LanguageFilter(allowed_languages=set(allowed), **kwargs)
        return proc.process_docs(docs, None)

    def test_keeps_english_when_allowed(self):
        docs = [Document(text="Hello world, this is English.")]
        result = self._filter(docs, {"en"})
        self.assertEqual(len(result), 1)

    def test_drops_chinese_when_only_en_allowed(self):
        docs = [
            Document(text="This is English text."),
            Document(text="这是中文文本。"),
        ]
        result = self._filter(docs, {"en"})
        self.assertEqual(len(result), 1)
        self.assertIn("English", result[0].text)

    def test_keeps_chinese_when_zh_allowed(self):
        docs = [Document(text="这是中文。")]
        result = self._filter(docs, {"zh"})
        self.assertEqual(len(result), 1)

    def test_multiple_allowed_languages(self):
        docs = [
            Document(text="English text here."),
            Document(text="中文内容。"),
            Document(text="これは日本語です。"),
        ]
        result = self._filter(docs, {"en", "zh"})
        self.assertEqual(len(result), 2)

    def test_short_text_kept_regardless(self):
        docs = [Document(text="hi")]
        result = self._filter(docs, {"zh"})
        self.assertEqual(len(result), 1)

    def test_empty_input(self):
        proc = LanguageFilter(allowed_languages={"en"}, use_langdetect=False)
        self.assertEqual(proc.process_docs([], None), [])

    def test_empty_allowed_keeps_all(self):
        docs = [Document(text="Any language"), Document(text="任何语言")]
        result = self._filter(docs, set())
        self.assertEqual(len(result), 2)

    def test_cyrillic_detected(self):
        docs = [Document(text="Это текст на русском языке.")]
        result = self._filter(docs, {"ru"})
        self.assertEqual(len(result), 1)

    def test_arabic_detected(self):
        docs = [Document(text="هذا نص باللغة العربية")]
        result = self._filter(docs, {"ar"})
        self.assertEqual(len(result), 1)

    def test_dominant_script_wins(self):
        # Mixed text — dominant language should determine classification.
        docs = [Document(text="Hello 你好世界这是一段很长的中文文本用于测试")]
        result = self._filter(docs, {"zh"})
        self.assertEqual(len(result), 1)
        result2 = self._filter(docs, {"en"})
        self.assertEqual(len(result2), 0)

    def test_preserves_original_metadata(self):
        doc = Document(text="English text.", metadata={"source": "test"})
        result = self._filter([doc], {"en"})
        self.assertEqual(result[0].metadata["source"], "test")


if __name__ == "__main__":
    unittest.main(verbosity=2)
