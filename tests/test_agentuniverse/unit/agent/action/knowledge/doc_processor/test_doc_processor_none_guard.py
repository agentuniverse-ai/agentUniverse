#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for None.text / dimension-mismatch guards in doc processors.

1. SemanticDeduplicator._compute_hash crashed on None text (Document.text is
   Optional[str]); now treats None as ''.
2. SemanticDeduplicator._compute_similarity used zip() across mismatched
   dimensions, silently truncating and returning a meaningless score (same
   hole MMRProcessor was hardened against); now returns 0.0 on mismatch.
3. JiebaKeywordExtractor._process_docs crashed on None text (jieba.lcut(None)
   TypeError) and had no empty-input short-circuit; both fixed.
"""

import unittest

from agentuniverse.agent.action.knowledge.store.document import Document


class TestSemanticDeduplicatorsNoneAndDimensionGuards(unittest.TestCase):

    def _processor(self):
        from agentuniverse.agent.action.knowledge.doc_processor.\
            semantic_deduplicator import SemanticDeduplicator
        return SemanticDeduplicator()

    def test_compute_hash_handles_none_text(self):
        proc = self._processor()
        # Previously: None.encode() raised AttributeError.
        h = proc._compute_hash(None)
        self.assertEqual(h, proc._compute_hash(''))
        self.assertEqual(len(h), 64)  # sha256 hex length

    def test_compute_hash_handles_empty_text(self):
        proc = self._processor()
        h = proc._compute_hash('')
        self.assertEqual(len(h), 64)

    def test_compute_similarity_rejects_mismatched_dimensions(self):
        proc = self._processor()
        # Previously: zip() silently truncated to length 2 and produced a
        # plausible-looking but meaningless score.
        score = proc._compute_similarity([1.0, 0.0], [1.0, 0.0, 0.0])
        self.assertEqual(score, 0.0,
                         "mismatched-dimension vectors must not be compared; "
                         "they come from different embedding spaces")

    def test_compute_similarity_returns_zero_on_empty_vector(self):
        proc = self._processor()
        self.assertEqual(proc._compute_similarity([], [1.0, 0.0]), 0.0)
        self.assertEqual(proc._compute_similarity([1.0, 0.0], []), 0.0)

    def test_compute_similarity_matches_equal_dimensions(self):
        proc = self._processor()
        # Same direction → similarity 1.0.
        score = proc._compute_similarity([1.0, 0.0], [1.0, 0.0])
        self.assertAlmostEqual(score, 1.0, places=6)


class TestJiebaKeywordExtractorNoneGuard(unittest.TestCase):

    def _processor(self):
        from agentuniverse.agent.action.knowledge.doc_processor.\
            jieba_keyword_extractor import JiebaKeywordExtractor
        return JiebaKeywordExtractor()

    def test_process_docs_handles_none_text(self):
        proc = self._processor()
        # Previously: jieba.lcut(None) raised TypeError.
        docs = [Document(id="d1", text=None),
                Document(id="d2", text="正常中文文本")]
        result = proc._process_docs(docs)
        self.assertEqual(len(result), 2)

    def test_process_docs_empty_input_returns_empty(self):
        proc = self._processor()
        # Previously: no short-circuit; the loop just didn't run, returning
        # the empty list. Pin the explicit return.
        self.assertEqual(proc._process_docs([]), [])

    def test_process_docs_extracts_keywords_from_normal_text(self):
        proc = self._processor()
        docs = [Document(id="d1", text="人工智能是未来")]
        result = proc._process_docs(docs)
        # Some keywords should be extracted (sanity — we are not asserting
        # the exact set, which depends on the jieba dictionary).
        # keywords is a set on Document; just assert it ran without crashing
        # and returned the doc.
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "d1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
