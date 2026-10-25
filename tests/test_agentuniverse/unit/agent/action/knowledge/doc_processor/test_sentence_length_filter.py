# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_sentence_length_filter.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.sentence_length_filter import SentenceLengthFilter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Twelve financial-flavoured sentences, each exactly 10 characters long
# (4-letter word + space + 4-letter word + terminal dot). The exact
# lengths are asserted in test_fixture_lengths so the hand-computed
# statistics below stay trustworthy.
TENS = (
    "Base rate.", "Fund size.", "Risk pool.", "Cash flow.",
    "Loan debt.", "Euro zone.", "Debt note.", "Bank runs.",
    "Bond fund.", "Gold bull.", "Yuan bond.", "Cash call.",
)

# A 47-character legal-disclaimer-flavoured sentence — the kind of
# boilerplate that rides along inside prose and pollutes embeddings.
DISCLAIMER47 = "See the appended legal notice for full details."

# Eight uniform 10-char sentences plus the 47-char disclaimer.
# lengths = [10]*8 + [47]; n = 9.
#   mean    = 127 / 9               = 14.11111...
#   var     = (8 * (10-14.1111)^2 + (47-14.1111)^2) / 9 = 135.20988...
#   stdev   = sqrt(var)             = 11.62800...
#   k=2 threshold = 14.1111 + 23.256 = 37.367  -> 47 IS an outlier
#   k=3 threshold = 14.1111 + 34.884 = 48.995  -> 47 is NOT an outlier
STAT_TEXT = " ".join(TENS[:8] + (DISCLAIMER47,))

# Exact-arithmetic boundary fixture: lengths [2, 2, 6, 6], n = 4.
#   mean = 4.0 (exact), population stdev = 2.0 (exact)
#   k=1.0 -> threshold 6.0: length 6 == threshold -> NOT an outlier
#   (the rule is strictly greater; exactly-at-threshold is kept)
#   k=0.5 -> threshold 5.0: 6 > 5 -> outliers at indices 2 and 3
BOUNDARY_TEXT = "A! B! Cdefg! Cdefg!"

# Two sentences (below the default min_sentences=3): lengths [10, 200].
# Statistical mode is OFF; only the absolute cap applies.
LONG200 = "M" * 199 + "."
TWO_TEXT = "Base rate. " + LONG200
# With min_sentences=2 the statistics turn exact again:
#   mean = 105.0, stdev = 95.0 (exact)
#   k=2   -> threshold 295.0 -> 200 is NOT an outlier
#   k=0.5 -> threshold 152.5 -> 200 IS an outlier

# Twelve uniform sentences plus one 600-char table-dump sentence that
# trips the default absolute cap (600 > 500) regardless of statistics.
LONG600 = "T" * 599 + "!"
TWELVE_TEXT = " ".join(TENS + (LONG600,))

# CJK fixtures: eight 7-char sentences (6 ideographs + full stop) plus a
# 39-char disclaimer. lengths = [7]*8 + [39]; n = 9.
#   mean  = 95 / 9 = 10.5556
#   stdev = 10.05663...
#   k=2 threshold = 30.669 -> 39 IS an outlier
CJK_SENTENCES = (
    "系统运行正常。", "数据同步完成。", "接口调用成功。", "缓存清理完成。",
    "日志滚动归档。", "带宽使用正常。", "磁盘空间充足。", "证书更新完毕。",
)
CJK_DISCLAIMER = "本报告中的信息均来源于公开资料，本公司对这些信息的准确性及完整性不作任何保证。"
CJK_TEXT = "".join(CJK_SENTENCES) + CJK_DISCLAIMER

# Uniform lengths with irregular inter-sentence whitespace (double space,
# blank lines): no outliers, so even drop mode must stay byte-identical.
UNIFORM_TEXT = "Base rate.  Fund size.\n\nRisk pool. Cash flow."


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestSentenceLengthFilter(unittest.TestCase):
    """Comprehensive test suite for SentenceLengthFilter."""

    def setUp(self):
        self.filter = SentenceLengthFilter()
        self.query = Query(query_str="boilerplate")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _texts(self, text: str):
        """Sentence texts of `text` under default configuration."""
        return [text[start:end]
                for start, end in self.filter._sentences(text)]

    # ========== Fixture self-checks ==========

    def test_fixture_lengths(self):
        """Fixture sentences carry exactly the char lengths the
        hand-computed statistics rely on (terminal punctuation and
        closing quotes included)."""
        for ten in TENS:
            self.assertEqual(len(ten), 10, ten)
        self.assertEqual(len(DISCLAIMER47), 47)
        self.assertEqual(len(LONG200), 200)
        self.assertEqual(len(LONG600), 600)
        for seven in CJK_SENTENCES:
            self.assertEqual(len(seven), 7, seven)
        self.assertEqual(len(CJK_DISCLAIMER), 39)
        self.assertEqual(
            [end - start for start, end in self.filter._sentences(STAT_TEXT)],
            [10] * 8 + [47])
        self.assertEqual(
            [end - start for start, end in self.filter._sentences(CJK_TEXT)],
            [7] * 8 + [39])

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: k 2.0, cap 500, min 3 sentences, tag mode."""
        f = SentenceLengthFilter()
        self.assertEqual(f.k, 2.0)
        self.assertEqual(f.max_chars, 500)
        self.assertEqual(f.min_sentences, 3)
        self.assertEqual(f.mode, "tag")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'sentence_length_filter',
            'description': 'sentence length outlier filter',
            'k': 1.5,
            'max_chars': 120,
            'min_sentences': 5,
            'mode': 'drop',
        })
        f = SentenceLengthFilter()
        f._initialize_by_component_configer(configer)
        self.assertEqual(f.k, 1.5)
        self.assertEqual(f.max_chars, 120)
        self.assertEqual(f.min_sentences, 5)
        self.assertEqual(f.mode, "drop")
        self.assertEqual(f.name, "sentence_length_filter")
        self.assertEqual(f.description, "sentence length outlier filter")

    def test_k_accepts_integer(self):
        """An integer k is a valid number and is applied as-is."""
        configer = self._create_configer({
            'name': 'f', 'description': 'd', 'k': 3,
        })
        f = SentenceLengthFilter()
        f._initialize_by_component_configer(configer)
        self.assertEqual(f.k, 3)

    def test_invalid_configuration_raises(self):
        """Non-positive k, bad caps, bad min_sentences and unknown modes
        all fail eagerly at load time."""
        base = {
            'name': 'f', 'description': 'd',
            'k': 2.0, 'max_chars': 500, 'min_sentences': 3, 'mode': 'tag',
        }
        for key, value in (
            ('k', 0),
            ('k', -0.5),
            ('k', True),
            ('k', "2"),
            ('max_chars', 0),
            ('max_chars', -5),
            ('max_chars', True),
            ('max_chars', 2.5),
            ('min_sentences', 0),
            ('min_sentences', True),
            ('min_sentences', 1.5),
            ('mode', 'remove'),
            ('mode', ''),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                SentenceLengthFilter()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Segmentation tests ==========

    def test_segmentation_abbreviations_and_initials(self):
        """Known abbreviations and single-letter initials do not split;
        real sentence dots do."""
        self.assertEqual(self._texts("Dr. Smith asked. Ms. Lee replied."),
                         ["Dr. Smith asked.", "Ms. Lee replied."])

    def test_segmentation_decimal_point(self):
        """A decimal dot inside a number does not split."""
        self.assertEqual(self._texts("Pi is 3.14 rounded."),
                         ["Pi is 3.14 rounded."])

    def test_segmentation_ellipsis(self):
        """An ellipsis splits only at its final dot."""
        self.assertEqual(self._texts("Wait... then go."),
                         ["Wait...", "then go."])

    def test_segmentation_terminal_run_and_quotes(self):
        """A terminal punctuation run plus closing quotes stays inside
        the sentence it terminates."""
        self.assertEqual(self._texts('"Are you sure?" she asked.'),
                         ['"Are you sure?"', 'she asked.'])

    def test_segmentation_cjk_boundaries(self):
        """CJK full stops and terminal runs split sentences."""
        self.assertEqual(self._texts("好的。嗯。"), ["好的。", "嗯。"])
        self.assertEqual(self._texts("真的吗？！当然。"),
                         ["真的吗？！", "当然。"])

    def test_segmentation_trailing_without_punctuation(self):
        """A trailing segment without terminal punctuation still counts
        as a sentence."""
        self.assertEqual(self._texts("one. two three"),
                         ["one.", "two three"])

    def test_segmentation_drops_punctuation_husks(self):
        """Bare punctuation runs carry no word and are not sentences."""
        self.assertEqual(self._texts("A! ??? B!"), ["A!", "B!"])

    def test_spans_slice_the_original_text(self):
        """Every span satisfies text[start:end] exactly, spans are
        ordered and non-overlapping, and leading whitespace between
        sentences is skipped."""
        for text in (STAT_TEXT, TWO_TEXT, CJK_TEXT, UNIFORM_TEXT,
                     '"Are you sure?" she asked.'):
            spans = self.filter._sentences(text)
            previous_end = 0
            for start, end in spans:
                self.assertGreaterEqual(start, previous_end)
                self.assertLess(start, end)
                self.assertTrue(text[start:end].strip())
                self.assertTrue(self.filter._has_word(text[start:end]))
                previous_end = end

    # ========== Statistics and outlier-rule tests ==========

    def test_statistical_outlier_detected(self):
        """The 47-char disclaimer is an outlier among eight 10-char
        sentences at the default k=2 (threshold ~37.37)."""
        self.assertEqual(self.filter._outlier_indices([10] * 8 + [47]), [8])

    def test_k_knob_moves_the_threshold(self):
        """k=3 raises the threshold to ~48.99 and the same 47-char
        sentence is no longer an outlier."""
        self.filter.k = 3
        self.assertEqual(self.filter._outlier_indices([10] * 8 + [47]), [])

    def test_boundary_exactly_at_statistical_threshold_is_kept(self):
        """lengths [2,2,6,6]: mean 4.0, population stdev 2.0 (both
        exact). With k=1 the threshold is exactly 6.0 and a length of 6
        is NOT an outlier — the rule is strictly greater."""
        lengths = [end - start
                   for start, end in self.filter._sentences(BOUNDARY_TEXT)]
        self.assertEqual(lengths, [2, 2, 6, 6])

        self.filter.k = 1
        self.assertEqual(self.filter._outlier_indices(lengths), [])

        self.filter.k = 0.5
        self.assertEqual(self.filter._outlier_indices(lengths), [2, 3])

    def test_zero_stdev_flags_nothing(self):
        """All sentences equally long: mean == length, stdev == 0, so no
        sentence is strictly greater than the threshold."""
        self.assertEqual(self.filter._outlier_indices([10, 10, 10, 10]), [])
        self.assertEqual(self.filter._outlier_indices([7, 7, 7]), [])

    def test_below_min_sentences_statistics_disabled(self):
        """With two sentences (below min_sentences=3) even a 200-char
        sentence among 10-char ones is not flagged: the mean of two
        sentences is noise, not a norm."""
        lengths = [10, 200]
        self.assertEqual(self.filter._outlier_indices(lengths), [])
        # A huge k must not change that either.
        self.filter.k = 0.01
        self.assertEqual(self.filter._outlier_indices(lengths), [])

    def test_min_sentences_knob_enables_statistics(self):
        """min_sentences=2 turns the statistical rule on for the same
        pair: mean 105, stdev 95 (exact). k=2 keeps 200 (threshold 295);
        k=0.5 flags it (threshold 152.5)."""
        self.filter.min_sentences = 2
        self.filter.k = 2
        self.assertEqual(self.filter._outlier_indices([10, 200]), [])
        self.filter.k = 0.5
        self.assertEqual(self.filter._outlier_indices([10, 200]), [1])

    def test_absolute_cap_boundary_exclusive(self):
        """length > max_chars is required: exactly at the cap the
        sentence is kept, one char over is flagged."""
        self.filter.max_chars = 200
        self.assertEqual(self.filter._outlier_indices([10, 200]), [])
        self.filter.max_chars = 199
        self.assertEqual(self.filter._outlier_indices([10, 200]), [1])

    def test_cap_applies_even_when_statistics_say_no(self):
        """The cap is an OR-branch: with k huge (threshold far above any
        length) only the cap can flag the disclaimer."""
        self.filter.k = 100
        self.filter.max_chars = 47
        self.assertEqual(self.filter._outlier_indices([10] * 8 + [47]), [])
        self.filter.max_chars = 46
        self.assertEqual(self.filter._outlier_indices([10] * 8 + [47]), [8])

    # ========== tag mode ==========

    def test_tag_mode_stamps_metadata_and_keeps_text(self):
        """Default mode records index / length / span of every outlier
        and leaves the document byte-identical."""
        doc = _doc(STAT_TEXT, source="report")
        result = self.filter.process_docs([doc], self.query)

        self.assertIs(result[0], doc)
        self.assertEqual(doc.text, STAT_TEXT)
        self.assertEqual(doc.metadata["source"], "report")

        outliers = doc.metadata["sentence_outliers"]
        self.assertEqual(len(outliers), 1)
        start, end = outliers[0]["span"]
        self.assertEqual(outliers[0]["index"], 8)
        self.assertEqual(outliers[0]["length"], 47)
        self.assertEqual(STAT_TEXT[start:end], DISCLAIMER47)
        # No removal bookkeeping in tag mode.
        self.assertNotIn("sentence_removed_count", doc.metadata)
        self.assertNotIn("sentence_removed", doc.metadata)

    def test_tag_mode_no_outliers(self):
        """Uniform sentence lengths yield an empty outlier list and an
        untouched document."""
        doc = _doc(UNIFORM_TEXT)
        self.filter.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["sentence_outliers"], [])
        self.assertEqual(doc.text, UNIFORM_TEXT)

    # ========== drop mode ==========

    def test_drop_mode_removes_outliers_and_rejoins(self):
        """drop strips the disclaimer, rejoins survivors with single
        spaces, and records the removal."""
        self.filter.mode = "drop"
        doc = _doc(STAT_TEXT)
        self.filter.process_docs([doc], self.query)

        self.assertEqual(doc.text, " ".join(TENS[:8]))
        self.assertEqual(doc.metadata["sentence_removed_count"], 1)
        self.assertEqual(doc.metadata["sentence_removed"], [DISCLAIMER47])
        # The outlier list still refers to the pre-filter text.
        outliers = doc.metadata["sentence_outliers"]
        self.assertEqual(len(outliers), 1)
        start, end = outliers[0]["span"]
        self.assertEqual(STAT_TEXT[start:end], DISCLAIMER47)

    def test_drop_mode_no_outliers_is_byte_identical(self):
        """With nothing to remove the text is returned untouched —
        irregular whitespace included, no rejoin, no normalisation."""
        self.filter.mode = "drop"
        doc = _doc(UNIFORM_TEXT)
        self.filter.process_docs([doc], self.query)
        self.assertEqual(doc.text, UNIFORM_TEXT)
        self.assertEqual(doc.metadata["sentence_removed_count"], 0)
        self.assertEqual(doc.metadata["sentence_removed"], [])

    def test_drop_mode_multiple_outliers(self):
        """Two boundary outliers (k=0.5 on [2,2,6,6]) are both removed
        and the rejoin keeps sentence order."""
        self.filter.mode = "drop"
        self.filter.k = 0.5
        doc = _doc(BOUNDARY_TEXT)
        self.filter.process_docs([doc], self.query)
        self.assertEqual(doc.text, "A! B!")
        self.assertEqual(doc.metadata["sentence_removed_count"], 2)
        self.assertEqual(doc.metadata["sentence_removed"],
                         ["Cdefg!", "Cdefg!"])

    def test_drop_mode_cap_outlier(self):
        """A 600-char table dump trips the absolute cap and is dropped
        from a twelve-sentence document."""
        self.filter.mode = "drop"
        doc = _doc(TWELVE_TEXT)
        self.filter.process_docs([doc], self.query)
        self.assertEqual(doc.text, " ".join(TENS))
        self.assertEqual(doc.metadata["sentence_removed_count"], 1)
        self.assertEqual(doc.metadata["sentence_removed"], [LONG600])

    # ========== keep_only mode ==========

    def test_keep_only_mode_keeps_outliers(self):
        """keep_only inverts the filter: only the disclaimer survives,
        rejoined with single spaces."""
        self.filter.mode = "keep_only"
        doc = _doc(STAT_TEXT)
        self.filter.process_docs([doc], self.query)
        self.assertEqual(doc.text, DISCLAIMER47)
        self.assertEqual(doc.metadata["sentence_removed_count"], 8)
        self.assertEqual(doc.metadata["sentence_removed"], list(TENS[:8]))
        self.assertEqual(len(doc.metadata["sentence_outliers"]), 1)

    def test_keep_only_mode_caps_removed_texts_at_ten(self):
        """The removed-text list is capped at 10 entries while
        sentence_removed_count stays the uncapped total (12)."""
        self.filter.mode = "keep_only"
        doc = _doc(TWELVE_TEXT)
        self.filter.process_docs([doc], self.query)
        self.assertEqual(doc.text, LONG600)
        self.assertEqual(doc.metadata["sentence_removed_count"], 12)
        self.assertEqual(len(doc.metadata["sentence_removed"]), 10)
        self.assertEqual(doc.metadata["sentence_removed"], list(TENS[:10]))

    def test_keep_only_mode_without_outliers_empties_text(self):
        """No outliers means nothing survives: the text becomes the empty
        join, and every normal sentence counts as removed."""
        self.filter.mode = "keep_only"
        doc = _doc(UNIFORM_TEXT)
        self.filter.process_docs([doc], self.query)
        self.assertEqual(doc.text, "")
        self.assertEqual(doc.metadata["sentence_removed_count"], 4)
        self.assertEqual(doc.metadata["sentence_removed"],
                         ["Base rate.", "Fund size.", "Risk pool.",
                          "Cash flow."])

    # ========== CJK documents ==========

    def test_cjk_statistical_outlier(self):
        """The 39-char Chinese disclaimer is an outlier among eight
        7-char sentences (k=2 threshold ~30.67)."""
        doc = _doc(CJK_TEXT)
        self.filter.process_docs([doc], self.query)
        outliers = doc.metadata["sentence_outliers"]
        self.assertEqual(len(outliers), 1)
        self.assertEqual(outliers[0]["index"], 8)
        self.assertEqual(outliers[0]["length"], 39)
        start, end = outliers[0]["span"]
        self.assertEqual(CJK_TEXT[start:end], CJK_DISCLAIMER)

    def test_cjk_drop_mode_rejoin(self):
        """drop removes the Chinese disclaimer and rejoins the survivors
        with single spaces."""
        self.filter.mode = "drop"
        doc = _doc(CJK_TEXT)
        self.filter.process_docs([doc], self.query)
        self.assertEqual(doc.text, " ".join(CJK_SENTENCES))
        self.assertEqual(doc.metadata["sentence_removed"],
                         [CJK_DISCLAIMER])

    # ========== Pipeline-shape and edge cases ==========

    def test_empty_batch_and_empty_documents(self):
        """An empty batch returns []; empty / blank / husk-only documents
        carry an empty outlier list and keep their text unchanged in
        every mode."""
        self.assertEqual(self.filter.process_docs([], self.query), [])

        for text in ("", "   ", "???!"):
            doc = Document(text=text)
            self.filter.process_docs([doc], self.query)
            self.assertEqual(doc.metadata["sentence_outliers"], [])
            self.assertEqual(doc.text, text)

        self.filter.mode = "drop"
        doc = _doc("???!")
        self.filter.process_docs([doc], self.query)
        self.assertEqual(doc.text, "???!")
        self.assertEqual(doc.metadata["sentence_removed_count"], 0)

    def test_documents_in_a_batch_are_independent(self):
        """Each document is measured against its own sentences; a
        boilerplate-heavy doc does not change a clean doc's norm."""
        clean = _doc(UNIFORM_TEXT)
        dirty = _doc(STAT_TEXT)
        result = self.filter.process_docs([clean, dirty], self.query)
        self.assertEqual([d.text for d in result],
                         [UNIFORM_TEXT, STAT_TEXT])
        self.assertEqual(clean.metadata["sentence_outliers"], [])
        self.assertEqual(len(dirty.metadata["sentence_outliers"]), 1)

    def test_existing_metadata_preserved_and_copied(self):
        """Pre-existing metadata entries survive, and stamps go through
        a copied mapping — the caller's original dict never gains keys
        in place."""
        doc = _doc(STAT_TEXT, source="wire", rank=1)
        meta_ref = doc.metadata
        self.filter.process_docs([doc], self.query)

        self.assertEqual(doc.metadata["source"], "wire")
        self.assertEqual(doc.metadata["rank"], 1)
        self.assertIn("sentence_outliers", doc.metadata)
        self.assertNotIn("sentence_outliers", meta_ref)
        self.assertIsNot(doc.metadata, meta_ref)

    def test_deterministic_across_runs_and_instances(self):
        """Identical inputs produce identical text and metadata across
        repeated runs and independent instances, in every mode."""
        for mode in ("tag", "drop", "keep_only"):
            self.filter.mode = mode
            runs = []
            for _ in range(2):
                doc = _doc(STAT_TEXT)
                self.filter.process_docs([doc], self.query)
                runs.append(doc)
            other = SentenceLengthFilter()
            other.mode = mode
            third = _doc(STAT_TEXT)
            other.process_docs([third], self.query)
            runs.append(third)

            self.assertEqual(runs[0].text, runs[1].text)
            self.assertEqual(runs[0].metadata, runs[1].metadata)
            self.assertEqual(runs[0].text, runs[2].text)
            self.assertEqual(runs[0].metadata, runs[2].metadata)


if __name__ == '__main__':
    unittest.main()
