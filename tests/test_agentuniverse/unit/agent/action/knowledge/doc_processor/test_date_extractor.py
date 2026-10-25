# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_date_extractor.py

import datetime
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.date_extractor import DateExtractor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Fixed anchor injected for every determinism-sensitive test.
FIXED_REF = '2026-10-19'


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestDateExtractor(unittest.TestCase):
    """Comprehensive offline test suite for DateExtractor."""

    def setUp(self):
        self.query = Query(query_str="dates")
        self.extractor = DateExtractor()
        self.extractor.reference_date = FIXED_REF

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _extract(self, text: str):
        """Run extraction over one document, returning its dates."""
        doc = _doc(text)
        self.extractor.process_docs([doc], self.query)
        return (doc.metadata or {}).get('dates', [])

    def _isos(self, text: str):
        """Convenience: ISO values of all entries extracted from text."""
        return [entry['iso'] for entry in self._extract(text)]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: no fixed reference, month-first reading, 'dates' and
        'date_range' metadata keys."""
        fresh = DateExtractor()
        self.assertIsNone(fresh.reference_date)
        self.assertFalse(fresh.day_first)
        self.assertEqual(fresh.dates_key, 'dates')
        self.assertEqual(fresh.range_key, 'date_range')

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization; an
        empty reference_date string means 'no fixed reference'."""
        configer = self._create_configer({
            'name': 'date_extractor',
            'description': 'date extraction',
            'reference_date': '2026-01-02',
            'day_first': True,
            'dates_key': 'found_dates',
            'range_key': 'bounding',
        })
        extractor = DateExtractor()
        extractor._initialize_by_component_configer(configer)
        self.assertEqual(extractor.reference_date, '2026-01-02')
        self.assertTrue(extractor.day_first)
        self.assertEqual(extractor.dates_key, 'found_dates')
        self.assertEqual(extractor.range_key, 'bounding')
        self.assertEqual(extractor.name, 'date_extractor')

    def test_initialize_treats_empty_reference_date_as_none(self):
        """The yaml default '' clears the fixed reference date."""
        configer = self._create_configer({
            'name': 'd', 'description': 'd', 'reference_date': '',
        })
        extractor = DateExtractor()
        extractor.reference_date = '2020-05-05'
        extractor._initialize_by_component_configer(configer)
        self.assertIsNone(extractor.reference_date)

    def test_invalid_configuration_raises(self):
        """Malformed reference dates, non-boolean day_first and
        non-string metadata keys all fail eagerly at load time."""
        base = {
            'name': 'd', 'description': 'd',
            'reference_date': '', 'day_first': False,
            'dates_key': 'dates', 'range_key': 'date_range',
        }
        for key, value in (
            ('reference_date', '2026/10/19'),
            ('reference_date', 'not-a-date'),
            ('reference_date', '2026-02-30'),
            ('reference_date', '26-10-19'),
            ('reference_date', 20261019),
            ('day_first', 'yes'),
            ('day_first', 1),
            ('dates_key', 5),
            ('range_key', ['x']),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                DateExtractor()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Format recognition tests ==========

    def test_iso_dates_with_all_three_separators(self):
        """2026-10-19, 2026/10/19 and 2026.10.19 all normalize to the
        same ISO value; none is flagged ambiguous (year-first is
        unambiguous)."""
        for text in ('2026-10-19', '2026/10/19', '2026.10.19'):
            entries = self._extract(f"published on {text} by the team")
            self.assertEqual(len(entries), 1, text)
            self.assertEqual(entries[0]['iso'], '2026-10-19', text)
            self.assertEqual(entries[0]['kind'], 'date')
            self.assertFalse(entries[0]['ambiguous'], text)

    def test_iso_rejects_mixed_separators(self):
        """2026-10/19 mixes separators and must not match at all."""
        self.assertEqual(self._isos('no date in 2026-10/19 here'), [])

    def test_compact_eight_digit_dates(self):
        """Compact YYYYMMDD parses and never matches inside a longer or
        shorter digit run, but letters around it are fine."""
        self.assertEqual(self._isos('ref 20261019 ok'),
                         ['2026-10-19'])
        self.assertEqual(self._isos('id 1202610193 x'), [])
        self.assertEqual(self._isos('id 202610191 x'), [])
        self.assertEqual(self._isos('id 2026101 x'), [])
        self.assertEqual(self._isos('A20261019B'), ['2026-10-19'])

    def test_us_numeric_date(self):
        """10/19/2026 forces month-first (19 cannot be a month) and is
        not flagged ambiguous."""
        entries = self._extract('released 10/19/2026 worldwide')
        self.assertEqual(entries[0]['iso'], '2026-10-19')
        self.assertFalse(entries[0]['ambiguous'])

    def test_eu_numeric_date(self):
        """19/10/2026 forces day-first (19 cannot be a month) and is
        not flagged ambiguous."""
        entries = self._extract('released 19/10/2026 in Europe')
        self.assertEqual(entries[0]['iso'], '2026-10-19')
        self.assertFalse(entries[0]['ambiguous'])

    def test_month_name_forms(self):
        """Oct 19, 2026 / October 19 2026 / October 19th, 2026 /
        Sept 5 2026 / lowercase and uppercased variants all parse."""
        cases = {
            'Oct 19, 2026': '2026-10-19',
            'October 19 2026': '2026-10-19',
            'October 19th, 2026': '2026-10-19',
            'Oct. 19, 2026': '2026-10-19',
            'SEP 5 2026': '2026-09-05',
            'september 1, 2026': '2026-09-01',
            'March 21, 2026': '2026-03-21',
        }
        for text, iso in cases.items():
            self.assertEqual(self._isos(f"dated {text} accordingly"),
                             [iso], text)

    def test_cjk_full_date(self):
        """2026年10月19日 parses to ISO; span covers the whole
        expression."""
        entries = self._extract('发布于2026年10月19日。')
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['iso'], '2026-10-19')
        self.assertEqual(entries[0]['text'], '2026年10月19日')

    def test_cjk_yearless_uses_reference_year(self):
        """10月19日 borrows the reference year; other yearless forms
        resolve against the same anchor."""
        self.assertEqual(self._isos('定在10月19日举行'),
                         ['2026-10-19'])
        self.assertEqual(self._isos('定在1月1日举行'),
                         ['2026-01-01'])
        self.assertEqual(self._isos('定在12月25日举行'),
                         ['2026-12-25'])

    def test_cjk_yearless_not_double_reported_inside_full(self):
        """A full CJK date suppresses its embedded yearless tail via
        overlap resolution, but a separate yearless date still
        reports."""
        entries = self._extract('2026年10月19日以及10月19日')
        self.assertEqual([e['text'] for e in entries],
                         ['2026年10月19日', '10月19日'])
        self.assertEqual([e['iso'] for e in entries],
                         ['2026-10-19', '2026-10-19'])

    def test_yearless_reference_year_change(self):
        """A different injected reference year moves yearless dates."""
        self.extractor.reference_date = '2024-03-05'
        self.assertEqual(self._isos('10月19日'), ['2024-10-19'])

    # ========== Ambiguity tests ==========

    def test_ambiguous_numeric_default_month_first(self):
        """05/06/2026 (both numbers fit both roles) reads month-first
        by default and is flagged ambiguous."""
        entries = self._extract('meeting 05/06/2026 held')
        self.assertEqual(entries[0]['iso'], '2026-05-06')
        self.assertTrue(entries[0]['ambiguous'])

    def test_ambiguous_numeric_day_first_option(self):
        """day_first=True flips the ambiguous reading to day-first
        while keeping the flag."""
        self.extractor.day_first = True
        entries = self._extract('meeting 05/06/2026 held')
        self.assertEqual(entries[0]['iso'], '2026-06-05')
        self.assertTrue(entries[0]['ambiguous'])

    def test_day_first_ignores_forced_readings(self):
        """day_first never overrides a forced reading: 10/19/2026 and
        19/10/2026 keep their interpretations under day_first=True."""
        self.extractor.day_first = True
        self.assertEqual(self._isos('on 10/19/2026'), ['2026-10-19'])
        self.assertEqual(self._isos('on 19/10/2026'), ['2026-10-19'])

    def test_ambiguity_untouched_by_day_first_on_other_families(self):
        """ISO, month-name and CJK forms stay unflagged under both
        day_first settings."""
        for setting in (False, True):
            self.extractor.day_first = setting
            for text in ('2026-10-19', 'Oct 19, 2026', '2026年10月19日'):
                entries = self._extract(text)
                self.assertFalse(entries[0]['ambiguous'],
                                 f"day_first={setting} {text}")

    # ========== Relative keyword tests ==========

    def test_relative_english_keywords(self):
        """today/tomorrow/yesterday resolve as offsets against the
        fixed reference date, kind 'relative', never ambiguous."""
        entries = self._extract('yesterday today and tomorrow')
        self.assertEqual([e['iso'] for e in entries],
                         ['2026-10-18', '2026-10-19', '2026-10-20'])
        for entry in entries:
            self.assertEqual(entry['kind'], 'relative')
            self.assertFalse(entry['ambiguous'])

    def test_relative_case_insensitive_and_cjk(self):
        """Sentence-case English and CJK equivalents resolve too."""
        entries = self._extract('Today matters; 明天 and 昨天 too')
        self.assertEqual([e['iso'] for e in entries],
                         ['2026-10-19', '2026-10-20', '2026-10-18'])
        self.assertEqual([e['text'] for e in entries],
                         ['Today', '明天', '昨天'])

    def test_relative_default_reference_is_today(self):
        """With reference_date=None the anchor is the processing day
        (guarded against a midnight rollover between the two calls)."""
        extractor = DateExtractor()
        before = datetime.date.today()
        doc = _doc('see you tomorrow')
        extractor.process_docs([doc], self.query)
        after = datetime.date.today()
        iso = doc.metadata['dates'][0]['iso']
        self.assertIn(iso, {(before + datetime.timedelta(days=1)).isoformat(),
                            (after + datetime.timedelta(days=1)).isoformat()})

    def test_relative_word_boundaries(self):
        """Keywords embedded in longer words are ignored; possessive
        forms (today's) still match the keyword itself."""
        self.assertEqual(self._isos('todays plan'), [])
        self.assertEqual(self._isos('yesterdays news'), [])
        self.assertEqual(self._isos("today's plan"), ['2026-10-19'])

    # ========== Range tests ==========

    def test_tilde_range(self):
        """2026-10-01~2026-10-19 becomes one 'range' entry with ISO
        interval notation and a span covering both dates."""
        entries = self._extract('campaign 2026-10-01~2026-10-19 done')
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['kind'], 'range')
        self.assertEqual(entries[0]['iso'], '2026-10-01/2026-10-19')
        self.assertEqual(entries[0]['text'],
                         '2026-10-01~2026-10-19')

    def test_range_separator_variants(self):
        """Spaced tilde, hyphen, en dash and the English 'to' all
        merge adjacent dates."""
        cases = {
            '2026-10-01 ~ 2026-10-19': '2026-10-01/2026-10-19',
            '2026-10-01-2026-10-19': '2026-10-01/2026-10-19',
            '2026-10-01 – 2026-10-19': '2026-10-01/2026-10-19',
            '2026-10-01 to 2026-10-19': '2026-10-01/2026-10-19',
        }
        for text, iso in cases.items():
            self.assertEqual(self._isos(text), [iso], text)

    def test_cjk_range_cong_dao(self):
        """从…到… spans merge into one range entry whose text covers
        both CJK dates (the leading 从 stays outside the span)."""
        text = '从2026年10月1日到2026年10月19日'
        entries = self._extract(text)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['kind'], 'range')
        self.assertEqual(entries[0]['iso'],
                         '2026-10-01/2026-10-19')
        self.assertEqual(entries[0]['text'],
                         '2026年10月1日到2026年10月19日')

    def test_cjk_range_zhi_separator(self):
        """The 至 separator merges CJK dates, whitespace tolerated."""
        self.assertEqual(self._isos('2026年10月1日 至 2026年10月19日'),
                         ['2026-10-01/2026-10-19'])

    def test_non_range_gap_keeps_dates_separate(self):
        """Prose between two dates (' and ', multi-word gaps) blocks
        the merge."""
        entries = self._extract('from 2026-10-01 and 2026-10-19')
        self.assertEqual(len(entries), 2)
        self.assertTrue(all(e['kind'] == 'date' for e in entries))

    def test_relative_dates_never_merge_into_ranges(self):
        """today ~ tomorrow stays two 'relative' entries — ranges join
        concrete dates only."""
        entries = self._extract('today ~ tomorrow')
        self.assertEqual(len(entries), 2)
        self.assertTrue(all(e['kind'] == 'relative' for e in entries))

    def test_range_flagged_when_endpoint_ambiguous(self):
        """A range whose endpoints include an ambiguous numeric date
        carries ambiguous=True."""
        entries = self._extract('05/06/2026~07/08/2026')
        self.assertEqual(entries[0]['kind'], 'range')
        self.assertTrue(entries[0]['ambiguous'])

    def test_three_dates_with_separator_chain(self):
        """A~B~C merges left to right: one range plus a trailing date
        (the greedy leftmost merge wins)."""
        entries = self._extract('2026-10-01~2026-10-19~2026-10-20')
        self.assertEqual([e['kind'] for e in entries],
                         ['range', 'date'])
        self.assertEqual(entries[0]['iso'], '2026-10-01/2026-10-19')
        self.assertEqual(entries[1]['iso'], '2026-10-20')

    # ========== Metadata stamping tests ==========

    def test_metadata_dates_and_range_stamped(self):
        """Two distinct dates stamp both 'dates' and 'date_range'
        [min, max]."""
        doc = _doc('kickoff 2026-05-01, wrap 2026-10-19', source='plan')
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(doc.metadata['dates']), 2)
        self.assertEqual(doc.metadata['date_range'],
                         ['2026-05-01', '2026-10-19'])
        self.assertEqual(doc.metadata['source'], 'plan')

    def test_no_date_range_without_two_distinct_dates(self):
        """A single date, or repeated identical dates, stamp 'dates'
        but never 'date_range'."""
        doc = _doc('only 2026-10-19 here')
        self.extractor.process_docs([doc], self.query)
        self.assertNotIn('date_range', doc.metadata)

        doc = _doc('2026-10-19 then 2026-10-19 again')
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(doc.metadata['dates']), 2)
        self.assertNotIn('date_range', doc.metadata)

    def test_range_endpoints_count_toward_date_range(self):
        """One range entry alone yields two distinct endpoints and
        therefore stamps date_range."""
        doc = _doc('2026-10-01~2026-10-19')
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata['date_range'],
                         ['2026-10-01', '2026-10-19'])

    def test_relative_dates_count_toward_date_range(self):
        """Resolved relative dates participate in the bounding pair."""
        doc = _doc('opened 2026-10-19, closing tomorrow')
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata['date_range'],
                         ['2026-10-19', '2026-10-20'])

    def test_entry_structure_and_order(self):
        """Entries carry exactly the five documented fields, sorted by
        position, spans slice back to the matched text."""
        text = ('on Oct 3, 2026 and 19/10/2026 plus 10月19日 '
                'see you tomorrow')
        entries = self._extract(text)
        self.assertEqual(len(entries), 4)
        self.assertEqual([e['iso'] for e in entries],
                         ['2026-10-03', '2026-10-19', '2026-10-19',
                          '2026-10-20'])
        for entry in entries:
            self.assertEqual(sorted(entry.keys()),
                             ['ambiguous', 'iso', 'kind', 'span', 'text'])
            start, end = entry['span']
            self.assertEqual(text[start:end], entry['text'])

    def test_metadata_copied_not_mutated(self):
        """Stamping writes through a copied mapping; the caller's
        original dict is untouched, existing keys survive."""
        doc = _doc('due 2026-10-19', source='contract', rank=7)
        original = doc.metadata
        self.extractor.process_docs([doc], self.query)
        self.assertIsNot(doc.metadata, original)
        self.assertNotIn('dates', original)
        self.assertEqual(doc.metadata['source'], 'contract')
        self.assertEqual(doc.metadata['rank'], 7)
        self.assertEqual(doc.text, 'due 2026-10-19')

    def test_disabled_keys_stamp_nothing(self):
        """Empty dates_key / range_key disable both stamps."""
        self.extractor.dates_key = ''
        self.extractor.range_key = ''
        doc = _doc('due 2026-10-19', source='contract')
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata, {'source': 'contract'})

    def test_no_dates_passthrough(self):
        """Documents without any date keep metadata completely
        untouched and stay in the batch."""
        doc = _doc('no temporal content whatsoever', keep=1)
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(result, [doc])
        self.assertEqual(doc.metadata, {'keep': 1})

    # ========== Edge and guard tests ==========

    def test_impossible_dates_skipped(self):
        """Calendar-invalid expressions are ignored rather than
        normalized: Feb 30, month 13, day 32, compact garbage, EU/US
        impossible readings, CJK yearless Feb 30."""
        for text in ('2026-02-30', '2026-13-01', '2026-10-32',
                     'Feb 30, 2026', '13/13/2026', '12/32/2026',
                     '20261319', '20260230', '2月30日', '13月1日'):
            self.assertEqual(self._extract(text), [], text)

    def test_leap_year_handling(self):
        """Feb 29 parses in leap years only."""
        self.assertEqual(self._isos('2024-02-29'), ['2024-02-29'])
        self.assertEqual(self._isos('2023-02-29'), [])

    def test_empty_and_blank_inputs(self):
        """An empty batch returns []; blank text stamps nothing and
        raises nothing (Document itself cannot hold text=None — its id
        validator hashes the text — so blank strings are the empty
        case)."""
        self.assertEqual(
            self.extractor.process_docs([], self.query), [])
        for text in ('', '   '):
            doc = _doc(text, tag='x')
            self.extractor.process_docs([doc], self.query)
            self.assertNotIn('dates', doc.metadata or {})

    def test_batch_order_and_count_preserved(self):
        """Mixed batches come back in the same order and count; only
        documents with hits are stamped."""
        docs = [
            _doc('alpha 2026-10-19'),
            _doc('beta nothing'),
            _doc('gamma 10/19/2026 and tomorrow'),
        ]
        result = self.extractor.process_docs(docs, self.query)
        self.assertEqual(result, docs)
        self.assertNotIn('dates', docs[1].metadata or {})
        self.assertEqual(len(docs[2].metadata['dates']), 2)
        self.assertEqual(docs[2].metadata['date_range'],
                         ['2026-10-19', '2026-10-20'])

    def test_deterministic_given_reference_date(self):
        """Identical inputs and reference dates produce byte-identical
        output across runs and instances."""
        text = 'Oct 3, 2026 ~ 10/19/2026, 从1月1日到3月5日, yesterday'
        first = DateExtractor()
        first.reference_date = FIXED_REF
        doc_a, doc_b = _doc(text), _doc(text)
        first.process_docs([doc_a], self.query)
        self.extractor.process_docs([doc_b], self.query)
        self.assertEqual(doc_a.metadata, doc_b.metadata)

        again = _doc(text)
        first.process_docs([again], self.query)
        self.assertEqual(doc_a.metadata, again.metadata)

    def test_reference_date_accepted_as_date_object(self):
        """datetime/date objects are accepted anchors for relative
        resolution."""
        entries = self.extractor._extract(
            'today', datetime.date(2020, 2, 29))
        self.assertEqual(entries[0]['iso'], '2020-02-29')


if __name__ == '__main__':
    unittest.main()
