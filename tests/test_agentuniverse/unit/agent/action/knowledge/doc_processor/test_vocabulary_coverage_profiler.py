# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_vocabulary_coverage_profiler.py

import json
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.vocabulary_coverage_profiler import VocabularyCoverageProfiler
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# 9 tokens / 6 types: the=3, cat=2, sat/on/mat/ran=1 each.
# TTR = 6/9, root TTR = 6/sqrt(9) = 2.0, hapax = 4/9 tokens,
# avg word length = 26/9, stopword hits = the*3 + on = 4 -> 400/9 %.
BASE_TEXT = "the cat sat on the mat the cat ran"

# 8 repetitions of one word: root TTR = 1/sqrt(8) ~ 0.354 -> low diversity.
REPEAT_TEXT = "spam spam spam spam spam spam spam spam"

# 30 distinct words: root TTR = 30/sqrt(30) = sqrt(30) ~ 5.477 > 5.0
# -> high diversity under the default threshold.
DIVERSE_TEXT = (
    "alpha bravo charlie delta echo foxtrot golf hotel india juliet "
    "kilo lima mike november oscar papa quebec romeo sierra tango "
    "uniform victor whiskey xray yankee zulu apple banana cherry dogwood"
)

# 7 distinct CJK characters, each its own token unit.
CJK_TEXT = "我爱北京天安门"


def _doc(text, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    if text is None:
        # A null text needs an explicit id: the model's uuid5 validator
        # cannot hash None.
        return Document(id='doc-null-text', text=None,
                        metadata=dict(metadata) or None)
    return Document(text=text, metadata=dict(metadata) or None)


class TestVocabularyCoverageProfiler(unittest.TestCase):
    """Comprehensive test suite for VocabularyCoverageProfiler."""

    def setUp(self):
        self.profiler = VocabularyCoverageProfiler()
        self.query = Query(query_str="vocabulary")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _profile_text(self, text: str) -> dict:
        """Run the profiler over a single-document batch and return the
        stamped vocabulary statistics dict."""
        docs = self.profiler.process_docs([_doc(text)], self.query)
        return docs[0].metadata['vocabulary']

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: threshold 5.0, 'vocabulary' stats key,
        'vocabulary_flag' flag key."""
        p = VocabularyCoverageProfiler()
        self.assertEqual(p.low_diversity_threshold, 5.0)
        self.assertEqual(p.vocabulary_key, 'vocabulary')
        self.assertEqual(p.flag_key, 'vocabulary_flag')

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'vocabulary_coverage_profiler',
            'description': 'vocabulary profiler',
            'low_diversity_threshold': 3.5,
            'vocabulary_key': 'vocab',
            'flag_key': 'monotony',
        })
        p = VocabularyCoverageProfiler()
        p._initialize_by_component_configer(configer)
        self.assertEqual(p.low_diversity_threshold, 3.5)
        self.assertEqual(p.vocabulary_key, 'vocab')
        self.assertEqual(p.flag_key, 'monotony')
        self.assertEqual(p.name, "vocabulary_coverage_profiler")

    def test_integer_threshold_normalized_to_float(self):
        """An integer threshold is accepted and normalized to float."""
        configer = self._create_configer({
            'name': 'p', 'description': 'd',
            'low_diversity_threshold': 4,
        })
        p = VocabularyCoverageProfiler()
        p._initialize_by_component_configer(configer)
        self.assertEqual(p.low_diversity_threshold, 4.0)
        self.assertIsInstance(p.low_diversity_threshold, float)

    def test_invalid_configuration_raises(self):
        """Non-positive / non-numeric thresholds and non-string metadata
        keys all fail at load time."""
        base = {
            'name': 'p', 'description': 'd',
            'low_diversity_threshold': 5.0,
            'vocabulary_key': 'vocabulary',
            'flag_key': 'vocabulary_flag',
        }
        for key, value in (
            ('low_diversity_threshold', 0),
            ('low_diversity_threshold', -1.5),
            ('low_diversity_threshold', 'high'),
            ('low_diversity_threshold', True),
            ('vocabulary_key', 5),
            ('vocabulary_key', ['x']),
            ('flag_key', 7),
            ('flag_key', None.__class__),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                VocabularyCoverageProfiler()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Hand-computed metric arithmetic ==========

    def test_hand_computed_metrics_on_base_corpus(self):
        """All ten statistics match hand-computed arithmetic for
        9 tokens / 6 types ('the'=3, 'cat'=2, four singletons)."""
        stats = self._profile_text(BASE_TEXT)
        self.assertEqual(stats['token_count'], 9)
        self.assertEqual(stats['type_count'], 6)
        self.assertAlmostEqual(stats['type_token_ratio'], 6 / 9, places=12)
        self.assertAlmostEqual(stats['root_ttr'], 6 / 3.0, places=12)
        self.assertEqual(stats['hapax_count'], 4)
        self.assertAlmostEqual(stats['hapax_ratio'], 4 / 9, places=12)
        self.assertAlmostEqual(stats['avg_word_length'], 26 / 9, places=12)
        self.assertEqual(stats['longest_word'], 'the')
        self.assertAlmostEqual(stats['stopword_coverage'],
                               4 / 9 * 100.0, places=12)
        self.assertEqual(stats['top_5_tokens'],
                         [['the', 3], ['cat', 2],
                          ['mat', 1], ['on', 1], ['ran', 1]])

    def test_root_ttr_length_fairness_documented(self):
        """Classic TTR falls as a corpus is padded with repeats while
        root TTR degrades far more slowly — the reason both ship."""
        short = self._profile_text("alpha bravo charlie delta")
        padded = self._profile_text(" ".join(["alpha", "bravo", "charlie",
                                              "delta"] * 9))
        # Same 4 types; padding multiplies tokens 9x.
        self.assertEqual(padded['type_count'], short['type_count'])
        self.assertEqual(padded['token_count'], 9 * short['token_count'])
        self.assertAlmostEqual(padded['type_token_ratio'],
                               short['type_token_ratio'] / 9.0, places=12)
        self.assertAlmostEqual(padded['root_ttr'],
                               short['root_ttr'] / 3.0, places=12)

    def test_hapax_arithmetic(self):
        """Hapax counts token types occurring exactly once, never twice
        or zero times."""
        all_hapax = self._profile_text("one two three four")
        self.assertEqual(all_hapax['hapax_count'], 4)
        self.assertEqual(all_hapax['hapax_ratio'], 1.0)
        no_hapax = self._profile_text("go go go go stop stop stop stop")
        self.assertEqual(no_hapax['hapax_count'], 0)
        self.assertEqual(no_hapax['hapax_ratio'], 0.0)
        mixed = self._profile_text("a a b c c c d")
        # Types: a=2, b=1, c=3, d=1 -> hapax types are b and d.
        self.assertEqual(mixed['hapax_count'], 2)
        self.assertAlmostEqual(mixed['hapax_ratio'], 2 / 7, places=12)

    def test_case_folding_collapses_to_one_type(self):
        """Mixed-case repetitions of a word count as one type."""
        stats = self._profile_text("Apple apple APPLE apPlE")
        self.assertEqual(stats['token_count'], 4)
        self.assertEqual(stats['type_count'], 1)
        self.assertAlmostEqual(stats['type_token_ratio'], 0.25, places=12)
        self.assertAlmostEqual(stats['root_ttr'], 0.5, places=12)
        self.assertEqual(stats['top_5_tokens'], [['apple', 4]])

    def test_apostrophe_contractions_stay_whole(self):
        """Letters plus one internal apostrophe form a single token."""
        stats = self._profile_text("don't don't stop")
        self.assertEqual(stats['token_count'], 3)
        self.assertEqual(stats['type_count'], 2)
        self.assertEqual(stats['longest_word'], "don't")
        self.assertAlmostEqual(stats['avg_word_length'], 14 / 3, places=12)
        # 'don't' is not in the built-in stopword list.
        self.assertEqual(stats['stopword_coverage'], 0.0)

    def test_longest_word_takes_first_encountered_on_ties(self):
        """Equal-length candidates resolve to the earliest token."""
        stats = self._profile_text("cat dog the")
        self.assertEqual(stats['longest_word'], 'cat')

    # ========== Low-diversity flagging ==========

    def test_repeated_token_document_flagged_low_diversity(self):
        """A document repeating one word has near-zero root TTR and is
        flagged 'low_diversity'."""
        docs = self.profiler.process_docs([_doc(REPEAT_TEXT)], self.query)
        stats = docs[0].metadata['vocabulary']
        self.assertEqual(stats['token_count'], 8)
        self.assertEqual(stats['type_count'], 1)
        self.assertAlmostEqual(stats['root_ttr'], 1 / 8 ** 0.5, places=12)
        self.assertEqual(docs[0].metadata['vocabulary_flag'],
                         'low_diversity')

    def test_diverse_document_not_flagged(self):
        """30 distinct words give root TTR sqrt(30) ~ 5.477, above the
        default 5.0 threshold: no flag."""
        docs = self.profiler.process_docs([_doc(DIVERSE_TEXT)], self.query)
        stats = docs[0].metadata['vocabulary']
        self.assertEqual(stats['token_count'], 30)
        self.assertEqual(stats['type_count'], 30)
        self.assertAlmostEqual(stats['root_ttr'], 30 ** 0.5, places=12)
        self.assertNotIn('vocabulary_flag', docs[0].metadata)

    def test_threshold_boundary_equality_not_flagged(self):
        """Root TTR exactly equal to the threshold is NOT flagged —
        the comparison is strict."""
        # BASE_TEXT root TTR is exactly 2.0 (6 types, 9 tokens).
        self.profiler.low_diversity_threshold = 2.0
        docs = self.profiler.process_docs([_doc(BASE_TEXT)], self.query)
        self.assertEqual(docs[0].metadata['vocabulary']['root_ttr'], 2.0)
        self.assertNotIn('vocabulary_flag', docs[0].metadata)

    def test_threshold_just_below_flags(self):
        """A threshold infinitesimally above the document's root TTR
        flags it; one below does not."""
        self.profiler.low_diversity_threshold = 2.0 + 1e-9
        docs = self.profiler.process_docs([_doc(BASE_TEXT)], self.query)
        self.assertEqual(docs[0].metadata['vocabulary_flag'],
                         'low_diversity')
        self.profiler.low_diversity_threshold = 1.5
        docs = self.profiler.process_docs([_doc(BASE_TEXT)], self.query)
        self.assertNotIn('vocabulary_flag', docs[0].metadata)

    def test_custom_threshold_via_configer(self):
        """A YAML-configured threshold drives flagging."""
        configer = self._create_configer({
            'name': 'p', 'description': 'd',
            'low_diversity_threshold': 1.5,
        })
        p = VocabularyCoverageProfiler()
        p._initialize_by_component_configer(configer)
        # BASE_TEXT root TTR is 2.0 -> above 1.5, unflagged.
        docs = p.process_docs([_doc(BASE_TEXT)], self.query)
        self.assertNotIn('vocabulary_flag', docs[0].metadata)
        # REPEAT_TEXT root TTR ~ 0.354 -> below 1.5, flagged.
        docs = p.process_docs([_doc(REPEAT_TEXT)], self.query)
        self.assertEqual(docs[0].metadata['vocabulary_flag'],
                         'low_diversity')

    def test_tokenless_documents_never_flagged(self):
        """Documents without measurable diversity are not flagged —
        their ratios are null, not low."""
        for text in ('', '   \n\t ', '123 !!! 42-7', '???'):
            docs = self.profiler.process_docs([_doc(text)], self.query)
            self.assertIsNone(
                docs[0].metadata['vocabulary']['root_ttr'],
                msg=f"unexpected root_ttr for {text!r}")
            self.assertNotIn('vocabulary_flag', docs[0].metadata,
                             msg=f"unexpected flag for {text!r}")

    # ========== CJK char-unit path ==========

    def test_cjk_char_unit_metrics(self):
        """Every CJK ideograph is its own token; hand-computed stats for
        seven distinct characters."""
        stats = self._profile_text(CJK_TEXT)
        self.assertEqual(stats['token_count'], 7)
        self.assertEqual(stats['type_count'], 7)
        self.assertAlmostEqual(stats['type_token_ratio'], 1.0, places=12)
        self.assertAlmostEqual(stats['root_ttr'], 7 ** 0.5, places=12)
        self.assertEqual(stats['hapax_count'], 7)
        self.assertEqual(stats['hapax_ratio'], 1.0)
        self.assertEqual(stats['avg_word_length'], 1.0)
        self.assertEqual(stats['longest_word'], '我')
        # Only 我 is in the built-in CJK stopword list: 1/7 * 100 %.
        self.assertAlmostEqual(stats['stopword_coverage'],
                               100.0 / 7, places=12)
        # Ties (all count 1) break by ascending code point.
        self.assertEqual(stats['top_5_tokens'],
                         [['京', 1], ['北', 1], ['天', 1],
                          ['安', 1], ['我', 1]])

    def test_cjk_repeated_chars_flagged(self):
        """A string of one repeated stopword character: full coverage,
        minimal diversity, flagged."""
        stats = self._profile_text("的的的的的")
        self.assertEqual(stats['token_count'], 5)
        self.assertEqual(stats['type_count'], 1)
        self.assertEqual(stats['stopword_coverage'], 100.0)
        docs = self.profiler.process_docs([_doc("的的的的的")], self.query)
        self.assertEqual(docs[0].metadata['vocabulary_flag'],
                         'low_diversity')

    def test_mixed_script_metrics(self):
        """Latin words and CJK chars share one token stream."""
        stats = self._profile_text("The cat 爱吃鱼")
        self.assertEqual(stats['token_count'], 5)
        self.assertEqual(stats['type_count'], 5)
        self.assertAlmostEqual(stats['type_token_ratio'], 1.0, places=12)
        self.assertAlmostEqual(stats['avg_word_length'], 9 / 5, places=12)
        self.assertEqual(stats['longest_word'], 'the')
        # 'the' is the only stopword among the five tokens: 20 %.
        self.assertAlmostEqual(stats['stopword_coverage'], 20.0, places=12)
        # All counts equal 1; ASCII sorts before the CJK code points.
        self.assertEqual(stats['top_5_tokens'],
                         [['cat', 1], ['the', 1],
                          ['吃', 1], ['爱', 1], ['鱼', 1]])

    # ========== Empty / tokenless documents ==========

    def test_empty_and_whitespace_documents_null_metrics(self):
        """Tokenless documents get count 0 and null ratios/averages —
        never a division error."""
        for text in ('', '   \n\t  ', None):
            stats = self._profile_text(text)
            self.assertEqual(stats['token_count'], 0)
            self.assertEqual(stats['type_count'], 0)
            self.assertEqual(stats['hapax_count'], 0)
            self.assertIsNone(stats['type_token_ratio'])
            self.assertIsNone(stats['root_ttr'])
            self.assertIsNone(stats['hapax_ratio'])
            self.assertIsNone(stats['avg_word_length'])
            self.assertIsNone(stats['longest_word'])
            self.assertIsNone(stats['stopword_coverage'])
            self.assertEqual(stats['top_5_tokens'], [])

    def test_digits_and_punctuation_are_not_tokens(self):
        """Digits, punctuation and symbol runs never inflate counts."""
        stats = self._profile_text("12 + 34 = 46 ... !!! $%^ 3.14")
        self.assertEqual(stats['token_count'], 0)
        self.assertEqual(stats['type_count'], 0)
        self.assertIsNone(stats['type_token_ratio'])
        # Glued digits do not split a word: 'abc123' yields 'abc' once.
        stats = self._profile_text("abc123 45def")
        self.assertEqual(stats['token_count'], 2)
        self.assertEqual(stats['type_count'], 2)

    # ========== Stopword coverage ==========

    def test_stopword_coverage_arithmetic(self):
        """Coverage is the percentage of tokens in the built-in EN+ZH
        function-word lists."""
        self.assertEqual(self._profile_text("the of and")['stopword_coverage'],
                         100.0)
        self.assertEqual(
            self._profile_text("orchid daffodil chrysanthemum")
            ['stopword_coverage'], 0.0)
        # 4 hits over 9 tokens on the base corpus (the x3, on x1).
        self.assertAlmostEqual(
            self._profile_text(BASE_TEXT)['stopword_coverage'],
            4 / 9 * 100.0, places=12)

    # ========== Top-5 token list ==========

    def test_top5_ties_break_alphabetically(self):
        """Equal counts order alphabetically ascending; 'sat' loses the
        fifth slot to 'ran' on the base corpus."""
        stats = self._profile_text(BASE_TEXT)
        self.assertEqual(stats['top_5_tokens'],
                         [['the', 3], ['cat', 2],
                          ['mat', 1], ['on', 1], ['ran', 1]])
        self.assertNotIn(['sat', 1], stats['top_5_tokens'])

    def test_top5_truncated_to_five_entries(self):
        """At most five pairs are reported even with more types."""
        stats = self._profile_text("a b c d e f g")
        self.assertEqual(len(stats['top_5_tokens']), 5)
        # All count 1: the five alphabetically first tokens win.
        self.assertEqual(stats['top_5_tokens'],
                         [['a', 1], ['b', 1], ['c', 1],
                          ['d', 1], ['e', 1]])

    # ========== Metadata stamping behavior ==========

    def test_custom_metadata_keys_via_configer(self):
        """vocabulary_key / flag_key relocate (or namespace) both
        stamps."""
        configer = self._create_configer({
            'name': 'p', 'description': 'd',
            'vocabulary_key': 'vocab',
            'flag_key': 'monotony',
        })
        p = VocabularyCoverageProfiler()
        p._initialize_by_component_configer(configer)
        docs = p.process_docs([_doc(REPEAT_TEXT)], self.query)
        self.assertIn('vocab', docs[0].metadata)
        self.assertNotIn('vocabulary', docs[0].metadata)
        self.assertEqual(docs[0].metadata['monotony'], 'low_diversity')
        self.assertNotIn('vocabulary_flag', docs[0].metadata)

    def test_empty_vocabulary_key_disables_stats_but_not_flag(self):
        """vocabulary_key='' drops the statistics stamp; flagging is an
        independent option and still runs."""
        self.profiler.vocabulary_key = ''
        docs = self.profiler.process_docs([_doc(REPEAT_TEXT)], self.query)
        self.assertNotIn('vocabulary', docs[0].metadata)
        self.assertEqual(docs[0].metadata['vocabulary_flag'],
                         'low_diversity')

    def test_empty_flag_key_disables_flag_but_not_stats(self):
        """flag_key='' drops the flag; statistics still land."""
        self.profiler.flag_key = ''
        docs = self.profiler.process_docs([_doc(REPEAT_TEXT)], self.query)
        self.assertNotIn('vocabulary_flag', docs[0].metadata)
        self.assertEqual(docs[0].metadata['vocabulary']['token_count'], 8)

    def test_existing_metadata_preserved_and_mapping_copied(self):
        """Pre-existing metadata survives stamping and the original
        mapping object is never mutated in place."""
        original = {'source': 'wiki', 'lang': 'en'}
        doc = _doc(BASE_TEXT, **original)
        docs = self.profiler.process_docs([doc], self.query)
        self.assertEqual(docs[0].metadata['source'], 'wiki')
        self.assertEqual(docs[0].metadata['lang'], 'en')
        self.assertIn('vocabulary', docs[0].metadata)
        # The caller-held mapping was not mutated by the stamping.
        self.assertEqual(original, {'source': 'wiki', 'lang': 'en'})

    def test_text_and_id_untouched_and_order_preserved(self):
        """Documents map 1:1 onto the output: same objects, same order,
        byte-identical text."""
        texts = [BASE_TEXT, REPEAT_TEXT, CJK_TEXT, '']
        docs = [_doc(t) for t in texts]
        out = self.profiler.process_docs(docs, self.query)
        self.assertEqual(len(out), 4)
        for original, processed in zip(docs, out):
            self.assertIs(processed, original)
            self.assertEqual(processed.text, original.text)

    def test_empty_batch_returns_empty_list(self):
        """An empty batch yields an empty list."""
        self.assertEqual(self.profiler.process_docs([], self.query), [])

    def test_determinism_across_runs(self):
        """Same text produces identical statistics on every run and for
        every copy of the document in a batch."""
        first = self._profile_text(BASE_TEXT + " " + CJK_TEXT)
        second = self._profile_text(BASE_TEXT + " " + CJK_TEXT)
        self.assertEqual(first, second)
        doc_a, doc_b = _doc(REPEAT_TEXT), _doc(REPEAT_TEXT)
        docs = self.profiler.process_docs([doc_a, doc_b], self.query)
        self.assertEqual(docs[0].metadata['vocabulary'],
                         docs[1].metadata['vocabulary'])
        self.assertIn('vocabulary_flag', docs[0].metadata)
        self.assertIn('vocabulary_flag', docs[1].metadata)

    def test_metadata_is_json_serializable(self):
        """The stamped dict uses only JSON-native shapes, safe for
        metadata stores that serialize."""
        docs = self.profiler.process_docs(
            [_doc(BASE_TEXT + " " + CJK_TEXT)], self.query)
        payload = json.dumps(docs[0].metadata, ensure_ascii=False)
        self.assertIn('vocabulary', json.loads(payload))


if __name__ == '__main__':
    unittest.main()
