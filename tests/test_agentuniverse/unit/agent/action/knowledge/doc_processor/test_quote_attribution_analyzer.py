# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_quote_attribution_analyzer.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.quote_attribution_analyzer import QuoteAttributionAnalyzer
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestQuoteAttributionAnalyzer(unittest.TestCase):
    """Comprehensive offline test suite for QuoteAttributionAnalyzer."""

    def setUp(self):
        self.analyzer = QuoteAttributionAnalyzer()
        self.query = Query(query_str="who said what")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _analyze(self, text):
        """Run the analyzer over one document and return its metadata."""
        doc = _doc(text)
        result = self.analyzer.process_docs([doc], self.query)
        self.assertIs(result[0], doc)
        return doc.metadata

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: cap 50, lookback 2, 'quotes'/'quote_count'/'speakers'
        metadata keys."""
        a = QuoteAttributionAnalyzer()
        self.assertEqual(a.max_quotes, 50)
        self.assertEqual(a.speaker_lookback, 2)
        self.assertEqual(a.quotes_key, "quotes")
        self.assertEqual(a.count_key, "quote_count")
        self.assertEqual(a.speakers_key, "speakers")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'quote_attribution_analyzer',
            'description': 'quote attribution analyzer',
            'max_quotes': 10,
            'speaker_lookback': 4,
            'quotes_key': 'citations',
            'count_key': 'citations_total',
            'speakers_key': 'voices',
        })
        a = QuoteAttributionAnalyzer()
        a._initialize_by_component_configer(configer)
        self.assertEqual(a.max_quotes, 10)
        self.assertEqual(a.speaker_lookback, 4)
        self.assertEqual(a.quotes_key, 'citations')
        self.assertEqual(a.count_key, 'citations_total')
        self.assertEqual(a.speakers_key, 'voices')
        self.assertEqual(a.name, 'quote_attribution_analyzer')

    def test_invalid_configuration_raises(self):
        """Non-positive/odd-typed caps and lookbacks, and non-string
        metadata keys, all fail at load time."""
        base = {
            'name': 'a', 'description': 'd',
            'max_quotes': 50, 'speaker_lookback': 2,
            'quotes_key': 'quotes', 'count_key': 'quote_count',
            'speakers_key': 'speakers',
        }
        for key, value in (
            ('max_quotes', 0),
            ('max_quotes', -3),
            ('max_quotes', 2.5),
            ('max_quotes', True),
            ('speaker_lookback', 0),
            ('speaker_lookback', 1.5),
            ('speaker_lookback', False),
            ('quotes_key', 5),
            ('count_key', ['x']),
            ('speakers_key', 3.0),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                QuoteAttributionAnalyzer()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== English attribution tests ==========

    def test_pre_position_attribution(self):
        """`Alice Chen said, "..."` — the name run before the verb is the
        speaker; the quote keeps its markers; the span reproduces it."""
        meta = self._analyze(
            'Alice Chen said, "We will not rest until every customer '
            'is refunded."')
        self.assertEqual(meta['quote_count'], 1)
        hit = meta['quotes'][0]
        self.assertEqual(hit['speaker'], 'Alice Chen')
        self.assertEqual(hit['speaker_resolved'], 'name')
        self.assertEqual(hit['attribution_text'], 'Alice Chen said')
        self.assertEqual(hit['quote'],
                         '"We will not rest until every customer '
                         'is refunded."')
        start, end = hit['span']
        text = 'Alice Chen said, "We will not rest until every customer ' \
               'is refunded."'
        self.assertEqual(text[start:end], hit['quote'])

    def test_post_position_attribution(self):
        """`"..." said Alice Chen.` — the journalistic post-position
        resolves the speaker after the verb."""
        meta = self._analyze(
            '"We will not rest until every customer is refunded," '
            'said Alice Chen.')
        hit = meta['quotes'][0]
        self.assertEqual(hit['speaker'], 'Alice Chen')
        self.assertEqual(hit['speaker_resolved'], 'name')
        self.assertEqual(hit['attribution_text'], 'said Alice Chen')

    def test_according_to_attribution(self):
        """`According to NAME, "..."` — the introductory phrase is
        recognized as an attribution."""
        meta = self._analyze(
            'According to Bob Martinez, "It never closed."')
        hit = meta['quotes'][0]
        self.assertEqual(hit['speaker'], 'Bob Martinez')
        self.assertEqual(hit['speaker_resolved'], 'name')
        self.assertEqual(hit['attribution_text'],
                         'According to Bob Martinez')

    def test_verb_variants(self):
        """All documented English verbs resolve their preceding name."""
        verbs = ('said', 'says', 'told', 'added', 'noted', 'claimed',
                 'stated')
        for verb in verbs:
            meta = self._analyze(f'Ann Cole {verb} reporters, '
                                 f'"The numbers hold up."')
            hit = meta['quotes'][0]
            self.assertEqual(hit['speaker'], 'Ann Cole', verb)
            self.assertEqual(hit['speaker_resolved'], 'name', verb)
            self.assertEqual(hit['attribution_text'],
                             f'Ann Cole {verb}', verb)

    def test_name_with_appositive_between_name_and_verb(self):
        """`Alice Weber, the finance director, said "..."` — the comma
        appositive is skipped; the name (not the role) is the speaker."""
        meta = self._analyze(
            'Alice Weber, the finance director, said '
            '"We simply cannot absorb these costs."')
        hit = meta['quotes'][0]
        self.assertEqual(hit['speaker'], 'Alice Weber')
        self.assertEqual(hit['speaker_resolved'], 'name')
        self.assertIn('said', hit['attribution_text'])

    def test_titles_preserved_in_name(self):
        """Dr./Mr./President stay part of the matched name; the
        abbreviation period does not split the sentence."""
        for prefix, last in (('Dr.', 'Maya Patel'), ('Mr.', 'Chen'),
                             ('President', 'Liu')):
            meta = self._analyze(
                f'{prefix} {last} told reporters, "The trial is on track."')
            hit = meta['quotes'][0]
            self.assertEqual(hit['speaker'], f'{prefix} {last}')
            self.assertEqual(hit['speaker_resolved'], 'name')

    def test_next_sentence_attribution_for_terminal_quote(self):
        """A sentence-terminal quote whose speaker opens the NEXT
        sentence: `"..." Alice Weber said in a note.`"""
        meta = self._analyze(
            'The board met for six hours on Tuesday. '
            '"We simply cannot absorb these costs." '
            'Alice Weber said in a follow-up note.')
        self.assertEqual(meta['quote_count'], 1)
        hit = meta['quotes'][0]
        self.assertEqual(hit['speaker'], 'Alice Weber')
        self.assertEqual(hit['speaker_resolved'], 'name')
        self.assertEqual(hit['attribution_text'], 'Alice Weber said')

    # ========== Quote style tests ==========

    def test_all_four_quote_styles(self):
        """ASCII doubles, curly doubles, CJK corner brackets and German
        low-high marks all yield quote records with markers included."""
        meta = self._analyze(
            'Ann Lee said, "Plain double quotes work." '
            'Bo Ma noted, “Curly double quotes work.” '
            'Cyr Nao claimed, 「Corner brackets work。」 '
            'Di Oak stated, „German quotes work.“')
        self.assertEqual(meta['quote_count'], 4)
        quotes = [hit['quote'] for hit in meta['quotes']]
        self.assertEqual(quotes, [
            '"Plain double quotes work."',
            '“Curly double quotes work.”',
            '「Corner brackets work。」',
            '„German quotes work.“',
        ])
        speakers = [hit['speaker'] for hit in meta['quotes']]
        self.assertEqual(speakers,
                         ['Ann Lee', 'Bo Ma', 'Cyr Nao', 'Di Oak'])

    def test_unpaired_and_newline_quotes_ignored(self):
        """Unpaired markers and quotes spanning a newline never produce
        records."""
        meta = self._analyze(
            'A lone " mark sits here.\n'
            'Nobody said anything "important\nacross lines" at all.')
        self.assertEqual(meta['quote_count'], 0)
        self.assertEqual(meta['quotes'], [])
        self.assertEqual(meta['speakers'], {})

    # ========== Chinese attribution tests ==========

    def test_zh_verb_attribution(self):
        """`李娜表示："..."` — the hanzi run before 表示 is the speaker."""
        meta = self._analyze('李娜表示：“价格已经稳定。”')
        hit = meta['quotes'][0]
        self.assertEqual(hit['quote'], '“价格已经稳定。”')
        self.assertEqual(hit['speaker'], '李娜')
        self.assertEqual(hit['speaker_resolved'], 'name')
        self.assertEqual(hit['attribution_text'], '李娜表示')

    def test_zh_verb_variants_and_corner_brackets(self):
        """指出 / 说 / 认为 / 称 resolve their preceding names; corner
        brackets carry the quote."""
        cases = [
            ('王强指出，「行情会好转。」', '王强', '王强指出'),
            ('赵敏说：“今天不开会。”', '赵敏', '赵敏说'),
            ('钱多认为，“降价是必然的。”', '钱多', '钱多认为'),
            ('孙悦称，“团队已经到位。”', '孙悦', '孙悦称'),
        ]
        for text, speaker, attribution in cases:
            meta = self._analyze(text)
            hit = meta['quotes'][0]
            self.assertEqual(hit['speaker'], speaker, text)
            self.assertEqual(hit['speaker_resolved'], 'name', text)
            self.assertEqual(hit['attribution_text'], attribution, text)

    def test_zh_compound_verb_words_do_not_fire(self):
        """称为 / 说明 are not attribution verbs: single-character verbs
        must be followed by punctuation, a quote mark or whitespace."""
        meta = self._analyze(
            '这份说明称为指南。文档里没有“直接引语”。')
        self.assertEqual(meta['quote_count'], 1)
        hit = meta['quotes'][0]
        self.assertEqual(hit['speaker_resolved'], 'unknown')
        self.assertIsNone(hit['speaker'])

    def test_zh_ju_baodao_attribution(self):
        """`据X报道` introduces quoted coverage; X is the speaker."""
        meta = self._analyze(
            '据新华社报道，“需求正在回升，供应链压力缓解。”')
        hit = meta['quotes'][0]
        self.assertEqual(hit['speaker'], '新华社')
        self.assertEqual(hit['speaker_resolved'], 'name')
        self.assertEqual(hit['attribution_text'], '据新华社报道')

    def test_zh_pronoun_backoff(self):
        """他 after a named attribution resolves to that speaker."""
        meta = self._analyze(
            '王强表示：“项目会按期交付。”他表示，“没有任何障碍。”')
        self.assertEqual(meta['quote_count'], 2)
        first, second = meta['quotes']
        self.assertEqual((first['speaker'], first['speaker_resolved']),
                         ('王强', 'name'))
        self.assertEqual((second['speaker'],
                          second['speaker_resolved']),
                         ('王强', 'pronoun'))
        self.assertEqual(second['attribution_text'], '他表示')
        self.assertEqual(meta['speakers'], {'王强': 2})

    # ========== Pronoun backoff tests ==========

    def test_pronoun_resolves_to_recent_name(self):
        """`She added, "..."` after `Alice Chen said, "..."` resolves to
        Alice Chen with speaker_resolved='pronoun'."""
        meta = self._analyze(
            'Alice Chen said, "First one." '
            'She added, "Second one."')
        self.assertEqual(meta['quote_count'], 2)
        first, second = meta['quotes']
        self.assertEqual((first['speaker'], first['speaker_resolved']),
                         ('Alice Chen', 'name'))
        self.assertEqual((second['speaker'],
                          second['speaker_resolved']),
                         ('Alice Chen', 'pronoun'))
        self.assertEqual(second['attribution_text'], 'She added')

    def test_pronoun_without_antecedent_is_unknown(self):
        """A pronoun attribution at the very start of a document has no
        antecedent: unknown, speaker None."""
        meta = self._analyze('He said, "Hello."')
        hit = meta['quotes'][0]
        self.assertEqual(hit['speaker_resolved'], 'unknown')
        self.assertIsNone(hit['speaker'])
        self.assertEqual(hit['attribution_text'], 'He said')
        self.assertEqual(meta['speakers'], {})

    def test_pronoun_backoff_within_lookback_limit(self):
        """One intervening unattributed quote still leaves the named
        speaker inside the lookback window of 2."""
        meta = self._analyze(
            'Alice Chen said, "The first quote." '
            '"Only the wind," someone whispered. '
            'She said, "That is enough."')
        self.assertEqual(meta['quote_count'], 3)
        self.assertEqual(meta['quotes'][1]['speaker_resolved'], 'unknown')
        hit = meta['quotes'][2]
        self.assertEqual((hit['speaker'], hit['speaker_resolved']),
                         ('Alice Chen', 'pronoun'))

    def test_pronoun_backoff_lookback_limit_exceeded(self):
        """Two intervening unattributed quotes push the named speaker out
        of the lookback window: the pronoun stays unknown."""
        meta = self._analyze(
            'Alice Chen said, "The first quote." '
            'The lights flickered twice. "Only the wind," someone whispered. '
            'A door slammed somewhere. "Nothing at all," another voice muttered. '
            'She said, "That is enough."')
        self.assertEqual(meta['quote_count'], 4)
        self.assertEqual([hit['speaker_resolved']
                          for hit in meta['quotes']],
                         ['name', 'unknown', 'unknown', 'unknown'])
        self.assertIsNone(meta['quotes'][3]['speaker'])

    def test_speaker_lookback_configurable(self):
        """speaker_lookback=3 widens the window so the same document
        resolves the trailing pronoun."""
        analyzer = QuoteAttributionAnalyzer()
        analyzer.speaker_lookback = 3
        text = ('Alice Chen said, "The first quote." '
                'The lights flickered twice. "Only the wind," someone '
                'whispered. '
                'A door slammed somewhere. "Nothing at all," another '
                'voice muttered. '
                'She said, "That is enough."')
        doc = _doc(text)
        analyzer.process_docs([doc], self.query)
        hit = doc.metadata['quotes'][3]
        self.assertEqual((hit['speaker'], hit['speaker_resolved']),
                         ('Alice Chen', 'pronoun'))

    # ========== Unattributed quotes ==========

    def test_unattributed_quote_is_unknown(self):
        """A quote with no attribution pattern anywhere yields
        speaker_resolved='unknown' and no attribution text."""
        meta = self._analyze('Etymology is a winding road. "Unclear at best."')
        hit = meta['quotes'][0]
        self.assertEqual(hit['speaker_resolved'], 'unknown')
        self.assertIsNone(hit['speaker'])
        self.assertIsNone(hit['attribution_text'])
        self.assertEqual(meta['speakers'], {})
        self.assertEqual(meta['quote_count'], 1)

    # ========== Span and cap invariants ==========

    def test_span_invariants(self):
        """Spans reproduce their quotes byte-for-byte, are ordered and
        non-overlapping across a mixed document."""
        text = ('Ann Lee said, "First thought." '
                '"Second thought," said Bo Ma. '
                'Cyr Nao added, “Third thought.”')
        meta = self._analyze(text)
        spans = [hit['span'] for hit in meta['quotes']]
        self.assertEqual(len(spans), 3)
        for hit in meta['quotes']:
            start, end = hit['span']
            self.assertEqual(text[start:end], hit['quote'])
            self.assertEqual(len(hit['quote']), end - start)
            self.assertTrue(hit['quote'][0] in '"“「„')
        for (s1, e1), (s2, e2) in zip(spans, spans[1:]):
            self.assertLessEqual(e1, s2)

    def test_cap_limits_quotes_but_count_reports_total(self):
        """60 quotes cap at the default 50 records while quote_count
        keeps the true total; a configured cap of 5 keeps 5."""
        text = ' '.join(['"Alpha one," Ann said.'] * 60)
        meta = self._analyze(text)
        self.assertEqual(meta['quote_count'], 60)
        self.assertEqual(len(meta['quotes']), 50)

        analyzer = QuoteAttributionAnalyzer()
        analyzer.max_quotes = 5
        doc = _doc(text)
        analyzer.process_docs([doc], self.query)
        self.assertEqual(doc.metadata['quote_count'], 60)
        self.assertEqual(len(doc.metadata['quotes']), 5)

    def test_speakers_deduped_with_counts(self):
        """metadata['speakers'] tallies each resolved speaker once per
        quote, insertion-ordered, unknowns excluded."""
        meta = self._analyze(
            'Alice Chen said, "One." '
            'Bo Ma noted, "Two." '
            '"Three," said Alice Chen. '
            '"Four."')
        self.assertEqual(meta['quote_count'], 4)
        self.assertEqual(meta['speakers'], {'Alice Chen': 2, 'Bo Ma': 1})
        self.assertEqual(meta['quotes'][3]['speaker_resolved'], 'unknown')

    def test_multiple_quotes_share_nearest_attribution(self):
        """Two quotes in one sentence both bind to the single attribution
        verb between them."""
        meta = self._analyze('"Left part," and "right part," Bo Ma said.')
        self.assertEqual(meta['quote_count'], 2)
        for hit in meta['quotes']:
            self.assertEqual(hit['speaker'], 'Bo Ma')
            self.assertEqual(hit['speaker_resolved'], 'name')
        self.assertEqual(meta['speakers'], {'Bo Ma': 2})

    # ========== Pipeline-shape tests ==========

    def test_empty_and_none_text(self):
        """Empty batch yields empty output; empty/None texts stamp empty
        quotes, zero count and an empty speaker tally. (None is assigned
        after construction because Document's id validator hashes the
        constructor text.)"""
        self.assertEqual(
            self.analyzer.process_docs([], self.query), [])

        meta = self._analyze('')
        self.assertEqual(meta['quotes'], [])
        self.assertEqual(meta['quote_count'], 0)
        self.assertEqual(meta['speakers'], {})

        doc = _doc('placeholder')
        doc.text = None
        result = self.analyzer.process_docs([doc], self.query)
        self.assertIs(result[0], doc)
        self.assertEqual(doc.metadata['quotes'], [])
        self.assertEqual(doc.metadata['quote_count'], 0)
        self.assertEqual(doc.metadata['speakers'], {})

    def test_documents_pass_through_untouched(self):
        """Same objects, same order, same text and id; pre-existing
        metadata survives; stamping writes through a copy, not in place."""
        text = 'Ann Lee said, "Pass through intact."'
        doc = _doc(text, source='wire', rank=1)
        meta_ref = doc.metadata
        result = self.analyzer.process_docs([doc], self.query)

        self.assertEqual(len(result), 1)
        self.assertIs(result[0], doc)
        self.assertEqual(doc.text, text)
        self.assertIsNotNone(doc.id)
        self.assertEqual(doc.metadata['source'], 'wire')
        self.assertEqual(doc.metadata['rank'], 1)
        self.assertEqual(doc.metadata['quote_count'], 1)
        # Stamp went through a copied mapping: the caller's original dict
        # object did not gain the new keys in place.
        self.assertNotIn('quotes', meta_ref)
        self.assertIsNot(doc.metadata, meta_ref)

    def test_speaker_tracking_resets_per_document(self):
        """A pronoun in document two does not inherit the named speaker
        of document one."""
        doc1 = _doc('Alice Chen said, "One." She added, "Two."')
        doc2 = _doc('He said, "Fresh start."')
        result = self.analyzer.process_docs([doc1, doc2], self.query)
        self.assertEqual([d.text for d in result],
                         [doc1.text, doc2.text])
        self.assertEqual(doc1.metadata['quotes'][1]
                         ['speaker_resolved'], 'pronoun')
        self.assertEqual(doc2.metadata['quotes'][0]['speaker'], None)
        self.assertEqual(doc2.metadata['quotes'][0]
                         ['speaker_resolved'], 'unknown')

    def test_metadata_key_stamps_configurable(self):
        """Custom keys land under their names; empty keys disable their
        stamps while the analysis itself still runs."""
        analyzer = QuoteAttributionAnalyzer()
        analyzer.quotes_key = 'pairs'
        analyzer.count_key = 'pairs_total'
        analyzer.speakers_key = 'voices'
        doc = _doc('Ann Lee said, "Hello."')
        analyzer.process_docs([doc], self.query)
        self.assertIn('pairs', doc.metadata)
        self.assertEqual(doc.metadata['pairs_total'], 1)
        self.assertIn('voices', doc.metadata)
        self.assertNotIn('quotes', doc.metadata)

        analyzer.quotes_key = ''
        analyzer.count_key = ''
        analyzer.speakers_key = ''
        doc2 = _doc('Ann Lee said, "Hello."')
        analyzer.process_docs([doc2], self.query)
        self.assertEqual(doc2.metadata, {})

    def test_deterministic_across_runs(self):
        """Identical inputs produce byte-identical metadata on repeated
        runs — no hash-order or randomness leaks in."""
        text = ('Alice Chen said, "One." '
                '"Two," said Bo Ma. '
                '王强指出，“三是中文。” '
                '"Four," she added. '
                '据新华社报道，“五。”')
        first = self._analyze(text)
        for _ in range(3):
            again = self._analyze(text)
            self.assertEqual(first, again)


if __name__ == '__main__':
    unittest.main()
