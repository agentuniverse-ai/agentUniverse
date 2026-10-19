# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_keyword_in_context_concentrator.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.keyword_in_context_concentrator import \
    KeywordInContextConcentrator
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# A 87-character news-like sentence hosting "rate" twice (word-bounded)
# and "rates" once (which must NOT match the keyword "rate").
BASE_TEXT = (
    "The interest rate hike surprised markets. Another rate decision "
    "is due next month; rates remain elevated."
)

# Chinese sentence hosting 利率 twice, always glued to other CJK
# characters — only substring matching (no word boundaries) finds them.
ZH_TEXT = "央行上调利率以抑制通胀，市场对利率决议保持谨慎。"

# The full concordance record pinned end-to-end for regression
# stability: keywords ['rate', 'decision'], window 8, defaults
# elsewhere. Offsets index into BASE_TEXT as concatenated above.
PINNED_RECORD = {
    'keywords': ['rate', 'decision'],
    'total_occurrences': 3,
    'counts': {'rate': 2, 'decision': 1},
    'snippets': [
        {'keyword': 'rate', 'start': 13, 'end': 17,
         'context': '…nterest rate hike su…'},
        {'keyword': 'rate', 'start': 50, 'end': 54,
         'context': '…Another rate decisio…'},
        {'keyword': 'decision', 'start': 55, 'end': 63,
         'context': '…er rate decision is due…'},
    ],
}


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestKeywordInContextConcentrator(unittest.TestCase):
    """Comprehensive test suite for KeywordInContextConcentrator."""

    def setUp(self):
        self.processor = KeywordInContextConcentrator()
        self.query = Query(query_str="rate decision")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: no static keywords, query keywords on, window 60,
        10 snippets, stamp-only, case-insensitive, 'kwic' metadata key."""
        p = KeywordInContextConcentrator()
        self.assertEqual(p.keywords, [])
        self.assertTrue(p.use_query_keywords)
        self.assertEqual(p.window_size, 60)
        self.assertEqual(p.max_snippets, 10)
        self.assertEqual(p.min_occurrences, 0)
        self.assertFalse(p.case_sensitive)
        self.assertEqual(p.kwic_key, "kwic")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'keyword_in_context_concentrator',
            'description': 'kwic concentrator',
            'keywords': ['rate', 'inflation'],
            'use_query_keywords': False,
            'window_size': 25,
            'max_snippets': 3,
            'min_occurrences': 2,
            'case_sensitive': True,
            'kwic_key': 'snippets',
        })
        p = KeywordInContextConcentrator()
        p._initialize_by_component_configer(configer)
        self.assertEqual(p.keywords, ['rate', 'inflation'])
        self.assertFalse(p.use_query_keywords)
        self.assertEqual(p.window_size, 25)
        self.assertEqual(p.max_snippets, 3)
        self.assertEqual(p.min_occurrences, 2)
        self.assertTrue(p.case_sensitive)
        self.assertEqual(p.kwic_key, 'snippets')
        self.assertEqual(p.name, 'keyword_in_context_concentrator')

    def test_invalid_configuration_raises(self):
        """Negative / fractional / boolean numerics, malformed keyword
        lists and non-string metadata keys all fail at load time."""
        base = {
            'name': 'p', 'description': 'd',
            'keywords': ['rate'], 'use_query_keywords': True,
            'window_size': 60, 'max_snippets': 10,
            'min_occurrences': 0, 'case_sensitive': False,
            'kwic_key': 'kwic',
        }
        for key, value in (
            ('window_size', -1),
            ('window_size', 2.5),
            ('window_size', True),
            ('max_snippets', 0),
            ('max_snippets', -3),
            ('max_snippets', 1.5),
            ('max_snippets', True),
            ('min_occurrences', -1),
            ('min_occurrences', 2.5),
            ('min_occurrences', True),
            ('keywords', 'rate'),
            ('keywords', 7),
            ('keywords', ['rate', 5]),
            ('keywords', ['rate', '']),
            ('keywords', ['rate', '   ']),
            ('kwic_key', 5),
            ('kwic_key', ['x']),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                KeywordInContextConcentrator()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Pattern matching tests ==========

    def test_word_boundary_prevents_substring_hits(self):
        """ASCII keywords only match whole words: 'cat' skips 'category',
        'categorical' and 'concatenate' but hits the standalone 'cat'."""
        text = "the category field is categorical; concatenate with cat"
        hits = self.processor._find_occurrences(text, ['cat'])
        self.assertEqual(hits, [(52, 55, 0)])
        self.assertEqual(text[52:55], 'cat')

    def test_underscore_edge_is_word_boundary(self):
        """Underscore counts as a word character, so 'cat' does not fire
        inside 'cat_dog'."""
        self.assertEqual(
            self.processor._find_occurrences("a cat_dog toy", ['cat']), [])

    def test_rates_does_not_match_rate(self):
        """The plural 'rates' in BASE_TEXT is skipped: exactly two
        word-bounded 'rate' occurrences at the pinned offsets."""
        self.assertEqual(
            self.processor._find_occurrences(BASE_TEXT, ['rate']),
            [(13, 17, 0), (50, 54, 0)])

    def test_case_insensitive_default_and_case_sensitive_option(self):
        """Case-insensitive by default ('Rate' and 'rate' both match,
        'RATES' still excluded by the word boundary); case_sensitive=True
        narrows matching to exact-case occurrences."""
        text = "Rate limits and RATES policy and rate cuts"
        self.assertEqual(
            self.processor._find_occurrences(text, ['rate']),
            [(0, 4, 0), (33, 37, 0)])

        self.processor.case_sensitive = True
        self.assertEqual(
            self.processor._find_occurrences(text, ['rate']), [(33, 37, 0)])

    def test_cjk_keywords_match_without_boundaries(self):
        """CJK edges get no word-boundary requirement — 利率 is found
        inside 利率风险 and inside running Chinese text at the pinned
        offsets."""
        self.assertEqual(
            self.processor._find_occurrences(ZH_TEXT, ['利率']),
            [(4, 6, 0), (15, 17, 0)])
        self.assertEqual(
            len(self.processor._find_occurrences("利率风险上升", ['利率'])), 1)

    def test_overlapping_distinct_keywords_both_reported(self):
        """'rate' and 'interest rate' cover the same span; each keyword
        reports its own occurrence, ordered by start offset."""
        text = "the interest rate decision"
        self.processor.keywords = ['rate', 'interest rate']
        result = self.processor.process_docs([_doc(text)], None)
        record = result[0].metadata['kwic']
        self.assertEqual(record['counts'],
                         {'rate': 1, 'interest rate': 1})
        self.assertEqual([(s['keyword'], s['start'], s['end'])
                          for s in record['snippets']],
                         [('interest rate', 4, 17), ('rate', 13, 17)])

    def test_same_keyword_non_overlapping_regex_semantics(self):
        """Overlapping occurrences of one boundary-free keyword follow
        regex non-overlapping semantics: '啊啊啊' yields one hit for
        '啊啊' (not two); an ASCII 'aa' in 'aaa' cannot match at all
        because no whole-word span exists."""
        self.assertEqual(
            self.processor._find_occurrences("啊啊啊", ['啊啊']), [(0, 2, 0)])
        self.assertEqual(
            self.processor._find_occurrences("aaa", ['aa']), [])

    # ========== Snippet extraction tests ==========

    def test_full_record_pinned(self):
        """End-to-end record equals the pinned literal exactly: keyword
        list, total, per-keyword counts (zero-count keywords included)
        and text-ordered snippets with offsets and contexts."""
        self.processor.keywords = ['rate', 'decision']
        self.processor.window_size = 8
        result = self.processor.process_docs([_doc(BASE_TEXT)], None)
        self.assertEqual(result[0].metadata['kwic'], PINNED_RECORD)

    def test_snippet_window_clamped_at_text_edges(self):
        """A keyword at offset 0 gets no leading ellipsis; the window is
        clamped to the document on both sides."""
        self.processor.keywords = ['rate']
        self.processor.window_size = 4
        result = self.processor.process_docs(
            [_doc("rate rise is coming fast")], None)
        snippets = result[0].metadata['kwic']['snippets']
        self.assertEqual(len(snippets), 1)
        self.assertEqual(snippets[0]['start'], 0)
        self.assertEqual(snippets[0]['end'], 4)
        self.assertEqual(snippets[0]['context'], 'rate ris…')
        self.assertFalse(snippets[0]['context'].startswith('…'))

    def test_ellipsis_marks_clipped_windows_only(self):
        """… appears exactly on the sides where window_size cut the
        text; a full-document window carries no markers."""
        self.processor.keywords = ['mid']
        self.processor.window_size = 1
        result = self.processor.process_docs([_doc("aa mid bb")], None)
        context = result[0].metadata['kwic']['snippets'][0]['context']
        self.assertEqual(context, '…mid…')

        self.processor.window_size = 100
        result = self.processor.process_docs([_doc("aa mid bb")], None)
        context = result[0].metadata['kwic']['snippets'][0]['context']
        self.assertEqual(context, 'aa mid bb')

    def test_zero_window_reduces_to_keyword(self):
        """window_size=0 narrows every snippet to the keyword itself,
        still carrying … markers wherever text continues beyond the
        keyword (both snippets here are interior)."""
        self.processor.keywords = ['rate']
        self.processor.window_size = 0
        result = self.processor.process_docs([_doc(BASE_TEXT)], None)
        self.assertEqual(
            [s['context'] for s in result[0].metadata['kwic']['snippets']],
            ['…rate…', '…rate…'])

    def test_whitespace_collapsed_in_context(self):
        """Newlines and tabs inside a window collapse to single spaces
        with edge whitespace stripped, keeping each snippet one line."""
        text = "line one has\n\nrate here\nand\ttabbed rate too"
        self.processor.keywords = ['rate']
        self.processor.window_size = 5
        result = self.processor.process_docs([_doc(text)], None)
        snippets = result[0].metadata['kwic']['snippets']
        self.assertEqual(snippets, [
            {'keyword': 'rate', 'start': 14, 'end': 18,
             'context': '…has rate here…'},
            {'keyword': 'rate', 'start': 35, 'end': 39,
             'context': '…bbed rate too'},
        ])

    def test_cjk_snippets_pinned(self):
        """Chinese snippets keep CJK text intact with ellipsis markers at
        the clipped edges (offsets pinned against ZH_TEXT)."""
        self.processor.keywords = ['利率']
        self.processor.window_size = 6
        result = self.processor.process_docs([_doc(ZH_TEXT)], None)
        self.assertEqual(result[0].metadata['kwic']['snippets'], [
            {'keyword': '利率', 'start': 4, 'end': 6,
             'context': '央行上调利率以抑制通胀，…'},
            {'keyword': '利率', 'start': 15, 'end': 17,
             'context': '…通胀，市场对利率决议保持谨慎…'},
        ])

    # ========== Capping and counting tests ==========

    def test_snippets_capped_but_counts_total_all(self):
        """15 occurrences produce 10 stored snippets (default cap) while
        total_occurrences and counts report all 15."""
        text = "rate " * 15
        self.processor.keywords = ['rate']
        result = self.processor.process_docs([_doc(text)], None)
        record = result[0].metadata['kwic']
        self.assertEqual(record['total_occurrences'], 15)
        self.assertEqual(record['counts'], {'rate': 15})
        self.assertEqual(len(record['snippets']), 10)

    def test_snippets_ordered_by_position(self):
        """Snippets come back in text order regardless of keyword list
        order."""
        self.processor.keywords = ['decision', 'rate']
        result = self.processor.process_docs([_doc(BASE_TEXT)], None)
        starts = [s['start'] for s in result[0].metadata['kwic']['snippets']]
        self.assertEqual(starts, sorted(starts))
        self.assertEqual(starts, [13, 50, 55])

    def test_counts_include_zero_hit_keywords(self):
        """A configured keyword with no occurrences still appears in
        counts (and in keywords) with value 0."""
        self.processor.keywords = ['rate', 'quantum']
        result = self.processor.process_docs([_doc(BASE_TEXT)], None)
        record = result[0].metadata['kwic']
        self.assertEqual(record['counts'], {'rate': 2, 'quantum': 0})
        self.assertEqual(record['keywords'], ['rate', 'quantum'])
        self.assertEqual(record['total_occurrences'], 2)

    # ========== Query keyword tests ==========

    def test_query_keywords_merged_after_static(self):
        """Query keywords join the effective list after the static ones,
        alphabetically sorted (set iteration order never leaks in)."""
        self.processor.keywords = ['inflation', 'rate']
        effective = self.processor._effective_keywords(
            Query(keywords={'zeta', 'alpha', 'rate'}))
        self.assertEqual(effective, ['inflation', 'rate', 'alpha', 'zeta'])

    def test_use_query_keywords_disabled(self):
        """use_query_keywords=False keeps the effective list to the
        static keywords even when the query carries keywords."""
        self.processor.keywords = ['rate']
        self.processor.use_query_keywords = False
        effective = self.processor._effective_keywords(
            Query(keywords={'inflation'}))
        self.assertEqual(effective, ['rate'])
        result = self.processor.process_docs(
            [_doc(BASE_TEXT)], Query(keywords={'inflation'}))
        self.assertEqual(result[0].metadata['kwic']['keywords'], ['rate'])

    def test_query_keywords_drive_matching(self):
        """With no static keywords, the query's keyword set alone drives
        snippet extraction (recall-time usage)."""
        result = self.processor.process_docs(
            [_doc(BASE_TEXT)], Query(keywords={'decision'}))
        record = result[0].metadata['kwic']
        self.assertEqual(record['keywords'], ['decision'])
        self.assertEqual(record['total_occurrences'], 1)
        self.assertEqual(record['snippets'][0]['keyword'], 'decision')

    def test_no_keywords_at_all_stamps_empty_record(self):
        """No static keywords and no query keywords: an empty record is
        stamped and the document is kept (stamp-only default)."""
        result = self.processor.process_docs([_doc(BASE_TEXT)], None)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata['kwic'], {
            'keywords': [],
            'total_occurrences': 0,
            'counts': {},
            'snippets': [],
        })

    # ========== Filtering tests ==========

    def test_default_min_occurrences_keeps_everything(self):
        """min_occurrences=0 is stamp-only: documents without any
        keyword hit survive untouched otherwise."""
        docs = [_doc(BASE_TEXT), _doc("no relevant terms here")]
        result = self.processor.process_docs(
            docs, Query(keywords={'rate'}))
        self.assertEqual([d.text for d in result],
                         [d.text for d in docs])

    def test_min_occurrences_drops_sparse_documents(self):
        """min_occurrences=2 keeps the document with two 'rate' hits and
        drops the one-off 'decision' document."""
        self.processor.keywords = ['rate']
        self.processor.min_occurrences = 2
        docs = [_doc(BASE_TEXT), _doc("a decision is pending")]
        result = self.processor.process_docs(docs, None)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, BASE_TEXT)
        # the dropped document was never stamped
        self.assertNotIn('kwic', docs[1].metadata or {})

    # ========== Metadata bookkeeping tests ==========

    def test_input_documents_not_corrupted(self):
        """Text and id are untouched; pre-existing metadata entries
        survive; and stamping writes through a copy rather than mutating
        the original mapping."""
        doc = _doc(BASE_TEXT, source="wire", rank=1)
        meta_ref = doc.metadata
        self.processor.keywords = ['rate']

        result = self.processor.process_docs([doc], None)

        self.assertIs(result[0], doc)
        self.assertEqual(result[0].text, BASE_TEXT)
        self.assertEqual(result[0].id, doc.id)
        self.assertEqual(doc.metadata['source'], 'wire')
        self.assertEqual(doc.metadata['rank'], 1)
        # Stamp went through a copied mapping: the caller's original dict
        # object did not gain the new key in place.
        self.assertNotIn('kwic', meta_ref)
        self.assertIsNot(doc.metadata, meta_ref)

    def test_disabled_and_custom_metadata_keys(self):
        """kwic_key='' disables stamping entirely; a custom key lands the
        record under that name instead."""
        self.processor.keywords = ['rate']
        self.processor.kwic_key = ''
        doc = _doc(BASE_TEXT, source="wire")
        result = self.processor.process_docs([doc], None)
        self.assertEqual(len(result), 1)
        self.assertEqual(doc.metadata, {'source': 'wire'})

        self.processor.kwic_key = 'snippets'
        result = self.processor.process_docs([_doc(BASE_TEXT)], None)
        self.assertNotIn('kwic', result[0].metadata)
        self.assertIn('snippets', result[0].metadata)

    # ========== Pipeline-shape tests ==========

    def test_empty_batch_returns_empty(self):
        """An empty input batch yields an empty output list."""
        self.assertEqual(self.processor.process_docs([], self.query), [])

    def test_blank_and_none_text_tolerated(self):
        """Blank texts are stamped with an empty record; a None text
        document (constructed with an explicit id) survives too."""
        docs = [_doc("", tag='blank'), Document(id='none-doc', text=None)]
        self.processor.keywords = ['rate']
        result = self.processor.process_docs(docs, None)
        self.assertEqual(len(result), 2)
        for doc in result:
            self.assertEqual(doc.metadata['kwic']['total_occurrences'], 0)
            self.assertEqual(doc.metadata['kwic']['snippets'], [])

    def test_order_preserved_for_multiple_documents(self):
        """Kept documents keep batch order; each is stamped with its own
        record."""
        self.processor.keywords = ['rate']
        docs = [_doc("nothing to see"),
                _doc(BASE_TEXT),
                _doc("rate of return matters")]
        result = self.processor.process_docs(docs, None)
        self.assertEqual([d.text for d in result],
                         ["nothing to see", BASE_TEXT,
                          "rate of return matters"])
        self.assertEqual(result[0].metadata['kwic']['total_occurrences'], 0)
        self.assertEqual(result[1].metadata['kwic']['total_occurrences'], 2)
        self.assertEqual(result[2].metadata['kwic']['total_occurrences'], 1)

    def test_deterministic_across_instances(self):
        """Two fresh instances with identical configuration produce
        byte-identical records (query set ordering included)."""
        records = []
        for _ in range(2):
            processor = KeywordInContextConcentrator()
            processor.keywords = ['rate', 'decision']
            processor.window_size = 8
            result = processor.process_docs(
                [_doc(BASE_TEXT)], Query(keywords={'markets', 'rate'}))
            records.append(result[0].metadata['kwic'])
        self.assertEqual(records[0], records[1])
        # Query keywords are merged deterministically (sorted) and the
        # static dedup keeps a single 'rate'; the query keyword
        # 'markets' adds its own word-bounded occurrence.
        self.assertEqual(records[0]['keywords'],
                         ['rate', 'decision', 'markets'])
        self.assertEqual(records[0]['counts'],
                         {'rate': 2, 'decision': 1, 'markets': 1})
        self.assertEqual(records[0]['total_occurrences'], 4)
        self.assertEqual(len(records[0]['snippets']), 4)


if __name__ == '__main__':
    unittest.main()
