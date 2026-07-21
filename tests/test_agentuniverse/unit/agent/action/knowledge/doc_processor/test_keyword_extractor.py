#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for KeywordExtractor DocProcessor."""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.keyword_extractor \
    import KeywordExtractor
from agentuniverse.agent.action.knowledge.store.document import Document


class TestKeywordExtractor(unittest.TestCase):

    def _extract(self, text, **kwargs):
        proc = KeywordExtractor(**kwargs)
        docs = proc.process_docs([Document(text=text)], None)
        return docs[0].metadata.get("keywords", [])

    def test_extracts_relevant_keywords(self):
        text = ("Python is a popular programming language. "
                "Python is used for data science and machine learning. "
                "The Python community is very active.")
        keywords = self._extract(text, top_k=5)
        self.assertIn("python", keywords)
        self.assertGreater(len(keywords), 0)

    def test_returns_at_most_top_k(self):
        text = "apple banana cherry date elderberry fig grape"
        keywords = self._extract(text, top_k=3)
        self.assertLessEqual(len(keywords), 3)

    def test_empty_text_returns_empty(self):
        keywords = self._extract("")
        self.assertEqual(keywords, [])

    def test_empty_input_docs(self):
        proc = KeywordExtractor()
        self.assertEqual(proc.process_docs([], None), [])

    def test_stopwords_not_extracted(self):
        text = "The the the is is is a a a"
        keywords = self._extract(text, top_k=5)
        self.assertNotIn("the", keywords)
        self.assertNotIn("is", keywords)
        self.assertNotIn("a", keywords)

    def test_ngram_extraction(self):
        text = ("Machine learning is powerful. "
                "Machine learning models are everywhere. "
                "Deep learning is a subset of machine learning.")
        keywords = self._extract(text, top_k=10, ngram_size=2)
        # Should find "machine learning" as a bigram.
        self.assertTrue(any("machine learning" in kw for kw in keywords))

    def test_keywords_stamped_in_metadata(self):
        proc = KeywordExtractor(keywords_key="my_kw")
        docs = proc.process_docs(
            [Document(text="Python is great.")], None)
        self.assertIn("my_kw", docs[0].metadata)

    def test_preserves_original_metadata(self):
        doc = Document(text="Hello world.", metadata={"source": "test"})
        proc = KeywordExtractor()
        docs = proc.process_docs([doc], None)
        self.assertEqual(docs[0].metadata["source"], "test")
        self.assertIn("keywords", docs[0].metadata)

    def test_chinese_text_supported(self):
        text = "人工智能是未来的方向。人工智能技术发展迅速。深度学习是人工智能的重要分支。"
        keywords = self._extract(text, top_k=5)
        self.assertGreater(len(keywords), 0)

    def test_min_term_freq_filters_rare(self):
        text = "rareword appears once. common common common common."
        keywords = self._extract(text, top_k=10, min_term_freq=2)
        self.assertIn("common", keywords)
        self.assertNotIn("rareword", keywords)


if __name__ == "__main__":
    unittest.main(verbosity=2)
