#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for QualityScorer DocProcessor."""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.quality_scorer \
    import QualityScorer
from agentuniverse.agent.action.knowledge.store.document import Document

# A well-formed English paragraph used as a "high quality" baseline.
_GOOD_TEXT = (
    "The quick brown fox jumps over the lazy dog. "
    "Machine learning models require large amounts of clean training data. "
    "Document quality affects retrieval accuracy in meaningful ways. "
    "Consistent punctuation and varied vocabulary improve readability. "
    "Agents perform better when their knowledge base is well curated."
)


class TestQualityScorer(unittest.TestCase):

    def _score(self, docs, **kwargs):
        proc = QualityScorer(**kwargs)
        return proc.process_docs(docs, None)

    def _single(self, text, **kwargs):
        result = self._score([Document(text=text)], **kwargs)
        return result[0] if result else None

    # ------------------------------------------------------------------ #
    # annotation mode (min_score None) — nothing is dropped
    # ------------------------------------------------------------------ #
    def test_annotates_score_in_metadata(self):
        doc = self._single(_GOOD_TEXT)
        self.assertIn("quality_score", doc.metadata)
        self.assertIsInstance(doc.metadata["quality_score"], float)

    def test_detail_breakdown_written(self):
        doc = self._single(_GOOD_TEXT)
        detail = doc.metadata["quality_detail"]
        for dim in ["length", "sentence_completeness", "special_char_ratio",
                    "repetition", "information_density"]:
            self.assertIn(dim, detail)
            self.assertIn("score", detail[dim])
            self.assertIn("weight", detail[dim])

    def test_score_in_unit_range(self):
        for text in ["", "a", _GOOD_TEXT, "!!!! @@@@ #### ****"]:
            doc = self._single(text)
            if doc is None:
                continue
            s = doc.metadata["quality_score"]
            self.assertGreaterEqual(s, 0.0)
            self.assertLessEqual(s, 1.0)

    def test_good_text_scores_higher_than_garbage(self):
        good = self._single(_GOOD_TEXT).metadata["quality_score"]
        garbage = self._single("@@@@ #### $$$$ %%%% **** !!!! @@@@").metadata[
            "quality_score"]
        self.assertGreater(good, garbage)

    # ------------------------------------------------------------------ #
    # min_score dropping
    # ------------------------------------------------------------------ #
    def test_min_score_drops_low_quality(self):
        # Pure symbol garbage scores very low; min_score 0.5 drops it.
        docs = [Document(text="@@@ #### $$$ %%% **** @@@ @@@ @@@")]
        result = self._score(docs, min_score=0.5)
        self.assertEqual(len(result), 0)

    def test_min_score_keeps_high_quality(self):
        docs = [Document(text=_GOOD_TEXT)]
        result = self._score(docs, min_score=0.3)
        self.assertEqual(len(result), 1)

    def test_min_score_none_keeps_everything(self):
        docs = [Document(text="@@@ ###"), Document(text=_GOOD_TEXT)]
        result = self._score(docs, min_score=None)
        self.assertEqual(len(result), 2)

    def test_invalid_min_score_raises(self):
        # min_score outside [0.0, 1.0] is rejected at construction time.
        with self.assertRaises(Exception):
            QualityScorer(min_score=2.0).process_docs(
                [Document(text="hi")], None)

    # ------------------------------------------------------------------ #
    # individual dimensions
    # ------------------------------------------------------------------ #
    def test_length_dimension_penalises_short_text(self):
        # Very short text -> length sub-score low; long text around ideal higher.
        short = self._single("hi there friend.").metadata["quality_detail"]
        good = self._single(_GOOD_TEXT).metadata["quality_detail"]
        self.assertLessEqual(short["length"]["score"],
                             good["length"]["score"] + 0.05)

    def test_special_char_ratio_penalises_symbols(self):
        clean = self._single("normal english words here.").metadata[
            "quality_detail"]
        symbols = self._single("@@@@@@@@@@#######").metadata["quality_detail"]
        self.assertGreater(clean["special_char_ratio"]["score"],
                           symbols["special_char_ratio"]["score"])

    def test_repetition_penalises_duplicates(self):
        varied = self._single(_GOOD_TEXT).metadata["quality_detail"]
        repeated = self._single(" ".join(["same"] * 40) + ".").metadata[
            "quality_detail"]
        self.assertGreater(varied["repetition"]["score"],
                           repeated["repetition"]["score"])

    def test_information_density_rewards_variety(self):
        varied = self._single(_GOOD_TEXT).metadata["quality_detail"]
        repetitive = self._single("the the the the the the.").metadata[
            "quality_detail"]
        self.assertGreater(varied["information_density"]["score"],
                           repetitive["information_density"]["score"])

    # ------------------------------------------------------------------ #
    # weights / config
    # ------------------------------------------------------------------ #
    def test_custom_weights_respected(self):
        # Only sentence_completeness with weight 1 -> final == that sub-score.
        doc = self._single(_GOOD_TEXT,
                           weights={"sentence_completeness": 1.0})
        detail = doc.metadata["quality_detail"]
        self.assertAlmostEqual(doc.metadata["quality_score"],
                               detail["sentence_completeness"]["score"],
                               places=5)

    def test_zero_weight_dimension_omitted(self):
        doc = self._single(_GOOD_TEXT, weights={
            "length": 0.0, "sentence_completeness": 1.0})
        detail = doc.metadata["quality_detail"]
        self.assertNotIn("length", detail)
        self.assertIn("sentence_completeness", detail)

    def test_unknown_dimension_raises(self):
        proc = QualityScorer(weights={"bogus": 1.0})
        with self.assertRaises(ValueError):
            proc.process_docs([Document(text="hi")], None)

    def test_all_zero_weights_raises(self):
        proc = QualityScorer(weights={
            "length": 0, "sentence_completeness": 0,
            "special_char_ratio": 0, "repetition": 0,
            "information_density": 0})
        with self.assertRaises(ValueError):
            proc.process_docs([Document(text="hi")], None)

    # ------------------------------------------------------------------ #
    # edge cases / metadata
    # ------------------------------------------------------------------ #
    def test_empty_input(self):
        proc = QualityScorer()
        self.assertEqual(proc.process_docs([], None), [])

    def test_empty_text_dropped_with_min_score(self):
        docs = [Document(text="")]
        result = self._score(docs, min_score=0.5)
        self.assertEqual(len(result), 0)

    def test_preserves_original_metadata(self):
        doc = Document(text=_GOOD_TEXT, metadata={"source": "wiki"})
        result = self._score([doc])
        self.assertEqual(result[0].metadata["source"], "wiki")
        self.assertIn("quality_score", result[0].metadata)

    def test_detail_key_empty_omits_breakdown(self):
        doc = self._single(_GOOD_TEXT, detail_key="")
        self.assertNotIn("quality_detail", doc.metadata)
        self.assertIn("quality_score", doc.metadata)

    def test_custom_score_key(self):
        doc = self._single(_GOOD_TEXT, score_key="my_quality")
        self.assertIn("my_quality", doc.metadata)
        self.assertNotIn("quality_score", doc.metadata)


if __name__ == "__main__":
    unittest.main(verbosity=2)
