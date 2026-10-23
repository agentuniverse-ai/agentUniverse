# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for `jieba_keyword_extractor`.

The processor had no coverage. It segments each document with jieba, drops
Chinese and English stopwords, and stores the top keywords on the document.

The assertions pin the structural contract rather than exact keyword lists:
the ranking comes from jieba's bundled TF-IDF model, so asserting
`keywords == ["自然语言", ...]` would break on any upstream model update while
telling us nothing about this module. What matters here is how many keywords
come back, that stopwords never do, that they actually occur in the text, and
that the processor mutates the documents it was given.
"""

import unittest
from types import SimpleNamespace

from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import (
    JiebaKeywordExtractor,
)
from agentuniverse.agent.action.knowledge.store.document import Document

CHINESE_TEXT = "自然语言处理是人工智能的一个重要分支，机器学习模型需要大量训练数据"
ENGLISH_TEXT = "The quick brown fox jumps over the lazy dog and runs away"

CHINESE_STOPWORDS = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人"}
ENGLISH_STOPWORDS = {"the", "and", "over", "is", "a", "of", "to"}


class JiebaKeywordExtractorDefaultTest(unittest.TestCase):

    def test_default_top_k(self):
        self.assertEqual(JiebaKeywordExtractor().top_k, 3)

    def test_it_returns_the_documents_it_was_given(self):
        """The processor mutates in place; it does not build new documents."""
        processor = JiebaKeywordExtractor()
        documents = [Document(text=CHINESE_TEXT)]

        result = processor.process_docs(documents)

        self.assertIs(result[0], documents[0])

    def test_keywords_land_on_the_document_itself(self):
        processor = JiebaKeywordExtractor()
        document = Document(text=CHINESE_TEXT)

        processor.process_docs([document])

        self.assertTrue(len(document.keywords) > 0)


class JiebaKeywordExtractorChineseTest(unittest.TestCase):

    def test_chinese_text_yields_top_k_keywords(self):
        processor = JiebaKeywordExtractor()
        document = Document(text=CHINESE_TEXT)

        processor.process_docs([document])

        self.assertEqual(len(document.keywords), processor.top_k)

    def test_chinese_keywords_come_from_the_text(self):
        processor = JiebaKeywordExtractor()
        document = Document(text=CHINESE_TEXT)

        processor.process_docs([document])

        for keyword in document.keywords:
            self.assertIn(keyword, CHINESE_TEXT)

    def test_chinese_stopwords_are_excluded(self):
        processor = JiebaKeywordExtractor()
        processor.top_k = 8
        document = Document(text=CHINESE_TEXT)

        processor.process_docs([document])

        self.assertEqual(set(document.keywords) & CHINESE_STOPWORDS, set())

    def test_top_k_is_honoured(self):
        for top_k in (1, 3, 5):
            with self.subTest(top_k=top_k):
                processor = JiebaKeywordExtractor()
                processor.top_k = top_k
                document = Document(text=CHINESE_TEXT)

                processor.process_docs([document])

                self.assertLessEqual(len(document.keywords), top_k)


class JiebaKeywordExtractorEnglishTest(unittest.TestCase):

    def test_english_text_yields_keywords(self):
        processor = JiebaKeywordExtractor()
        document = Document(text=ENGLISH_TEXT)

        processor.process_docs([document])

        self.assertEqual(len(document.keywords), processor.top_k)

    def test_english_stopwords_are_excluded(self):
        processor = JiebaKeywordExtractor()
        processor.top_k = 8
        document = Document(text=ENGLISH_TEXT)

        processor.process_docs([document])

        lowered = {keyword.lower() for keyword in document.keywords}
        self.assertEqual(lowered & ENGLISH_STOPWORDS, set())


class JiebaKeywordExtractorEdgeCaseTest(unittest.TestCase):

    def test_empty_text_yields_no_keywords(self):
        processor = JiebaKeywordExtractor()
        document = Document(text="")

        processor.process_docs([document])

        self.assertEqual(len(document.keywords), 0)

    def test_each_document_gets_its_own_keywords(self):
        processor = JiebaKeywordExtractor()
        chinese = Document(text=CHINESE_TEXT)
        english = Document(text=ENGLISH_TEXT)

        processor.process_docs([chinese, english])

        for keyword in chinese.keywords:
            self.assertIn(keyword, CHINESE_TEXT)
        for keyword in english.keywords:
            self.assertIn(keyword, ENGLISH_TEXT)

    def test_an_empty_document_list_is_a_no_op(self):
        processor = JiebaKeywordExtractor()

        self.assertEqual(processor.process_docs([]), [])


class JiebaKeywordExtractorConfigurationTest(unittest.TestCase):
    """`DocProcessor._initialize_by_component_configer` copies `name` and
    `description` from the configer before the subclass reads its own fields,
    so the stub has to carry them."""

    @staticmethod
    def _configer(**overrides):
        fields = {"name": "keywords", "description": "test"}
        fields.update(overrides)
        return SimpleNamespace(**fields)

    def test_top_k_is_read_from_the_component_configuration(self):
        processor = JiebaKeywordExtractor()

        processor._initialize_by_component_configer(self._configer(top_k=7))

        self.assertEqual(processor.top_k, 7)

    def test_configuration_omitting_top_k_keeps_the_default(self):
        processor = JiebaKeywordExtractor()

        processor._initialize_by_component_configer(self._configer())

        self.assertEqual(processor.top_k, 3)

    def test_the_name_from_configuration_is_applied(self):
        processor = JiebaKeywordExtractor()

        processor._initialize_by_component_configer(self._configer(name="my_extractor"))

        self.assertEqual(processor.name, "my_extractor")


if __name__ == "__main__":
    unittest.main()
