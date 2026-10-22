# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_paragraph_stats_profiler.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.paragraph_stats_profiler import ParagraphStatsProfiler
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Well-formed two-paragraph prose: a soft-wrapped first paragraph (single
# line breaks stay INSIDE the paragraph) followed by a one-line paragraph.
# Line spans: "alpha beta gamma" (0,16), "second line here" (17,33),
# blank (34,34), "third" (35,40) -> paragraphs of 33 and 5 chars.
PROSE = "alpha beta gamma\nsecond line here\n\nthird"

PROSE_STATS = {
    "paragraph_count": 2,
    "char_count": 38,
    "mean_paragraph_chars": 19.0,
    "median_paragraph_chars": 19.0,
    "max_paragraph_chars": 33,
    "min_paragraph_chars": 5,
    "longest_paragraph_span": {"start": 0, "end": 33},
    "single_line_paragraph_count": 1,
    "long_paragraph_count": 0,
    "short_paragraph_count": 1,
}

EMPTY_STATS = {
    "paragraph_count": 0,
    "char_count": 0,
    "mean_paragraph_chars": 0.0,
    "median_paragraph_chars": 0.0,
    "max_paragraph_chars": 0,
    "min_paragraph_chars": 0,
    "longest_paragraph_span": None,
    "single_line_paragraph_count": 0,
    "long_paragraph_count": 0,
    "short_paragraph_count": 0,
}


def _doc(text, **metadata):
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


def _paragraphs(text):
    """Direct access to the splitter for ground-truth tests."""
    return ParagraphStatsProfiler._paragraphs(text)


class TestParagraphStatsProfiler(unittest.TestCase):
    """Comprehensive test suite for ParagraphStatsProfiler."""

    def setUp(self):
        self.profiler = ParagraphStatsProfiler()
        self.query = Query(query_str="structure")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _flag_of(self, text):
        """Profile one text with the setUp instance, return the flag."""
        doc = _doc(text)
        self.profiler.process_docs([doc], self.query)
        return doc.metadata["structure_flag"]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: 2000/20 char thresholds, 0.5/0.7 flag ratios,
        'paragraph_stats' / 'structure_flag' metadata keys."""
        p = ParagraphStatsProfiler()
        self.assertEqual(p.long_threshold, 2000)
        self.assertEqual(p.short_threshold, 20)
        self.assertEqual(p.long_ratio, 0.5)
        self.assertEqual(p.fragmented_ratio, 0.7)
        self.assertEqual(p.stats_key, "paragraph_stats")
        self.assertEqual(p.flag_key, "structure_flag")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'paragraph_stats_profiler',
            'description': 'paragraph stats profiler',
            'long_threshold': 500,
            'short_threshold': 40,
            'long_ratio': 0.6,
            'fragmented_ratio': 0.8,
            'stats_key': 'pstats',
            'flag_key': 'sflag',
        })
        p = ParagraphStatsProfiler()
        p._initialize_by_component_configer(configer)
        self.assertEqual(p.long_threshold, 500)
        self.assertEqual(p.short_threshold, 40)
        self.assertEqual(p.long_ratio, 0.6)
        self.assertEqual(p.fragmented_ratio, 0.8)
        self.assertEqual(p.stats_key, 'pstats')
        self.assertEqual(p.flag_key, 'sflag')
        self.assertEqual(p.name, "paragraph_stats_profiler")

    def test_invalid_configuration_raises(self):
        """Out-of-range thresholds/ratios, non-numeric types, bools,
        non-string metadata keys and crossed thresholds all fail at load
        time."""
        base = {
            'name': 'p', 'description': 'd',
            'long_threshold': 2000, 'short_threshold': 20,
            'long_ratio': 0.5, 'fragmented_ratio': 0.7,
            'stats_key': 'paragraph_stats', 'flag_key': 'structure_flag',
        }
        for key, value in (
            ('long_threshold', 0),
            ('long_threshold', -5),
            ('long_threshold', 2.5),
            ('long_threshold', True),
            ('long_threshold', '30'),
            ('short_threshold', -1),
            ('short_threshold', 1.5),
            ('short_threshold', True),
            ('long_ratio', -0.1),
            ('long_ratio', 1.5),
            ('long_ratio', 'x'),
            ('long_ratio', True),
            ('fragmented_ratio', -0.5),
            ('fragmented_ratio', 2),
            ('fragmented_ratio', False),
            ('stats_key', 5),
            ('flag_key', ['x']),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                ParagraphStatsProfiler()._initialize_by_component_configer(
                    self._create_configer(config))

    def test_crossed_thresholds_rejected(self):
        """long_threshold below short_threshold would let one paragraph be
        simultaneously long and short; it is rejected. Equal thresholds
        are fine (strict inequalities can never overlap)."""
        base = {
            'name': 'p', 'description': 'd',
            'long_threshold': 10, 'short_threshold': 50,
        }
        with self.assertRaises(ValueError):
            ParagraphStatsProfiler()._initialize_by_component_configer(
                self._create_configer(base))

        ok = ParagraphStatsProfiler()._initialize_by_component_configer(
            self._create_configer({
                'name': 'p', 'description': 'd',
                'long_threshold': 20, 'short_threshold': 20,
            }))
        self.assertEqual((ok.long_threshold, ok.short_threshold),
                         (20, 20))

    # ========== Paragraph splitting ground truth ==========

    def test_soft_wrapped_prose_is_one_paragraph(self):
        """Single line breaks stay inside the paragraph: three wrapped
        lines yield ONE paragraph of 28 chars (internal breaks counted)."""
        text = "line one\nline two\nline three"
        self.assertEqual(_paragraphs(text), [(0, 28, 28, False)])
        stats = _doc_stats(text)
        self.assertEqual(stats["paragraph_count"], 1)
        self.assertEqual(stats["char_count"], 28)
        self.assertEqual(stats["single_line_paragraph_count"], 0)

    def test_blank_line_run_separates_paragraphs(self):
        """One, three or five blank lines — every run of 1+ blank lines
        is a single boundary and all yield identical statistics."""
        variants = ["A\n\nB", "A\n\n\nB", "A\n\n\n\n\nB"]
        for text in variants:
            self.assertEqual(_paragraphs(text),
                             [(0, 1, 1, True), (len(text) - 1, len(text),
                                                1, True)], repr(text))
        self.assertEqual(_doc_stats("A\n\nB"), _doc_stats("A\n\n\n\nB"))

    def test_whitespace_only_lines_are_blank(self):
        """Lines holding only spaces/tabs separate paragraphs just like
        truly empty lines."""
        self.assertEqual(_paragraphs("A\n \n\t\nB"),
                         [(0, 1, 1, True), (6, 7, 1, True)])

    def test_crlf_treated_like_lf(self):
        """CRLF terminators split and separate exactly like LF: the two
        documents produce identical statistics, spans point into the
        original text, and mixed endings behave the same."""
        crlf = "para one\r\n\r\npara two"
        lf = "para one\n\npara two"
        self.assertEqual(_doc_stats(crlf), _doc_stats(lf))
        self.assertEqual(_paragraphs(crlf),
                         [(0, 8, 8, True), (12, 20, 8, True)])
        self.assertEqual(crlf[12:20], "para two")
        # Mixed CRLF + LF endings still form one blank separator.
        self.assertEqual(_paragraphs("a\r\n\nb"),
                         [(0, 1, 1, True), (4, 5, 1, True)])

    def test_bare_cr_is_a_line_break(self):
        """Legacy bare-CR text: a single CR soft-wraps (one paragraph, CR
        counted as an internal character), a CR run separates."""
        self.assertEqual(_paragraphs("a\rb"), [(0, 3, 3, False)])
        self.assertEqual(_paragraphs("one\r\rtwo"),
                         [(0, 3, 3, True), (5, 8, 3, True)])

    def test_leading_and_trailing_blanks_ignored(self):
        """Leading/trailing blank and whitespace-only lines produce no
        empty paragraphs."""
        self.assertEqual(_paragraphs("\n\n  \nA\n\n"), [(5, 6, 1, True)])

    def test_paragraph_trimmed_to_non_whitespace_bounds(self):
        """Outer indentation/padding is trimmed from spans and lengths;
        internal breaks and inner spacing stay counted. The 3-line run
        spans chars 2..27 = 25 characters."""
        text = "  padded  \n  inner  \n  para  "
        self.assertEqual(_paragraphs(text), [(2, 27, 25, False)])
        self.assertEqual(text[2:27], "padded  \n  inner  \n  para")
        self.assertEqual(_doc_stats(text)["char_count"], 25)

    def test_span_reconstructs_paragraph(self):
        """text[start:end] of the longest span reproduces the paragraph
        exactly, starting and ending on non-whitespace."""
        doc = _doc(PROSE)
        self.profiler.process_docs([doc], self.query)
        span = doc.metadata["paragraph_stats"]["longest_paragraph_span"]
        self.assertEqual(PROSE[span["start"]:span["end"]],
                         "alpha beta gamma\nsecond line here")
        self.assertFalse(PROSE[span["start"]].isspace())
        self.assertFalse(PROSE[span["end"] - 1].isspace())

    def test_longest_span_first_on_ties(self):
        """Equal-length maxima: the FIRST longest paragraph wins, making
        the span a deterministic function of the text."""
        self.assertEqual(_paragraphs("aaaa\n\nbbbb")[0][:2], (0, 4))
        doc = _doc("aaaa\n\nbbbb")
        self.profiler.process_docs([doc], self.query)
        self.assertEqual(
            doc.metadata["paragraph_stats"]["longest_paragraph_span"],
            {"start": 0, "end": 4})

    # ========== Statistics ground truth ==========

    def test_full_statistics_dict_of_prose(self):
        """Every metric of the reference prose, hand-computed: counts,
        totals, mean/median (odd run of 2), min/max, span, single-line
        and offender counts."""
        doc = _doc(PROSE)
        self.profiler.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["paragraph_stats"], PROSE_STATS)

    def test_hand_computed_mean_median_even_count(self):
        """Lengths 4, 8, 12, 16: mean 10.0, median the average of the two
        middle values (8+12)/2 = 10.0."""
        text = "aaaa\n\nbbbbbbbb\n\ncccccccccccc\n\ndddddddddddddddd"
        stats = _doc_stats(text)
        self.assertEqual(stats["paragraph_count"], 4)
        self.assertEqual(stats["char_count"], 40)
        self.assertEqual(stats["mean_paragraph_chars"], 10.0)
        self.assertEqual(stats["median_paragraph_chars"], 10.0)
        self.assertEqual(stats["max_paragraph_chars"], 16)
        self.assertEqual(stats["min_paragraph_chars"], 4)

    def test_hand_computed_mean_median_odd_count(self):
        """Lengths 3, 7, 11: mean 7.0, median the middle value 7.0."""
        text = "aaa\n\nbbbbbbb\n\nccccccccccc"
        stats = _doc_stats(text)
        self.assertEqual(stats["paragraph_count"], 3)
        self.assertEqual(stats["char_count"], 21)
        self.assertEqual(stats["mean_paragraph_chars"], 7.0)
        self.assertEqual(stats["median_paragraph_chars"], 7.0)

    def test_offender_counts_with_default_thresholds(self):
        """Defaults: >2000 chars is long, <20 chars is short — counts of
        offenders are reported next to the flag they feed."""
        text = "x" * 2500 + "\n\n" + "y" * 100 + "\n\n" + "z" * 100 + \
            "\n\n" + "w" * 15
        stats = _doc_stats(text)
        self.assertEqual(stats["paragraph_count"], 4)
        self.assertEqual(stats["char_count"], 2715)
        self.assertEqual(stats["long_paragraph_count"], 1)
        self.assertEqual(stats["short_paragraph_count"], 1)
        self.assertEqual(stats["single_line_paragraph_count"], 4)

    def test_threshold_comparison_is_strict(self):
        """Exactly at a threshold a paragraph is neither offender:
        20 chars is not short (<20) and 2000 chars is not long (>2000)."""
        stats = _doc_stats("q" * 20 + "\n\n" + "r" * 2000)
        self.assertEqual(stats["short_paragraph_count"], 0)
        self.assertEqual(stats["long_paragraph_count"], 0)

    def test_custom_thresholds_change_offender_counts(self):
        """long_threshold/short_threshold are real knobs: tightening both
        turns the same text from clean into flagged territory."""
        text = "a" * 150 + "\n\n" + "b" * 150 + "\n\n" + "c" * 5
        self.assertEqual(_doc_stats(text)["long_paragraph_count"], 0)
        self.profiler.long_threshold = 100
        self.profiler.short_threshold = 10
        doc = _doc(text)
        self.profiler.process_docs([doc], self.query)
        stats = doc.metadata["paragraph_stats"]
        self.assertEqual(stats["long_paragraph_count"], 2)
        self.assertEqual(stats["short_paragraph_count"], 1)

    # ========== Structure flag classification ==========

    def test_flag_none_for_balanced_prose(self):
        """Well-formed prose raises no flag."""
        self.assertEqual(self._flag_of(PROSE), "none")

    def test_flag_long_paragraphs_default_threshold(self):
        """Default thresholds: one 2500-char wall of text holds 2500/2700
        of the characters (> 0.5) -> long_paragraphs."""
        text = "x" * 2500 + "\n\n" + "y" * 100 + "\n\n" + "z" * 100
        self.assertEqual(self._flag_of(text), "long_paragraphs")

    def test_flag_fragmented_default_thresholds(self):
        """Defaults: 8 of 10 paragraphs under 20 chars (0.8 > 0.7) ->
        fragmented."""
        text = "\n\n".join(["a" * 10] * 8 + ["b" * 100] * 2)
        self.assertEqual(self._flag_of(text), "fragmented")

    def test_flag_long_boundary_exactly_at_ratio(self):
        """Exactly 50% of characters in offenders does NOT raise the flag
        (strict >): lengths 11,11 long vs 10,10,2 short = 22/44. The short
        threshold is lowered so only the 2-char paragraph counts as short
        and the fragmented condition stays out of the way."""
        self.profiler.long_threshold = 10
        self.profiler.short_threshold = 5
        self.profiler.long_ratio = 0.5
        at_ratio = "A" * 11 + "\n\n" + "B" * 11 + "\n\n" + "C" * 10 + \
            "\n\n" + "D" * 10 + "\n\n" + "E" * 2
        self.assertEqual(self._flag_of(at_ratio), "none")

        above = "A" * 11 + "\n\n" + "B" * 12 + "\n\n" + "C" * 10 + \
            "\n\n" + "D" * 10 + "\n\n" + "E" * 2
        self.assertEqual(self._flag_of(above), "long_paragraphs")

    def test_flag_fragmented_boundary_exactly_at_ratio(self):
        """Exactly 70% short paragraphs does NOT raise the flag (strict
        >): 7 of 10 short stays 'none', 8 of 10 (0.8) is fragmented."""
        seven = "\n\n".join(["xyz"] * 7 + ["z" * 40] * 3)
        self.assertEqual(self._flag_of(seven), "none")

        eight = "\n\n".join(["xyz"] * 8 + ["z" * 40] * 2)
        self.assertEqual(self._flag_of(eight), "fragmented")

    def test_flag_mixed_when_both_conditions_hold(self):
        """long_threshold=50: a 120-char paragraph holds 120/154 of the
        text (> 0.5) while 9 of 10 paragraphs are short (> 0.7) -> both
        conditions -> mixed."""
        self.profiler.long_threshold = 50
        text = "\n\n".join(["m" * 120] + ["xyz"] * 8 + ["n" * 10])
        self.assertEqual(self._flag_of(text), "mixed")

    def test_flag_ratios_are_configurable(self):
        """Raising long_ratio past the observed share, or lowering it to
        0 (any offender share > 0 flags), flips the verdict."""
        self.profiler.long_threshold = 100
        text = "a" * 150 + "\n\n" + "b" * 150 + "\n\n" + "c" * 100
        # offenders hold 300/400 = 0.75 of the text.
        self.profiler.long_ratio = 0.8
        self.assertEqual(self._flag_of(text), "none")
        self.profiler.long_ratio = 0.7
        self.assertEqual(self._flag_of(text), "long_paragraphs")
        self.profiler.long_ratio = 0
        self.assertEqual(self._flag_of(text), "long_paragraphs")

    # ========== Degenerate inputs ==========

    def test_empty_and_whitespace_only_documents(self):
        """No non-blank line -> zeroed statistics with stable types (0 /
        0.0, span None) and the 'none' flag; None text is tolerated."""
        for text in ("", " ", " \n\t \n   \n"):
            doc = _doc(text)
            self.profiler.process_docs([doc], self.query)
            self.assertEqual(doc.metadata["paragraph_stats"],
                             EMPTY_STATS)
            self.assertEqual(doc.metadata["structure_flag"], "none")

        # A None text (which the Document validator refuses to build
        # directly) is tolerated by the profiling itself.
        stats, flag = self.profiler._profile(None)
        self.assertEqual(stats, EMPTY_STATS)
        self.assertEqual(flag, "none")

    def test_empty_batch(self):
        """An empty batch yields an empty list."""
        self.assertEqual(
            self.profiler.process_docs([], self.query), [])

    # ========== Metadata bookkeeping ==========

    def test_metadata_keys_and_values(self):
        """Both configured keys are stamped; pre-existing metadata
        survives; flag values come from the documented vocabulary."""
        doc = _doc(PROSE, source="crawl", rank=3)
        self.profiler.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["paragraph_stats"], PROSE_STATS)
        self.assertIn(doc.metadata["structure_flag"],
                      ("none", "long_paragraphs", "fragmented", "mixed"))
        self.assertEqual(doc.metadata["source"], "crawl")
        self.assertEqual(doc.metadata["rank"], 3)

    def test_documents_untouched_except_metadata(self):
        """Text and id are never modified, the batch is returned as the
        same list in the same order, and stamping writes through a copied
        mapping rather than mutating the original dict in place."""
        first = _doc(PROSE, source="a")
        second = _doc("short\n\ntext", source="b")
        docs = [first, second]
        first_meta_ref = first.metadata
        second_meta_ref = second.metadata

        result = self.profiler.process_docs(docs, self.query)

        self.assertIs(result, docs)
        self.assertIs(result[0], first)
        self.assertIs(result[1], second)
        self.assertEqual(first.text, PROSE)
        self.assertEqual(second.text, "short\n\ntext")
        self.assertTrue(first.id and second.id)
        # Stats differ per document and are independently computed.
        self.assertEqual(first.metadata["paragraph_stats"],
                         PROSE_STATS)
        self.assertEqual(
            second.metadata["paragraph_stats"]["paragraph_count"], 2)
        # Stamps went through copied mappings.
        self.assertIsNot(first.metadata, first_meta_ref)
        self.assertIsNot(second.metadata, second_meta_ref)
        self.assertNotIn("paragraph_stats", first_meta_ref)
        self.assertNotIn("structure_flag", second_meta_ref)

    def test_disabled_metadata_keys_stamp_nothing(self):
        """Empty stats_key / flag_key disable both stamps."""
        self.profiler.stats_key = ""
        self.profiler.flag_key = ""
        doc = _doc(PROSE, source="wire")
        result = self.profiler.process_docs([doc], self.query)
        self.assertEqual(len(result), 1)
        self.assertEqual(doc.metadata, {"source": "wire"})

    def test_custom_metadata_keys(self):
        """stats_key/flag_key relocate the stamps."""
        self.profiler.stats_key = "pstats"
        self.profiler.flag_key = "sflag"
        doc = _doc(PROSE)
        self.profiler.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["pstats"], PROSE_STATS)
        self.assertEqual(doc.metadata["sflag"], "none")
        self.assertNotIn("paragraph_stats", doc.metadata)

    def test_deterministic_across_instances_and_runs(self):
        """Identical inputs produce identical statistics dicts across
        instances and repeated runs — nothing depends on process state."""
        other = ParagraphStatsProfiler()
        for text in (PROSE, "A\n\nB", "", "x" * 2500):
            run_one = _doc(text)
            run_two = _doc(text)
            self.profiler.process_docs([run_one], self.query)
            self.profiler.process_docs([run_two], self.query)
            other.process_docs([run_two], self.query)
            self.assertEqual(run_one.metadata["paragraph_stats"],
                             run_two.metadata["paragraph_stats"])
            self.assertEqual(run_one.metadata["structure_flag"],
                             run_two.metadata["structure_flag"])

    def test_query_is_ignored(self):
        """Profiling depends only on the text: any query object leaves
        the statistics unchanged."""
        doc_a = _doc(PROSE)
        doc_b = _doc(PROSE)
        self.profiler.process_docs([doc_a], self.query)
        self.profiler.process_docs([doc_b], Query(query_str="other"))
        self.assertEqual(doc_a.metadata["paragraph_stats"],
                         doc_b.metadata["paragraph_stats"])


def _doc_stats(text):
    """Profile one text with a default-configured instance and return
    the statistics dict."""
    profiler = ParagraphStatsProfiler()
    doc = _doc(text)
    profiler.process_docs([doc], Query(query_str="stats"))
    return doc.metadata["paragraph_stats"]


if __name__ == '__main__':
    unittest.main()
