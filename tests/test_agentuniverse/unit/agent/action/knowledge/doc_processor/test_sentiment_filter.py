# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: test_sentiment_filter.py

"""
Unit tests for SentimentFilter.

The sentiment scorer is pure Python and dependency-free, so the whole suite is
deterministic and runs offline. The tests cover: scoring polarity for English
and Chinese text, the threshold / min_confidence boundaries, every
allowed_sentiment mode, ordering / metadata stamping, configuration loading
through ComponentConfiger (mirroring how the YAML is parsed), edge cases
(empty input, blank text, metadata text fallback), and input-order
preservation.
"""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.sentiment_filter import \
    SentimentFilter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer


class TestSentimentScoring(unittest.TestCase):
    """The pure scoring / polarity helpers."""

    def setUp(self) -> None:
        self.f = SentimentFilter()

    def test_positive_english_text_scores_positive(self) -> None:
        score, polarity, lang = self.f._analyze(
            "This is great and wonderful, I really love it.")
        self.assertGreater(score, 0.0)
        self.assertEqual(polarity, "positive")
        self.assertEqual(lang, "en")

    def test_negative_english_text_scores_negative(self) -> None:
        score, polarity, lang = self.f._analyze(
            "This is terrible and awful, I hate it.")
        self.assertLess(score, 0.0)
        self.assertEqual(polarity, "negative")
        self.assertEqual(lang, "en")

    def test_neutral_english_text_is_neutral(self) -> None:
        score, polarity, lang = self.f._analyze(
            "The report contains the quarterly figures.")
        self.assertEqual(polarity, "neutral")
        self.assertLess(abs(score), self.f.threshold)
        self.assertEqual(lang, "en")

    def test_chinese_positive_detected(self) -> None:
        score, polarity, lang = self.f._analyze("这个产品非常好，我很喜欢，强烈推荐。")
        self.assertGreater(score, 0.0)
        self.assertEqual(polarity, "positive")
        self.assertEqual(lang, "zh")

    def test_chinese_negative_detected(self) -> None:
        score, polarity, lang = self.f._analyze("这件商品太糟糕了，非常失望，质量很差。")
        self.assertLess(score, 0.0)
        self.assertEqual(polarity, "negative")
        self.assertEqual(lang, "zh")

    def test_empty_text_is_neutral(self) -> None:
        score, polarity, lang = self.f._analyze("")
        self.assertEqual((score, polarity), (0.0, "neutral"))
        self.assertEqual(lang, "none")

    def test_score_range_bounded(self) -> None:
        for text in [
            "good good good love perfect",
            "bad terrible awful worst hate",
            "the cat sat on the mat",
        ]:
            score, _, _ = self.f._analyze(text)
            self.assertGreaterEqual(score, -1.0)
            self.assertLessEqual(score, 1.0)

    def test_longer_chinese_term_takes_precedence(self) -> None:
        # "非常好" must be scored as the positive compound, and the inner "好"
        # should not be double counted into the negative bucket.
        score_pos, _, _ = self.f._analyze("非常好")
        score_plain, _, _ = self.f._analyze("好")
        self.assertGreater(score_pos, 0.0)
        self.assertGreater(score_plain, 0.0)


class TestThresholdAndConfidence(unittest.TestCase):
    """threshold and min_confidence gate behaviour."""

    def test_threshold_promotes_weak_signal_to_neutral(self) -> None:
        f = SentimentFilter()
        f.threshold = 0.9  # very high bar
        # Mixed-polarity text: "good good bad" -> score (2-1)/3 = 0.33, which
        # is a weak positive signal below the 0.9 bar, so it must be neutral.
        score, polarity, _ = f._analyze("good good bad")
        self.assertLess(abs(score), 0.9)
        self.assertEqual(polarity, "neutral")

    def test_min_confidence_forces_neutral(self) -> None:
        f = SentimentFilter()
        f.min_confidence = 0.9
        # The same weak mixed-polarity signal (|score| ~= 0.33) falls below the
        # 0.9 confidence gate, so it is demoted to neutral.
        _, polarity, _ = f._analyze("good good bad")
        self.assertEqual(polarity, "neutral")

    def test_min_confidence_zero_is_disabled(self) -> None:
        f = SentimentFilter()
        f.min_confidence = 0.0
        _, polarity, _ = f._analyze("This is great.")
        self.assertEqual(polarity, "positive")


class TestFilteringModes(unittest.TestCase):
    """End-to-end _process_docs across allowed_sentiment values."""

    def _docs(self) -> list:
        return [
            Document(text="This is great and wonderful, I love it."),   # positive
            Document(text="This is terrible and awful, I hate it."),    # negative
            Document(text="The report contains the quarterly figures."),  # neutral
        ]

    def test_keep_positive_only(self) -> None:
        f = SentimentFilter()
        f.allowed_sentiment = "positive"
        result = f._process_docs(self._docs())
        self.assertEqual(len(result), 1)
        self.assertIn("great", result[0].text)

    def test_keep_negative_only(self) -> None:
        f = SentimentFilter()
        f.allowed_sentiment = "negative"
        result = f._process_docs(self._docs())
        self.assertEqual(len(result), 1)
        self.assertIn("terrible", result[0].text)

    def test_keep_neutral_only(self) -> None:
        f = SentimentFilter()
        f.allowed_sentiment = "neutral"
        result = f._process_docs(self._docs())
        self.assertEqual(len(result), 1)
        self.assertIn("report", result[0].text)

    def test_keep_all_keeps_everything(self) -> None:
        f = SentimentFilter()
        f.allowed_sentiment = "all"
        result = f._process_docs(self._docs())
        self.assertEqual(len(result), 3)

    def test_empty_input_returns_empty(self) -> None:
        f = SentimentFilter()
        self.assertEqual(f._process_docs([]), [])


class TestMetadataAndOrder(unittest.TestCase):
    """Metadata stamping and input-order preservation."""

    def test_metadata_is_stamped(self) -> None:
        f = SentimentFilter()
        f.allowed_sentiment = "all"
        docs = [Document(text="This is great and wonderful.")]
        f._process_docs(docs)
        meta = docs[0].metadata
        self.assertIn("sentiment_score", meta)
        self.assertEqual(meta["sentiment_polarity"], "positive")
        self.assertEqual(meta["sentiment_language"], "en")

    def test_custom_metadata_keys(self) -> None:
        f = SentimentFilter()
        f.allowed_sentiment = "all"
        f.score_key = "s_score"
        f.polarity_key = "s_pol"
        f.language_key = None
        docs = [Document(text="This is great.")]
        f._process_docs(docs)
        meta = docs[0].metadata
        self.assertIn("s_score", meta)
        self.assertIn("s_pol", meta)
        self.assertNotIn("sentiment_language", meta)
        self.assertNotIn("sentiment_score", meta)

    def test_text_field_fallback(self) -> None:
        f = SentimentFilter()
        f.allowed_sentiment = "positive"
        f.text_field = "content"
        doc = Document(text="", metadata={"content": "amazing and wonderful"})
        result = f._process_docs([doc])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata["sentiment_polarity"], "positive")

    def test_order_preserved_when_all_kept(self) -> None:
        f = SentimentFilter()
        f.allowed_sentiment = "all"
        docs = [
            Document(text="good"),
            Document(text="bad"),
            Document(text="the report says"),
        ]
        result = f._process_docs(docs)
        self.assertEqual([d.text for d in result], [d.text for d in docs])

    def test_query_argument_ignored(self) -> None:
        f = SentimentFilter()
        f.allowed_sentiment = "positive"
        docs = [Document(text="This is great.")]
        # sentiment is intrinsic to the text; the query must not change it.
        result = f._process_docs(docs, query=Query(query_str="hate"))
        self.assertEqual(len(result), 1)


class TestConfiguration(unittest.TestCase):
    """Loading parameters through ComponentConfiger (as the YAML loader does)."""

    def _configer(self, config: dict) -> ComponentConfiger:
        cfg = Configer()
        cfg.value = config
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        if not hasattr(configer, "name"):
            configer.name = config.get("name", "sentiment_filter")
        if not hasattr(configer, "description"):
            configer.description = config.get("description", "")
        return configer

    def test_load_valid_config(self) -> None:
        configer = self._configer({
            "name": "sentiment_filter",
            "allowed_sentiment": "negative",
            "threshold": 0.1,
            "min_confidence": 0.02,
            "language": "en",
        })
        f = SentimentFilter()
        f._initialize_by_component_configer(configer)
        self.assertEqual(f.allowed_sentiment, "negative")
        self.assertAlmostEqual(f.threshold, 0.1)
        self.assertAlmostEqual(f.min_confidence, 0.02)
        self.assertEqual(f.language, "en")

    def test_invalid_allowed_sentiment_raises(self) -> None:
        configer = self._configer({"allowed_sentiment": "happy"})
        with self.assertRaises(ValueError):
            SentimentFilter()._initialize_by_component_configer(configer)

    def test_invalid_language_raises(self) -> None:
        configer = self._configer({"language": "fr"})
        with self.assertRaises(ValueError):
            SentimentFilter()._initialize_by_component_configer(configer)

    def test_threshold_out_of_range_raises(self) -> None:
        configer = self._configer({"threshold": 2.5})
        with self.assertRaises(ValueError):
            SentimentFilter()._initialize_by_component_configer(configer)

    def test_min_confidence_out_of_range_raises(self) -> None:
        configer = self._configer({"min_confidence": -0.1})
        with self.assertRaises(ValueError):
            SentimentFilter()._initialize_by_component_configer(configer)


if __name__ == "__main__":
    unittest.main()
