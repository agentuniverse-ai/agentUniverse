# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_stopword_remover.py

import re
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.stopword_remover import (
    StopwordRemover, _EN_STOPWORDS, _ZH_STOPWORDS, _is_cjk)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Mixed-language sentence used for combined-pass ground truths:
# EN word chunks: The, report, is, good (4) of which The/is are stopwords
# (2); ZH characters: 的 (1), itself a stopword (1) -> removed 3 / 5.
MIXED_TEXT = "The 的 report is good"


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestStopwordRemover(unittest.TestCase):
    """Comprehensive offline test suite for StopwordRemover."""

    def setUp(self):
        self.remover = StopwordRemover()
        self.query = Query(query_str="stopwords")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _process_one(self, text: str, **settings):
        """Run one document through a remover with optional overrides."""
        remover = StopwordRemover()
        for key, value in settings.items():
            setattr(remover, key, value)
        docs = remover.process_docs([_doc(text)], self.query)
        self.assertEqual(len(docs), 1)
        return docs[0]

    # ========== Built-in inventory tests ==========

    def test_builtin_lists_sizes_and_shape(self):
        """EN ships exactly 120 lowercase alphabetic function words, ZH
        exactly 81 single characters; the issue's seed words are present;
        the two inventories are disjoint."""
        self.assertEqual(len(_EN_STOPWORDS), 120)
        for word in _EN_STOPWORDS:
            self.assertRegex(word, r'^[a-z]+$')
        for seed in ('the', 'a', 'an', 'and', 'or', 'but', 'is', 'are',
                     'was', 'were', 'of', 'to', 'not'):
            self.assertIn(seed, _EN_STOPWORDS)

        self.assertEqual(len(_ZH_STOPWORDS), 81)
        for ch in _ZH_STOPWORDS:
            self.assertEqual(len(ch), 1)
            self.assertTrue(_is_cjk(ch))
        for seed in ('的', '了', '和', '是', '在', '不', '有', '我', '他', '这'):
            self.assertIn(seed, _ZH_STOPWORDS)

        self.assertFalse(_EN_STOPWORDS & _ZH_STOPWORDS)

    def test_is_cjk_boundaries(self):
        """The CJK gate accepts ideographs from Extension A, the main
        block and the compatibility block, and rejects neighbors."""
        self.assertTrue(_is_cjk('的'))          # main block U+4E00..
        self.assertTrue(_is_cjk('\u3400'))      # first char of Extension A
        self.assertTrue(_is_cjk('\uf900'))      # compatibility block
        self.assertFalse(_is_cjk('a'))
        self.assertFalse(_is_cjk('。'))          # CJK punctuation is not an ideograph
        self.assertFalse(_is_cjk('\u33ff'))     # just below Extension A
        self.assertFalse(_is_cjk('\ua000'))     # just above compatibility block

    # ========== Configuration tests ==========

    def test_default_configuration(self):
        """Defaults: both languages, no custom stopwords, builtins kept,
        remove mode."""
        r = StopwordRemover()
        self.assertEqual(r.languages, ['en', 'zh'])
        self.assertIsNone(r.custom_stopwords)
        self.assertFalse(r.replace_builtin)
        self.assertEqual(r.mode, 'remove')

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'stopword_remover',
            'description': 'stopword remover',
            'languages': ['en'],
            'custom_stopwords': ['alpha', 'beta'],
            'replace_builtin': False,
            'mode': 'tag',
        })
        r = StopwordRemover()
        r._initialize_by_component_configer(configer)
        self.assertEqual(r.languages, ['en'])
        self.assertEqual(r.custom_stopwords, ['alpha', 'beta'])
        self.assertFalse(r.replace_builtin)
        self.assertEqual(r.mode, 'tag')
        self.assertEqual(r.name, 'stopword_remover')

    def test_invalid_configuration_raises(self):
        """Unknown language codes, wrong container types, empty strings,
        bad modes and replace_builtin without custom words all fail at
        load time."""
        base = {
            'name': 'r', 'description': 'd',
            'languages': ['en', 'zh'],
            'custom_stopwords': ['ok'],
            'replace_builtin': False,
            'mode': 'remove',
        }
        for key, value in (
            ('languages', 'en'),
            ('languages', []),
            ('languages', ['fr']),
            ('languages', ['en', 3]),
            ('custom_stopwords', 'the'),
            ('custom_stopwords', ['the', '']),
            ('custom_stopwords', [1]),
            ('mode', 'delete'),
            ('mode', 7),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                StopwordRemover()._initialize_by_component_configer(
                    self._create_configer(config))

        # replace_builtin=true demands a non-empty custom list.
        no_custom = dict(base, replace_builtin=True)
        no_custom.pop('custom_stopwords')
        with self.assertRaises(ValueError):
            StopwordRemover()._initialize_by_component_configer(
                self._create_configer(no_custom))

    # ========== English pass ground truths ==========

    def test_en_stopwords_removed_and_content_preserved(self):
        """Every article/conjunction/preposition goes, every content word
        stays: 9 word chunks, 3 removed (The, over, the)."""
        doc = self._process_one("The quick brown fox jumps over the lazy dog")
        self.assertEqual(doc.text, "quick brown fox jumps lazy dog")
        self.assertEqual(doc.metadata['stopword_removed_count'], 3)
        self.assertAlmostEqual(doc.metadata['stopword_ratio'], 3 / 9)

    def test_punctuation_preserved_on_kept_words(self):
        """Punctuation glued to surviving words is kept and the single
        spaces around it are preserved byte-for-byte."""
        self.assertEqual(self._process_one("Hello, world!").text,
                         "Hello, world!")
        self.assertEqual(self._process_one('"quick" brown').text,
                         '"quick" brown')

    def test_punctuation_attached_to_removed_stopword_goes_with_it(self):
        """A word chunk carries its glued punctuation: the opening quote
        on '"The' and nothing survives 'is' either."""
        doc = self._process_one('"The report is ready."')
        self.assertEqual(doc.text, 'report ready."')
        self.assertEqual(doc.metadata['stopword_removed_count'], 2)

    def test_single_space_rejoin_normalizes_whitespace(self):
        """Tabs, newlines and repeated spaces between chunks collapse to
        exactly one space after stopword removal."""
        self.assertEqual(
            self._process_one("the  quick\tbrown\nfox").text,
            "quick brown fox")

    def test_contractions_kept_whole(self):
        """The tokenizer keeps 'don't' as one chunk; its core is not a
        stopword, so negation survives intact."""
        doc = self._process_one("don't stop believing")
        self.assertEqual(doc.text, "don't stop believing")
        self.assertEqual(doc.metadata['stopword_removed_count'], 0)
        self.assertEqual(doc.metadata['stopword_ratio'], 0.0)

    def test_hyphens_are_chunk_boundaries(self):
        """Intra-word hyphens split chunks, so 'of'/'the' inside
        'state-of-the-art' are removed as standalone stopwords."""
        doc = self._process_one("state-of-the-art")
        self.assertEqual(doc.text, "state- art")
        self.assertEqual(doc.metadata['stopword_removed_count'], 2)

    def test_case_insensitive_matching(self):
        """Uppercase stopwords are caught via lowercased cores."""
        doc = self._process_one("THE Model AND the Data")
        self.assertEqual(doc.text, "Model Data")
        self.assertEqual(doc.metadata['stopword_removed_count'], 3)

    # ========== Chinese pass ground truths ==========

    def test_zh_character_removal_ground_truths(self):
        """Char-level removal of particles: 我们的祖国 -> 祖国 (我/们/的
        are stopwords), 他是学生 -> 学生, 今天天气很好 -> 今天天气好."""
        self.assertEqual(self._process_one("我们的祖国").text, "祖国")
        self.assertEqual(self._process_one("他是学生").text, "学生")
        self.assertEqual(self._process_one("今天天气很好").text, "今天天气好")

    def test_zh_counts_and_ratio(self):
        """我们的祖国: 5 CJK chars considered, 3 removed -> ratio 0.6."""
        doc = self._process_one("我们的祖国")
        self.assertEqual(doc.metadata['stopword_removed_count'], 3)
        self.assertEqual(doc.metadata['stopword_ratio'], 0.6)

    def test_zh_pass_leaves_gap_whitespace_documented(self):
        """Only the characters are deleted: the space around a removed
        的 survives as an internal double space (nothing collapses)."""
        doc = self._process_one("C++ 和 Python", languages=['zh'])
        self.assertEqual(doc.text, "C++  Python")
        self.assertEqual(doc.metadata['stopword_removed_count'], 1)
        self.assertEqual(doc.metadata['stopword_ratio'], 1.0)

    # ========== Mixed-language ground truths ==========

    def test_mixed_language_document(self):
        """EN pass drops The/is and re-joins chunks with single spaces,
        ZH pass then deletes 的; leading whitespace is stripped: 3 of 5
        considered tokens removed."""
        doc = self._process_one(MIXED_TEXT)
        self.assertEqual(doc.text, "report good")
        self.assertEqual(doc.metadata['stopword_removed_count'], 3)
        self.assertEqual(doc.metadata['stopword_ratio'], 0.6)

    def test_en_pass_normalizes_newline_between_cjk_runs(self):
        """The re-join puts a single space between chunks, so a newline
        between two CJK runs becomes one space before the ZH pass runs."""
        doc = self._process_one("段落一\n了")
        self.assertEqual(doc.text, "段落一")
        self.assertEqual(doc.metadata['stopword_removed_count'], 1)

    def test_language_selection_gates_script_passes(self):
        """'en' alone never touches CJK stopword characters; 'zh' alone
        never touches Latin stopwords — each yields ratio 0."""
        doc = self._process_one("的", languages=['en'])
        self.assertEqual(doc.text, "的")
        self.assertEqual(doc.metadata['stopword_removed_count'], 0)
        self.assertEqual(doc.metadata['stopword_ratio'], 0.0)

        doc = self._process_one("the cat", languages=['zh'])
        self.assertEqual(doc.text, "the cat")
        self.assertEqual(doc.metadata['stopword_removed_count'], 0)

    # ========== Ratio arithmetic ==========

    def test_ratio_arithmetic_hand_verified(self):
        """removed / considered over the original text, per enabled
        languages only: 3/5, 1/5, 2/4 and 0 for nothing considered."""
        doc = self._process_one("the cat and the dog")
        self.assertEqual(doc.metadata['stopword_removed_count'], 3)
        self.assertEqual(doc.metadata['stopword_ratio'], 0.6)

        doc = self._process_one("a b c d e")
        self.assertEqual(doc.metadata['stopword_removed_count'], 1)
        self.assertEqual(doc.metadata['stopword_ratio'], 0.2)

        doc = self._process_one("他很重要", languages=['zh'])
        self.assertEqual(doc.metadata['stopword_removed_count'], 2)
        self.assertEqual(doc.metadata['stopword_ratio'], 0.5)

        doc = self._process_one("!!! ???")
        self.assertEqual(doc.metadata['stopword_removed_count'], 0)
        self.assertEqual(doc.metadata['stopword_ratio'], 0.0)

    # ========== Tag mode ==========

    def test_tag_mode_leaves_text_byte_identical(self):
        """mode='tag' stamps both statistics but never touches the text,
        including its original whitespace."""
        doc = self._process_one(MIXED_TEXT + "  ", mode='tag')
        self.assertEqual(doc.text, MIXED_TEXT + "  ")
        self.assertEqual(doc.metadata['stopword_removed_count'], 3)
        self.assertEqual(doc.metadata['stopword_ratio'], 0.6)

    def test_tag_mode_counts_only_enabled_languages(self):
        """Tagging with languages=['en'] ignores CJK characters entirely:
        2 of 4 considered, ratio 0.5, 的 neither counted nor removed."""
        doc = self._process_one(MIXED_TEXT, languages=['en'], mode='tag')
        self.assertEqual(doc.text, MIXED_TEXT)
        self.assertEqual(doc.metadata['stopword_removed_count'], 2)
        self.assertEqual(doc.metadata['stopword_ratio'], 0.5)

    # ========== Custom stopword configuration ==========

    def test_custom_stopwords_extend_builtins(self):
        """custom=['zebra'] adds to the English built-ins: both 'the' and
        'zebra' disappear, 2 of 3 word chunks removed."""
        doc = self._process_one("the zebra runs",
                                languages=['en'],
                                custom_stopwords=['zebra'])
        self.assertEqual(doc.text, "runs")
        self.assertEqual(doc.metadata['stopword_removed_count'], 2)

    def test_replace_builtin_swaps_the_whole_set(self):
        """replace_builtin=True: only 'zebra' is a stopword now, so 'the'
        survives while 'zebra' is dropped (1 of 3 removed)."""
        doc = self._process_one("the zebra runs",
                                languages=['en'],
                                custom_stopwords=['zebra'],
                                replace_builtin=True)
        self.assertEqual(doc.text, "the runs")
        self.assertEqual(doc.metadata['stopword_removed_count'], 1)

    def test_custom_zh_stopword_character(self):
        """A single CJK custom entry joins the zh pass: 我们的祖国 plus
        祖 leaves only 国 (4 of 5 removed)."""
        doc = self._process_one("我们的祖国",
                                languages=['zh'],
                                custom_stopwords=['祖'])
        self.assertEqual(doc.text, "国")
        self.assertEqual(doc.metadata['stopword_removed_count'], 4)

    # ========== Degenerate inputs ==========

    def test_empty_and_whitespace_documents(self):
        """Empty list in gives empty list out; '', None and blank text
        yield empty text with count 0 and ratio 0.0 (never a ZeroDivision
        error), and the documents themselves are kept."""
        self.assertEqual(self.remover.process_docs([], self.query), [])

        for text in ('', '   '):
            doc = self._process_one(text)
            self.assertEqual(doc.text, '')
            self.assertEqual(doc.metadata['stopword_removed_count'], 0)
            self.assertEqual(doc.metadata['stopword_ratio'], 0.0)

        # None text (only constructible alongside an explicit id) is
        # tolerated the same way.
        doc = self.remover.process_docs(
            [Document(id='none-text', text=None)], self.query)[0]
        self.assertEqual(doc.text, '')
        self.assertEqual(doc.metadata['stopword_removed_count'], 0)
        self.assertEqual(doc.metadata['stopword_ratio'], 0.0)

    def test_stopword_only_document_empties_text(self):
        """An all-stopword document is kept with empty text and ratio
        1.0 — dropping it is left to a downstream filter."""
        doc = self._process_one("THE AND OR BUT")
        self.assertEqual(doc.text, '')
        self.assertEqual(doc.metadata['stopword_removed_count'], 4)
        self.assertEqual(doc.metadata['stopword_ratio'], 1.0)

    def test_punctuation_only_document_untouched(self):
        """No word chunks and no CJK characters: nothing considered, text
        passes through unchanged (chunks re-joined with single spaces)."""
        doc = self._process_one("!!! ???")
        self.assertEqual(doc.text, "!!! ???")

    # ========== Pipeline-shape and metadata tests ==========

    def test_documents_kept_in_order_one_to_one(self):
        """Every input document survives exactly once, in order, with its
        id and other metadata intact."""
        docs = [_doc("the alpha", source="a"),
                _doc("我们的祖国", source="b"),
                _doc("kept fully intact xyz")]
        result = self.remover.process_docs(docs, self.query)
        self.assertEqual([d.id for d in result], [d.id for d in docs])
        self.assertEqual([d.text for d in result],
                         ["alpha", "祖国", "kept fully intact xyz"])
        self.assertEqual([d.metadata.get('source') for d in result],
                         ['a', 'b', None])

    def test_metadata_stamped_through_a_copy(self):
        """Pre-existing metadata survives stamping, and the original
        mapping object is not mutated in place."""
        doc = _doc("the cat", source="wire", rank=1)
        meta_ref = doc.metadata
        result = self.remover.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata['source'], 'wire')
        self.assertEqual(result[0].metadata['rank'], 1)
        self.assertEqual(result[0].metadata['stopword_removed_count'], 1)
        self.assertEqual(result[0].metadata['stopword_ratio'], 0.5)
        self.assertNotIn('stopword_removed_count', meta_ref)
        self.assertIsNot(doc.metadata, meta_ref)

    def test_deterministic_and_repeatable(self):
        """Two instances and repeated runs produce identical text and
        statistics; set-based internals never leak into the output."""
        first = self._process_one(MIXED_TEXT)
        second = self._process_one(MIXED_TEXT)
        self.assertEqual(first.text, second.text)
        self.assertEqual(first.metadata, second.metadata)

        docs = [_doc(MIXED_TEXT)]
        self.remover.process_docs(docs, self.query)
        again = self.remover.process_docs([_doc(MIXED_TEXT)], self.query)
        self.assertEqual(docs[0].text, again[0].text)
        self.assertEqual(docs[0].metadata, again[0].metadata)

    def test_chunk_regex_has_no_zero_width_matches(self):
        """Every chunk match is non-empty and every non-whitespace
        character of the text is covered by exactly one match."""
        from agentuniverse.agent.action.knowledge.doc_processor. \
            stopword_remover import _CHUNK_RE
        text = MIXED_TEXT + ' "The state-of-the-art, don\'t! 123 ok"'
        non_whitespace = [w for w in re.split(r'\s+', text) if w]
        matches = [m.group(0) for m in _CHUNK_RE.finditer(text)]
        self.assertTrue(matches)
        for chunk in matches:
            self.assertTrue(chunk)
            self.assertNotIn(' ', chunk)
            self.assertNotIn('\t', chunk)
        # Concatenating all matches after dropping whitespace reproduces
        # the concatenation of whitespace-separated words.
        self.assertEqual(''.join(matches), ''.join(non_whitespace))


if __name__ == '__main__':
    unittest.main()
