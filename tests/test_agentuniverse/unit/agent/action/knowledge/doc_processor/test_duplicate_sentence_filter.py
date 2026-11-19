# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_duplicate_sentence_filter.py

import os
import subprocess
import sys
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.duplicate_sentence_filter import DuplicateSentenceFilter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Nine-token base sentence used by the Jaccard boundary tests: adding one
# token gives token sets of size 9 and 10 with Jaccard 9/10 = 0.9 exactly.
NINE_TOKENS = "alpha beta gamma delta epsilon zeta eta theta iota"
TEN_TOKENS = NINE_TOKENS + " kappa"

# Eight-token variant: adding one token gives 8/9 ~ 0.889, below 0.9.
EIGHT_TOKENS = "alpha beta gamma delta epsilon zeta eta theta"
NINE_FROM_EIGHT = EIGHT_TOKENS + " iota"

# Length-class probe: 18 shared tokens plus 2 extra ones yield token-set
# sizes 18 and 20 (word-count gap 2) with Jaccard 18/20 = 0.9.
EIGHTEEN_TOKENS = " ".join(f"m{i}" for i in range(18))
TWENTY_TOKENS = EIGHTEEN_TOKENS + " x0 x1"

# Documented window corner: sizes 30 and 33 (gap 3) share all 30 tokens,
# Jaccard 30/33 ~ 0.909 >= 0.9, but the +-2 bucket window never compares
# them, so both survive.
THIRTY_TOKENS = " ".join(f"n{i}" for i in range(30))
THIRTY_THREE_TOKENS = THIRTY_TOKENS + " y0 y1 y2"


def _doc(text, **metadata):
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


def _run(filter_, text):
    """Process one document and return (text, metadata) after the run."""
    doc = _doc(text)
    result = filter_.process_docs([doc])
    assert result == [doc]
    return doc.text, doc.metadata


class TestDuplicateSentenceFilter(unittest.TestCase):
    """Comprehensive offline test suite for DuplicateSentenceFilter."""

    def setUp(self):
        self.filter = DuplicateSentenceFilter()
        self.query = Query(query_str="clean boilerplate")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    # ========== Configuration tests ==========

    def test_default_configuration(self):
        """Defaults: exact mode, threshold 0.9, keep_first."""
        f = DuplicateSentenceFilter()
        self.assertEqual(f.mode, "exact")
        self.assertEqual(f.jaccard_threshold, 0.9)
        self.assertFalse(f.keep_last)

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'duplicate_sentence_filter',
            'description': 'duplicate sentence filter',
            'mode': 'near',
            'jaccard_threshold': 0.75,
            'keep_last': True,
        })
        f = DuplicateSentenceFilter()
        f._initialize_by_component_configer(configer)
        self.assertEqual(f.mode, "near")
        self.assertEqual(f.jaccard_threshold, 0.75)
        self.assertTrue(f.keep_last)
        self.assertEqual(f.name, "duplicate_sentence_filter")
        self.assertEqual(f.description, "duplicate sentence filter")

    def test_invalid_mode_raises(self):
        """Unknown modes fail eagerly at load time."""
        configer = self._create_configer({
            'name': 'f', 'description': 'd', 'mode': 'fuzzy',
        })
        with self.assertRaises(ValueError):
            DuplicateSentenceFilter()._initialize_by_component_configer(
                configer)

    def test_invalid_threshold_raises(self):
        """Zero, out-of-range, non-numeric and boolean thresholds fail."""
        for bad in (0, -0.1, 1.5, "high", True):
            configer = self._create_configer({
                'name': 'f', 'description': 'd',
                'jaccard_threshold': bad,
            })
            with self.assertRaises(ValueError):
                DuplicateSentenceFilter()._initialize_by_component_configer(
                    configer)

    def test_boundary_threshold_values_accepted(self):
        """1 (int) and 1.0 are valid thresholds; 0.5 likewise."""
        for good, expected in ((1, 1.0), (1.0, 1.0), (0.5, 0.5)):
            configer = self._create_configer({
                'name': 'f', 'description': 'd',
                'jaccard_threshold': good,
            })
            f = DuplicateSentenceFilter()
            f._initialize_by_component_configer(configer)
            self.assertEqual(f.jaccard_threshold, expected)

    # ========== Exact mode tests ==========

    def test_exact_duplicates_normalized_variants(self):
        """Case, trailing punctuation and whitespace variants collapse to
        one key; only the first occurrence survives."""
        text = ("Intro line here. The quick brown fox jumps. "
                "Some middle text. THE QUICK BROWN FOX JUMPS! Final "
                "words. the QUICK   brown fox jumps...")
        text, meta = _run(self.filter, text)
        self.assertEqual(
            text,
            "Intro line here. The quick brown fox jumps. Some middle "
            "text. Final words.")
        self.assertEqual(meta["duplicate_count"], 2)
        self.assertEqual(meta["duplicate_mode"], "exact")
        entries = meta["duplicate_sentences"]
        self.assertEqual([e["index"] for e in entries], [3, 5])
        self.assertEqual([e["similarity"] for e in entries], [1.0, 1.0])

    def test_span_and_length_values(self):
        """Removal entries carry exact original-text offsets and lengths."""
        original = "One two. Three four. one TWO!"
        text, meta = _run(self.filter, original)
        self.assertEqual(text, "One two. Three four.")
        entry = meta["duplicate_sentences"][0]
        self.assertEqual(entry["index"], 2)
        self.assertEqual(entry["span"], [21, 29])
        self.assertEqual(entry["length"], 8)
        self.assertEqual(entry["similarity"], 1.0)
        self.assertEqual(original[entry["span"][0]:entry["span"][1]],
                         "one TWO!")

    def test_no_duplicates_passthrough_byte_identical(self):
        """Text without duplicates is returned byte-identical; decimals
        and dotted abbreviations are never split into false dupes."""
        text = ("Pi is about 3.14159 rad. See e.g. the appendix. End "
                "of section.\n\nTrailing paragraph here.  \n")
        out, meta = _run(self.filter, text)
        self.assertEqual(out, text)
        self.assertEqual(meta["duplicate_count"], 0)
        self.assertEqual(meta["duplicate_sentences"], [])

    def test_distinct_sentences_never_dropped(self):
        """Sentences differing by one word keep distinct keys and all
        survive in exact mode."""
        text = ("Their report is final. There report is final. Those "
                "reports are drafts.")
        out, meta = _run(self.filter, text)
        self.assertEqual(out, text)
        self.assertEqual(meta["duplicate_count"], 0)

    def test_keep_first_and_keep_last(self):
        """Default keeps the first occurrence; keep_last keeps the last
        and drops the earlier ones instead."""
        text = ("Alpha beta. Gamma delta. Alpha beta. Epsilon zeta. "
                "Alpha beta.")
        first_text, first_meta = _run(self.filter, text)
        self.assertEqual(first_text,
                         "Alpha beta. Gamma delta. Epsilon zeta.")
        self.assertEqual(
            [e["index"] for e in first_meta["duplicate_sentences"]],
            [2, 4])

        self.filter.keep_last = True
        last_text, last_meta = _run(self.filter, text)
        self.assertEqual(last_text,
                         "Gamma delta. Epsilon zeta. Alpha beta.")
        self.assertEqual(
            [e["index"] for e in last_meta["duplicate_sentences"]],
            [0, 2])
        self.assertEqual(last_meta["duplicate_count"], 2)

    def test_original_whitespace_preserved_between_kept_sentences(self):
        """Adjacent kept sentences keep their exact original separator;
        a removed sentence takes its preceding gap with it; the trailing
        gap survives only when the final sentence survives."""
        text = "A b.\n\n\nC d. A b."
        out, meta = _run(self.filter, text)
        self.assertEqual(out, "A b.\n\n\nC d.")
        self.assertEqual(meta["duplicate_count"], 1)

        out, _ = _run(self.filter, "A b. A b. C d.  \n")
        self.assertEqual(out, "A b. C d.  \n")

    def test_leading_removed_sentence_leaves_no_leading_space(self):
        """keep_last with the first sentence removed: the rebuilt text
        does not start with the removed sentence's separator."""
        self.filter.keep_last = True
        out, _ = _run(self.filter, "Old headline here. Body stays put. "
                                   "Old headline here.")
        self.assertEqual(out, "Body stays put. Old headline here.")

    def test_punctuation_only_sentences_never_merged(self):
        """Sentences normalizing to an empty key are never duplicates."""
        text = "! ? ! ... !!!"
        out, meta = _run(self.filter, text)
        self.assertEqual(out, text)
        self.assertEqual(meta["duplicate_count"], 0)

    def test_empty_whitespace_and_none_texts(self):
        """Empty, whitespace-only and None texts pass through untouched
        with zero-count metadata stamped."""
        for original in ("", "   \n\t  "):
            doc = _doc(original)
            self.filter.process_docs([doc])
            self.assertEqual(doc.text, original)
            self.assertEqual(doc.metadata["duplicate_count"], 0)
            self.assertEqual(doc.metadata["duplicate_sentences"], [])
            self.assertEqual(doc.metadata["duplicate_mode"], "exact")
        # None text (only reachable via post-construction assignment)
        # is likewise left alone.
        doc = _doc("")
        doc.text = None
        self.filter.process_docs([doc])
        self.assertIsNone(doc.text)
        self.assertEqual(doc.metadata["duplicate_count"], 0)

    def test_cjk_sentences(self):
        """CJK sentences split at 。/！ without spaces; repeated ones
        (differing only in terminal punctuation) deduplicate."""
        text = ("智能体是未来的方向。普通用户需要工具。"
                "智能体是未来的方向！数据很重要。")
        out, meta = _run(self.filter, text)
        self.assertEqual(
            out, "智能体是未来的方向。普通用户需要工具。数据很重要。")
        self.assertEqual(meta["duplicate_count"], 1)
        entry = meta["duplicate_sentences"][0]
        self.assertEqual(entry["index"], 2)
        self.assertEqual(entry["similarity"], 1.0)

    def test_metadata_entry_cap_with_full_total(self):
        """duplicate_sentences is capped at 50 entries while
        duplicate_count reports the uncapped total."""
        text = "Same sentence here." + " Same sentence here." * 60
        out, meta = _run(self.filter, text)
        self.assertEqual(out, "Same sentence here.")
        self.assertEqual(meta["duplicate_count"], 60)
        entries = meta["duplicate_sentences"]
        self.assertEqual(len(entries), 50)
        # Document order preserved: first entry is the second sentence.
        self.assertEqual(entries[0]["index"], 1)
        self.assertEqual(entries[49]["index"], 50)
        self.assertTrue(all(e["similarity"] == 1.0 for e in entries))

    def test_metadata_map_copied_before_mutation(self):
        """A metadata mapping shared across documents is never mutated
        in place; existing entries survive the stamp."""
        shared = {"source": "web"}
        doc = _doc("A b. A b.", **shared)
        self.filter.process_docs([doc])
        self.assertIsNot(doc.metadata, shared)
        self.assertNotIn("duplicate_count", shared)
        self.assertEqual(doc.metadata["source"], "web")
        self.assertEqual(doc.metadata["duplicate_count"], 1)

    def test_deduplication_is_per_document(self):
        """A sentence repeated across two documents survives once in
        EACH document: the filter works within, not across, documents."""
        first, _ = _run(self.filter, "A b. C d. A b.")
        second, _ = _run(self.filter, "A b. A b.")
        self.assertEqual(first, "A b. C d.")
        self.assertEqual(second, "A b.")

    def test_query_argument_is_accepted_and_ignored(self):
        """The public entry point accepts a Query and ignores it."""
        doc = _doc("Repeat after me. Repeat after me!")
        result = self.filter.process_docs([doc], self.query)
        self.assertEqual(result, [doc])
        self.assertEqual(doc.text, "Repeat after me.")

    # ========== Near mode tests ==========

    def test_near_mode_boundary_inclusive(self):
        """Jaccard exactly 0.9 counts as a duplicate (>= comparison)."""
        self.filter.mode = "near"
        text = NINE_TOKENS + ". " + TEN_TOKENS + "."
        out, meta = _run(self.filter, text)
        self.assertEqual(out, NINE_TOKENS + ".")
        entry = meta["duplicate_sentences"][0]
        self.assertEqual(entry["index"], 1)
        self.assertEqual(entry["similarity"], 0.9)

    def test_near_mode_boundary_exclusive(self):
        """Jaccard 8/9 (~0.889) stays below the threshold: both
        sentences survive."""
        self.filter.mode = "near"
        text = EIGHT_TOKENS + ". " + NINE_FROM_EIGHT + "."
        out, meta = _run(self.filter, text)
        self.assertEqual(out, text)
        self.assertEqual(meta["duplicate_count"], 0)

    def test_near_mode_word_count_gap_two_detected(self):
        """True duplicates whose token counts differ by exactly 2 (the
        bucket window edge) are always compared and caught, even with
        many intervening sentences of other length classes."""
        self.filter.mode = "near"
        fillers = [f"Filler number {i} stays unique." for i in range(6)]
        middle = " ".join(fillers)
        text = EIGHTEEN_TOKENS + ". " + middle + " " + TWENTY_TOKENS + "."
        out, meta = _run(self.filter, text)
        self.assertEqual(out, EIGHTEEN_TOKENS + ". " + middle)
        entry = meta["duplicate_sentences"][0]
        self.assertEqual(entry["index"], 7)
        self.assertEqual(entry["similarity"], 0.9)

    def test_near_mode_word_count_gap_three_documented_corner(self):
        """Sizes 30 vs 33 (gap 3) share all tokens (Jaccard ~0.909) but
        are deliberately never compared: the +-2 window trades this
        corner for linear scans. Locks in the documented behaviour."""
        self.filter.mode = "near"
        text = THIRTY_TOKENS + ". " + THIRTY_THREE_TOKENS + "."
        out, meta = _run(self.filter, text)
        self.assertEqual(out, text)
        self.assertEqual(meta["duplicate_count"], 0)

    def test_near_mode_identical_sentences_similarity_one(self):
        """Identical sentences removed in near mode carry 1.0."""
        self.filter.mode = "near"
        long_sentence = " ".join(f"w{i}" for i in range(40)) + "."
        out, meta = _run(self.filter, long_sentence + " " + long_sentence)
        self.assertEqual(out, long_sentence)
        self.assertEqual(meta["duplicate_sentences"][0]["similarity"],
                         1.0)

    def test_near_mode_distinct_same_length_class_never_dropped(self):
        """Every sentence in one length class (worst-case bucket) with
        disjoint vocabulary survives."""
        self.filter.mode = "near"
        sentences = [" ".join(f"s{i}x{j}" for j in range(10)) + "."
                     for i in range(10)]
        text = " ".join(sentences)
        out, meta = _run(self.filter, text)
        self.assertEqual(out, text)
        self.assertEqual(meta["duplicate_count"], 0)

    def test_near_mode_keep_last(self):
        """keep_last in near mode replaces the earlier occurrence with
        the later near-duplicate."""
        self.filter.mode = "near"
        self.filter.keep_last = True
        text = NINE_TOKENS + ". Filler between here. " + TEN_TOKENS + "."
        out, meta = _run(self.filter, text)
        self.assertEqual(out, "Filler between here. " + TEN_TOKENS + ".")
        entry = meta["duplicate_sentences"][0]
        self.assertEqual(entry["index"], 0)
        self.assertEqual(entry["similarity"], 0.9)

    def test_near_mode_edit_variants_caught(self):
        """A one-word substitution on a 20-token sentence stays above
        the default threshold: sets of 20 with 19 shared give Jaccard
        19/21 ~ 0.905."""
        self.filter.mode = "near"
        words = [f"v{i}" for i in range(20)]
        base_text = " ".join(words) + "."
        swapped = list(words)
        swapped[5] = "changed"
        variant_text = " ".join(swapped) + "."
        text = base_text + " " + variant_text
        out, meta = _run(self.filter, text)
        self.assertEqual(out, base_text)
        entry = meta["duplicate_sentences"][0]
        self.assertEqual(entry["index"], 1)
        self.assertAlmostEqual(entry["similarity"], 19.0 / 21.0,
                               places=12)
        self.assertGreaterEqual(entry["similarity"], 0.9)

    def test_exact_mode_ignores_threshold(self):
        """In exact mode near-identical sentences are kept regardless
        of jaccard_threshold."""
        self.filter.jaccard_threshold = 0.1
        text = "The values are settled here. The values are settled "
        out, meta = _run(self.filter, text + "now.")
        self.assertEqual(out, text + "now.")
        self.assertEqual(meta["duplicate_mode"], "exact")
        self.assertEqual(meta["duplicate_count"], 0)

    # ========== Determinism tests ==========

    def test_determinism_within_process(self):
        """Two fresh filters produce identical text and metadata."""
        text = ("Header sentence. Body differs once. HEADER SENTENCE! "
                "Body differs once? Tail sentence.")
        self.filter.mode = "near"
        first = _doc(text)
        second = _doc(text)
        DuplicateSentenceFilter(mode="near").process_docs([first])
        DuplicateSentenceFilter(mode="near").process_docs([second])
        self.assertEqual(first.text, second.text)
        self.assertEqual(first.metadata, second.metadata)

    def test_determinism_across_hash_seeds(self):
        """Output is independent of PYTHONHASHSEED (no salted hash()
        anywhere in the pipeline)."""
        import agentuniverse.agent.action.knowledge.doc_processor. \
            duplicate_sentence_filter as module
        root = module.__file__
        for _ in range(6):
            root = os.path.dirname(root)
        text = ("Boilerplate notice repeats. Real content differs. "
                "boilerplate notice repeats... Real content differs?")
        code = (
            "from agentuniverse.agent.action.knowledge.doc_processor"
            ".duplicate_sentence_filter import DuplicateSentenceFilter\n"
            "from agentuniverse.agent.action.knowledge.store.document"
            " import Document\n"
            "import os\n"
            "f = DuplicateSentenceFilter()\n"
            "f.mode = 'near'\n"
            "d = Document(text=os.environ['AU_TEXT'])\n"
            "f.process_docs([d])\n"
            "print(repr(d.text))\n"
            "print(repr(d.metadata['duplicate_count']))\n"
        )
        env = dict(os.environ)
        env["PYTHONPATH"] = root
        env["PYTHONHASHSEED"] = "12345"
        env["AU_TEXT"] = text
        result = subprocess.run([sys.executable, "-c", code], env=env,
                                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.filter.mode = "near"
        expected_text, expected_meta = _run(self.filter, text)
        lines = result.stdout.splitlines()
        self.assertEqual(lines[0], repr(expected_text))
        self.assertEqual(lines[1], repr(expected_meta["duplicate_count"]))


if __name__ == "__main__":
    unittest.main()
