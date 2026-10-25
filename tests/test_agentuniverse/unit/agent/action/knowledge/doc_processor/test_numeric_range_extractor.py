# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20 00:00
# @Author  : AI Assistant
# @Email   : ai@example.com
# @FileName: test_numeric_range_extractor.py

import unittest
from decimal import Decimal
from unittest.mock import Mock

from pydantic import ValidationError

from agentuniverse.agent.action.knowledge.doc_processor.\
    numeric_range_extractor import NumericRangeExtractor
from agentuniverse.agent.action.knowledge.store.document import Document


class TestNumericRangeExtractor(unittest.TestCase):
    """Test cases for NumericRangeExtractor."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = NumericRangeExtractor(
            name='test_numeric_range_extractor',
            max_ranges=50,
        )

    def _extract(self, text):
        """Process one document and return its numeric_ranges metadata."""
        docs = self.extractor.process_docs([Document(text=text)])
        return docs[0].metadata['numeric_ranges']

    def _single(self, text):
        """Assert exactly one range is extracted and return it."""
        hits = self._extract(text)
        self.assertEqual(len(hits), 1,
                         'expected exactly one range in {!r}, got {!r}'.format(
                             text, hits))
        return hits[0]

    # ------------------------------------------------------------------
    # Closed ranges, English connectors
    # ------------------------------------------------------------------

    def test_en_to_range(self):
        """X to Y with a trailing unit."""
        hit = self._single('Costs range 10 to 20 USD per license.')
        self.assertEqual(hit['kind'], 'closed')
        self.assertEqual(Decimal(hit['min']), Decimal('10'))
        self.assertEqual(Decimal(hit['max']), Decimal('20'))
        self.assertEqual(hit['unit'], 'USD')
        self.assertEqual(hit['notes'], [])
        self.assertEqual(hit['text'], '10 to 20 USD')

    def test_between_and_range(self):
        """between X and Y with decimal endpoints."""
        hit = self._single('Keep between 5.5 and 6.5 volts.')
        self.assertEqual(hit['kind'], 'closed')
        self.assertEqual(Decimal(hit['min']), Decimal('5.5'))
        self.assertEqual(Decimal(hit['max']), Decimal('6.5'))
        self.assertEqual(hit['unit'], 'volts')

    def test_from_to_range_with_comma_groups(self):
        """from X to Y with comma digit groups."""
        hit = self._single('We hired from 1,000 to 2,500 users.')
        self.assertEqual(hit['kind'], 'closed')
        self.assertEqual(Decimal(hit['min']), Decimal('1000'))
        self.assertEqual(Decimal(hit['max']), Decimal('2500'))
        self.assertEqual(hit['unit'], 'users')
        self.assertEqual(hit['text'], 'from 1,000 to 2,500 users')

    def test_from_to_single_hit_no_duplicate(self):
        """The inner `X to Y` of `from X to Y` must not produce a second hit."""
        hits = self._extract('The plan runs from 5 to 10 days.')
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]['text'], 'from 5 to 10 days')

    def test_dash_connector_variants(self):
        """Hyphen, en dash, em dash and tilde connectors."""
        for text, snippet in (
                ('Read 10-20 pages.', '10-20 pages'),
                ('Read 10–20 pages.', '10–20 pages'),
                ('Read 10—20 pages.', '10—20 pages'),
                ('Read 10~20 pages.', '10~20 pages')):
            hit = self._single(text)
            self.assertEqual(hit['kind'], 'closed')
            self.assertEqual(Decimal(hit['min']), Decimal('10'))
            self.assertEqual(Decimal(hit['max']), Decimal('20'))
            self.assertEqual(hit['unit'], 'pages')
            self.assertEqual(hit['text'], snippet)

    # ------------------------------------------------------------------
    # Closed ranges, Chinese connectors
    # ------------------------------------------------------------------

    def test_zh_closed_connectors(self):
        """至 / 到 connectors with CJK units."""
        hit = self._single('库存3至5个')
        self.assertEqual(hit['kind'], 'closed')
        self.assertEqual(Decimal(hit['min']), Decimal('3'))
        self.assertEqual(Decimal(hit['max']), Decimal('5'))
        self.assertEqual(hit['unit'], '个')
        self.assertEqual(hit['text'], '3至5个')

        hit = self._single('增长3到5倍')
        self.assertEqual(hit['kind'], 'closed')
        self.assertEqual(Decimal(hit['min']), Decimal('3'))
        self.assertEqual(Decimal(hit['max']), Decimal('5'))
        self.assertEqual(hit['unit'], '倍')

        hit = self._single('周期3—5天')
        self.assertEqual(hit['kind'], 'closed')
        self.assertEqual(hit['unit'], '天')
        self.assertEqual(hit['text'], '3—5天')

    # ------------------------------------------------------------------
    # Open ranges
    # ------------------------------------------------------------------

    def test_open_lower_en(self):
        """over X / above X."""
        hit = self._single('Spend over 90% of the quota.')
        self.assertEqual(hit['kind'], 'open_lower')
        self.assertEqual(Decimal(hit['min']), Decimal('90'))
        self.assertIsNone(hit['max'])
        self.assertEqual(hit['unit'], '%')
        self.assertEqual(hit['text'], 'over 90%')

        hit = self._single('Serve above 5000 users.')
        self.assertEqual(hit['kind'], 'open_lower')
        self.assertEqual(Decimal(hit['min']), Decimal('5000'))
        self.assertIsNone(hit['max'])
        self.assertEqual(hit['unit'], 'users')

    def test_open_lower_zh(self):
        """超过X / X以上 / X或以上 / X及以上."""
        hit = self._single('投入超过100元')
        self.assertEqual(hit['kind'], 'open_lower')
        self.assertEqual(Decimal(hit['min']), Decimal('100'))
        self.assertIsNone(hit['max'])
        self.assertEqual(hit['unit'], '元')

        hit = self._single('需3个以上')
        self.assertEqual(hit['kind'], 'open_lower')
        self.assertEqual(Decimal(hit['min']), Decimal('3'))
        self.assertEqual(hit['unit'], '个')

        hit = self._single('限18岁或以上')
        self.assertEqual(hit['kind'], 'open_lower')
        self.assertEqual(Decimal(hit['min']), Decimal('18'))
        self.assertIsNone(hit['max'])
        self.assertEqual(hit['unit'], '岁')

        hit = self._single('满2年及以上')
        self.assertEqual(hit['kind'], 'open_lower')
        self.assertEqual(Decimal(hit['min']), Decimal('2'))
        self.assertEqual(hit['unit'], '年')

    def test_open_upper(self):
        """不超过Y / Y以下 / Y及以下."""
        hit = self._single('温度不超过40℃')
        self.assertEqual(hit['kind'], 'open_upper')
        self.assertIsNone(hit['min'])
        self.assertEqual(Decimal(hit['max']), Decimal('40'))
        self.assertEqual(hit['unit'], '℃')

        hit = self._single('未成年人（18岁以下）')
        self.assertEqual(hit['kind'], 'open_upper')
        self.assertIsNone(hit['min'])
        self.assertEqual(Decimal(hit['max']), Decimal('18'))
        self.assertEqual(hit['unit'], '岁')

        hit = self._single('不超过1000字及以下均可')
        hit = self._single('稿件不超过1000字')
        self.assertEqual(hit['kind'], 'open_upper')
        self.assertEqual(Decimal(hit['max']), Decimal('1000'))
        self.assertEqual(hit['unit'], '字')

        hit = self._single('年龄60及以下')
        self.assertEqual(hit['kind'], 'open_upper')
        self.assertEqual(Decimal(hit['max']), Decimal('60'))

    def test_open_bounds_en_or_and_forms(self):
        """X or above / X and above / Y or below / Y and below."""
        hit = self._single('Quantity is 3 or above.')
        self.assertEqual(hit['kind'], 'open_lower')
        self.assertEqual(Decimal(hit['min']), Decimal('3'))
        self.assertIsNone(hit['max'])

        hit = self._single('Requires 5 tokens and above.')
        self.assertEqual(hit['kind'], 'open_lower')
        self.assertEqual(Decimal(hit['min']), Decimal('5'))
        self.assertEqual(hit['unit'], 'tokens')

        hit = self._single('Discount for ages 60 or below.')
        self.assertEqual(hit['kind'], 'open_upper')
        self.assertIsNone(hit['min'])
        self.assertEqual(Decimal(hit['max']), Decimal('60'))

        hit = self._single('Scores of 40 and below fail.')
        self.assertEqual(hit['kind'], 'open_upper')
        self.assertEqual(Decimal(hit['max']), Decimal('40'))

    # ------------------------------------------------------------------
    # Decimal normalization: multipliers and comma groups
    # ------------------------------------------------------------------

    def test_cjk_multipliers_in_ranges(self):
        """万 / 亿 multipliers applied to range endpoints."""
        hit = self._single('收入3万至5万元')
        self.assertEqual(Decimal(hit['min']), Decimal('30000'))
        self.assertEqual(Decimal(hit['max']), Decimal('50000'))
        self.assertEqual(hit['unit'], '元')

        hit = self._single('规模2.5亿至4.5亿')
        self.assertEqual(Decimal(hit['min']), Decimal('250000000'))
        self.assertEqual(Decimal(hit['max']), Decimal('450000000'))

        hit = self._single('年薪20万以上')
        self.assertEqual(hit['kind'], 'open_lower')
        self.assertEqual(Decimal(hit['min']), Decimal('200000'))

        hit = self._single('融资2.5亿及以上')
        self.assertEqual(hit['kind'], 'open_lower')
        self.assertEqual(Decimal(hit['min']), Decimal('250000000'))

    def test_decimal_exactness(self):
        """Exact Decimal strings, no float artifacts, no exponents."""
        hit = self._single('稀释至0.125到0.375升')
        self.assertEqual(hit['min'], '0.125')
        self.assertEqual(hit['max'], '0.375')

        hit = self._single('每份1,234,567到2,468,135字节')
        self.assertEqual(hit['min'], '1234567')
        self.assertEqual(hit['max'], '2468135')

    # ------------------------------------------------------------------
    # Units
    # ------------------------------------------------------------------

    def test_unit_extraction_same_unit_both_sides(self):
        """Same unit on both endpoints resolves once without notes."""
        hit = self._single('Failure rate moved from 10% to 20%')
        self.assertEqual(hit['unit'], '%')
        self.assertEqual(hit['notes'], [])

    def test_unit_mismatch_note(self):
        """Different units: second number's unit wins plus a note."""
        hit = self._single('Convert 10 kg to 20 lb per box.')
        self.assertEqual(hit['unit'], 'lb')
        self.assertEqual(hit['notes'], ['unit_mismatch(kg|lb)'])

    def test_currency_prefix_units(self):
        """Currency symbols before each endpoint act as the unit."""
        hit = self._single('Tickets cost $5 to $10 each.')
        self.assertEqual(hit['unit'], '$')
        self.assertEqual(hit['notes'], [])

        hit = self._single('价格¥3—¥5')
        self.assertEqual(hit['unit'], '¥')
        self.assertEqual(Decimal(hit['min']), Decimal('3'))
        self.assertEqual(Decimal(hit['max']), Decimal('5'))

    def test_unit_mixed_cjk_en(self):
        """CJK units and ASCII word units are both recognized."""
        hit = self._single('延迟不超过500ms')
        self.assertEqual(hit['unit'], 'ms')
        hit = self._single('需要30到50个盒子')
        self.assertEqual(hit['unit'], '个')

    # ------------------------------------------------------------------
    # Guards
    # ------------------------------------------------------------------

    def test_guard_year_ranges_deferred_to_date_extractor(self):
        """Closed ranges whose both endpoints are years 1900-2100 are skipped."""
        for text in ('FY 2020-2025 was tough.',
                     '从2020至2025年持续增长。',
                     'It grew from 2020 to 2025 steadily.'):
            self.assertEqual(self._extract(text), [],
                             'year range should be skipped: {!r}'.format(text))

    def test_guard_year_boundary_keeps_non_year_ranges(self):
        """A 4-digit endpoint outside 1900-2100 keeps the range."""
        hit = self._single('容量2000到3000人')
        self.assertEqual(hit['kind'], 'closed')
        self.assertEqual(Decimal(hit['min']), Decimal('2000'))
        self.assertEqual(Decimal(hit['max']), Decimal('3000'))
        self.assertEqual(hit['unit'], '人')

    def test_guard_dates(self):
        """Date-shaped spans are skipped."""
        for text in ('released 2024-01-15',
                     'published on 2024/3/5',
                     'deadline 01-15-2024'):
            self.assertEqual(self._extract(text), [],
                             'date should be skipped: {!r}'.format(text))

    def test_guard_versions(self):
        """Version-shaped spans are skipped; word connectors keep decimals."""
        for text in ('upgrade v1.2-1.5',
                     'version 1.2.3-1.2.4',
                     'build 1.5-2.5',
                     'node 192.168.1.1-192.168.1.10'):
            self.assertEqual(self._extract(text), [],
                             'version/IP shape should be skipped: {!r}'.format(
                                 text))
        hit = self._single('稀释1.5 to 2.5 kg')
        self.assertEqual(Decimal(hit['min']), Decimal('1.5'))
        self.assertEqual(Decimal(hit['max']), Decimal('2.5'))
        self.assertEqual(hit['unit'], 'kg')

    def test_guard_urls(self):
        """Ranges inside URLs are skipped, ranges outside are kept."""
        self.assertEqual(
            self._extract('See https://example.com/list?gte=5-10 now.'), [])
        hits = self._extract('See https://example.com/x for 5-10 items.')
        self.assertEqual(len(hits), 1)
        self.assertEqual(Decimal(hits[0]['min']), Decimal('5'))
        self.assertEqual(Decimal(hits[0]['max']), Decimal('10'))

    def test_guard_phones(self):
        """Phone-like digit runs are skipped."""
        for text in ('call 010-12345678',
                     'hotline 400-800-1200',
                     'fax 550-123456'):
            self.assertEqual(self._extract(text), [],
                             'phone-like run should be skipped: {!r}'.format(
                                 text))
        hit = self._single('port 300-500 range')
        self.assertEqual(Decimal(hit['min']), Decimal('300'))
        self.assertEqual(Decimal(hit['max']), Decimal('500'))

    # ------------------------------------------------------------------
    # Inverted ranges
    # ------------------------------------------------------------------

    def test_inverted_closed_range_kept_with_note(self):
        """min > max closed ranges are kept with an inverted_range note."""
        hit = self._single('Coverage fell from 20 to 10 points.')
        self.assertEqual(hit['kind'], 'closed')
        self.assertEqual(Decimal(hit['min']), Decimal('20'))
        self.assertEqual(Decimal(hit['max']), Decimal('10'))
        self.assertIn('inverted_range', hit['notes'])
        self.assertEqual(hit['unit'], 'points')

    # ------------------------------------------------------------------
    # Span invariants and ordering
    # ------------------------------------------------------------------

    def test_span_invariants(self):
        """text[span] == hit text; spans ordered and non-overlapping."""
        text = 'A 10-20 kg batch, 30到50个盒子, over 75% yield.'
        hits = self._extract(text)
        self.assertEqual(len(hits), 3)
        last_end = -1
        for hit in hits:
            start, end = hit['span']
            self.assertEqual(text[start:end], hit['text'])
            self.assertGreaterEqual(start, last_end)
            self.assertGreater(end, start)
            last_end = end

    def test_hits_ordered_by_position(self):
        """Hits are returned in text order."""
        text = 'first 1-2, second 3-4, third 5-6.'
        hits = self._extract(text)
        self.assertEqual([h['text'] for h in hits],
                         ['1-2', '3-4', '5-6'])

    # ------------------------------------------------------------------
    # Cap and metadata stamping
    # ------------------------------------------------------------------

    def test_max_ranges_cap(self):
        """Only max_ranges hits are stored plus a truncation flag."""
        text = ' '.join('{}-{}'.format(i, i + 1) for i in range(1, 61))
        doc = Document(text=text)
        docs = self.extractor.process_docs([doc])
        metadata = docs[0].metadata
        self.assertEqual(len(metadata['numeric_ranges']), 50)
        self.assertEqual(metadata['range_count'], 50)
        self.assertTrue(metadata['range_truncated'])
        self.assertEqual(metadata['numeric_ranges'][0]['text'], '1-2')

    def test_max_ranges_custom_value(self):
        """A custom max_ranges value caps accordingly."""
        extractor = NumericRangeExtractor(name='cap', max_ranges=7)
        text = ' '.join('{}-{}'.format(i, i + 1) for i in range(1, 21))
        doc = Document(text=text)
        extractor.process_docs([doc])
        self.assertEqual(len(doc.metadata['numeric_ranges']), 7)
        self.assertEqual(doc.metadata['range_count'], 7)
        self.assertTrue(doc.metadata['range_truncated'])

    def test_no_truncation_flag_when_under_cap(self):
        """No range_truncated flag when all ranges fit."""
        extractor = NumericRangeExtractor(name='cap', max_ranges=10)
        text = ' '.join('{}-{}'.format(i, i + 1) for i in range(1, 6))
        doc = Document(text=text)
        extractor.process_docs([doc])
        self.assertEqual(doc.metadata['range_count'], 5)
        self.assertNotIn('range_truncated', doc.metadata)

    def test_no_ranges_passthrough(self):
        """Documents without ranges pass through with empty stamps."""
        doc = Document(text='No numbers here at all.',
                       metadata={'source': 'unit-test'})
        docs = self.extractor.process_docs([doc])
        self.assertEqual(len(docs), 1)
        self.assertIs(docs[0], doc)
        self.assertEqual(doc.text, 'No numbers here at all.')
        self.assertEqual(doc.metadata['numeric_ranges'], [])
        self.assertEqual(doc.metadata['range_count'], 0)
        self.assertEqual(doc.metadata['source'], 'unit-test')
        self.assertNotIn('range_truncated', doc.metadata)

    def test_empty_text(self):
        """Empty text yields empty range metadata."""
        doc = Document(text='')
        self.extractor.process_docs([doc])
        self.assertEqual(doc.metadata['numeric_ranges'], [])
        self.assertEqual(doc.metadata['range_count'], 0)

    def test_empty_document_list(self):
        """An empty input list returns an empty list."""
        self.assertEqual(self.extractor.process_docs([]), [])

    def test_metadata_none_initialized(self):
        """Documents with null metadata get a fresh metadata dict."""
        doc = Document(text='5-10 items')
        doc.metadata = None
        self.extractor.process_docs([doc])
        self.assertEqual(doc.metadata['range_count'], 1)
        self.assertEqual(Decimal(doc.metadata['numeric_ranges'][0]['max']),
                         Decimal('10'))

    # ------------------------------------------------------------------
    # Config validation
    # ------------------------------------------------------------------

    def test_invalid_max_ranges_zero(self):
        """max_ranges of zero is rejected at processing time."""
        extractor = NumericRangeExtractor(name='bad', max_ranges=0)
        with self.assertRaises(ValueError):
            extractor.process_docs([Document(text='1-2 items')])

    def test_invalid_max_ranges_type(self):
        """A non-integer max_ranges is rejected by the model."""
        with self.assertRaises(ValidationError):
            NumericRangeExtractor(name='bad', max_ranges='abc')

    def test_configer_initialization(self):
        """The component configer wiring validates and applies max_ranges."""
        configer = Mock(spec=['name', 'description', 'max_ranges'])
        configer.name = 'numeric_range_extractor'
        configer.description = 'test'
        configer.max_ranges = -1
        with self.assertRaises(ValueError):
            NumericRangeExtractor(name='n').\
                _initialize_by_component_configer(configer)

        configer.max_ranges = 25
        extractor = NumericRangeExtractor(name='n').\
            _initialize_by_component_configer(configer)
        self.assertEqual(extractor.max_ranges, 25)

    # ------------------------------------------------------------------
    # Determinism
    # ------------------------------------------------------------------

    def test_deterministic_output(self):
        """Repeated runs over the same text produce identical metadata."""
        text = ('从3万至5万元的预算，延迟不超过500ms，between 1.5 and 2.5 kg, '
                'over 75% yield, 覆盖2000到3000人, v1.2-1.5 已跳过。')
        doc1 = Document(text=text)
        doc2 = Document(text=text)
        self.extractor.process_docs([doc1])
        self.extractor.process_docs([doc2])
        self.assertEqual(doc1.metadata['numeric_ranges'],
                         doc2.metadata['numeric_ranges'])
        self.assertEqual(doc1.metadata['range_count'], 5)

    # ------------------------------------------------------------------
    # Hostile review regressions: negative endpoints
    # ------------------------------------------------------------------

    def test_negative_closed_en(self):
        """Word-connector ranges with negative endpoints keep the sign."""
        hit = self._single('Winter temps range -10 to -5°C.')
        self.assertEqual(hit['kind'], 'closed')
        self.assertEqual(Decimal(hit['min']), Decimal('-10'))
        self.assertEqual(Decimal(hit['max']), Decimal('-5'))
        self.assertEqual(hit['unit'], '°C')
        self.assertEqual(hit['notes'], [])

        hit = self._single('Scores ranged from -3 to 4 points.')
        self.assertEqual(Decimal(hit['min']), Decimal('-3'))
        self.assertEqual(Decimal(hit['max']), Decimal('4'))
        self.assertEqual(hit['unit'], 'points')

        hit = self._single('Loss between -2.5 and -1.5 billion.')
        self.assertEqual(Decimal(hit['min']), Decimal('-2.5'))
        self.assertEqual(Decimal(hit['max']), Decimal('-1.5'))

    def test_negative_closed_zh(self):
        """Chinese connector ranges with negative endpoints keep the sign."""
        hit = self._single('温度降至-10到-5度')
        self.assertEqual(Decimal(hit['min']), Decimal('-10'))
        self.assertEqual(Decimal(hit['max']), Decimal('-5'))
        self.assertEqual(hit['unit'], '度')

        hit = self._single('失业率-5%到-3%')
        self.assertEqual(Decimal(hit['min']), Decimal('-5'))
        self.assertEqual(Decimal(hit['max']), Decimal('-3'))
        self.assertEqual(hit['unit'], '%')

    def test_negative_open_bounds(self):
        """Open bounds with negative endpoints keep the sign."""
        probes = (
            ('Threshold crosses over -10 dB.', 'open_lower', '-10', 'dB'),
            ('Keep it below -20°C.', 'open_upper', '-20', '°C'),
            ('误差不超过-0.5%', 'open_upper', '-0.5', '%'),
            ('no more than -2 delta', 'open_upper', '-2', 'delta'),
            ('at least -10 margin', 'open_lower', '-10', 'margin'),
        )
        for text, kind, value, unit in probes:
            hit = self._single(text)
            self.assertEqual(hit['kind'], kind, text)
            if kind == 'open_lower':
                self.assertEqual(Decimal(hit['min']), Decimal(value), text)
                self.assertIsNone(hit['max'], text)
            else:
                self.assertEqual(Decimal(hit['max']), Decimal(value), text)
                self.assertIsNone(hit['min'], text)
            self.assertEqual(hit['unit'], unit, text)

    def test_glued_separator_numbers_never_start_a_range(self):
        """Numbers glued to a preceding . / : are skipped (no wrong values)."""
        for text in ('.5 to 1.5 liters',
                     'shutter 1/250 to 1/500 s',
                     'aperture f/2.8 to f/4',
                     'ratio 1:2到1:4',
                     'p.3-5'):
            self.assertEqual(self._extract(text), [],
                             'glued form should be skipped: {!r}'.format(
                                 text))

    def test_glued_guard_keeps_spaced_forms(self):
        """Spaced page references still extract after the glued guard."""
        hit = self._single('See manual p. 3-5 for wiring.')
        self.assertEqual(Decimal(hit['min']), Decimal('3'))
        self.assertEqual(Decimal(hit['max']), Decimal('5'))

    # ------------------------------------------------------------------
    # Hostile review regressions: currency equivalence and units
    # ------------------------------------------------------------------

    def test_currency_equivalence_no_mismatch_note(self):
        """Equivalent currency symbols/codes on both endpoints unify."""
        hit = self._single('价格¥3,000-5,000元')
        self.assertEqual(Decimal(hit['min']), Decimal('3000'))
        self.assertEqual(Decimal(hit['max']), Decimal('5000'))
        self.assertEqual(hit['unit'], '元')
        self.assertEqual(hit['notes'], [])

        hit = self._single('from $5 to 10 USD')
        self.assertEqual(hit['unit'], 'USD')
        self.assertEqual(hit['notes'], [])

        hit = self._single('￥3-5')
        self.assertEqual(hit['unit'], '￥')
        self.assertEqual(Decimal(hit['min']), Decimal('3'))
        self.assertEqual(Decimal(hit['max']), Decimal('5'))

    def test_additional_cjk_units_and_degree_symbol(self):
        """Seat, electrical and bare-degree units are recognized."""
        for text, unit in (('功率500-800瓦', '瓦'),
                           ('转速3000-5000转', '转'),
                           ('电流1到2安', '安'),
                           ('座位数5到7座', '座'),
                           ('angle 45° to 90°', '°')):
            hit = self._single(text)
            self.assertEqual(hit['unit'], unit, text)

    def test_multichar_cjk_nouns_have_no_unit(self):
        """Multi-character CJK count nouns resolve to no unit, not garbage."""
        hit = self._single('The region counts 5万-10万用户.')
        self.assertEqual(hit['unit'], None)
        self.assertEqual(Decimal(hit['min']), Decimal('50000'))
        self.assertEqual(Decimal(hit['max']), Decimal('100000'))

    # ------------------------------------------------------------------
    # Hostile review regressions: version guard refinements
    # ------------------------------------------------------------------

    def test_version_guard_spares_definite_units_and_multipliers(self):
        """Dash decimal ranges with a multiplier, currency or unit extract."""
        for text, lo, hi, unit in (
                ('1.5万-2.5万', '15000', '25000', None),
                ('价格1.5-2.5万元', '15000', '25000', '元'),
                ('利率2.5%-3.5%', '2.5', '3.5', '%'),
                ('dilute 1.5-2.5 L', '1.5', '2.5', 'L'),
                ('range 2.0-3.0 m', '2.0', '3.0', 'm'),
                ('$1.5-2.5', '1.5', '2.5', '$')):
            hit = self._single(text)
            self.assertEqual(Decimal(hit['min']), Decimal(lo), text)
            self.assertEqual(Decimal(hit['max']), Decimal(hi), text)
            self.assertEqual(hit['unit'], unit, text)

    def test_version_guard_still_skips_prose_word_units(self):
        """Dash decimal ranges followed by prose words stay version-shaped."""
        for text in ('GPA 3.5-4.0 scale',
                     'build 2.0-3.0 stable',
                     'build 1.5-2.5'):
            self.assertEqual(self._extract(text), [],
                             'version-shaped range should be skipped: '
                             '{!r}'.format(text))

    # ------------------------------------------------------------------
    # Hostile review regressions: inferred multiplier
    # ------------------------------------------------------------------

    def test_inferred_multiplier_scales_bare_endpoint(self):
        """A lone 万/亿 scales the bare endpoint, with a note."""
        for text, lo, hi in (('规模3到5万', '30000', '50000'),
                             ('薪资20-30万', '200000', '300000'),
                             ('融资1到2亿', '100000000', '200000000'),
                             ('1.5-2.5万', '15000', '25000')):
            hit = self._single(text)
            self.assertEqual(Decimal(hit['min']), Decimal(lo), text)
            self.assertEqual(Decimal(hit['max']), Decimal(hi), text)
            self.assertIn('multiplier_inferred', hit['notes'], text)

    def test_inferred_multiplier_skipped_when_it_would_invert(self):
        """Scaling that would invert the range is not applied."""
        hit = self._single('从100到3.5亿')
        self.assertEqual(Decimal(hit['min']), Decimal('100'))
        self.assertEqual(Decimal(hit['max']), Decimal('350000000'))
        self.assertNotIn('multiplier_inferred', hit['notes'])

    def test_both_multipliers_never_infer(self):
        """Endpoints each carrying a multiplier produce no inference note."""
        hit = self._single('收入3万至5万元')
        self.assertEqual(hit['notes'], [])

    # ------------------------------------------------------------------
    # Hostile review regressions: additional open-bound phrasings
    # ------------------------------------------------------------------

    def test_open_prefix_bound_phrases(self):
        """up to / under / below / at least / at most / no more|less than."""
        probes = (
            ('Capacity up to 100 TB.', 'open_upper', '100', 'TB'),
            ('Children under 5 years.', 'open_upper', '5', 'years'),
            ('Keep it below 100ms.', 'open_upper', '100', 'ms'),
            ('Under 18 not admitted.', 'open_upper', '18', None),
            ('At least 3 nodes required.', 'open_lower', '3', 'nodes'),
            ('Allow at most 5 retries.', 'open_upper', '5', 'retries'),
            ('No more than 10 items.', 'open_upper', '10', 'items'),
            ('No less than 8 hours.', 'open_lower', '8', 'hours'),
        )
        for text, kind, value, unit in probes:
            hit = self._single(text)
            self.assertEqual(hit['kind'], kind, text)
            if kind == 'open_lower':
                self.assertEqual(Decimal(hit['min']), Decimal(value), text)
            else:
                self.assertEqual(Decimal(hit['max']), Decimal(value), text)
            self.assertEqual(hit['unit'], unit, text)

    def test_open_suffix_bound_phrases(self):
        """X or more / X or less / X at most / X at least."""
        probes = (
            ('Valid for 5 or more days.', 'open_lower', '5'),
            ('Limit 10 or less per user.', 'open_upper', '10'),
            ('Queue of 5 at most.', 'open_upper', '5'),
            ('Bring 2 at least.', 'open_lower', '2'),
        )
        for text, kind, value in probes:
            hit = self._single(text)
            self.assertEqual(hit['kind'], kind, text)
            if kind == 'open_lower':
                self.assertEqual(Decimal(hit['min']), Decimal(value), text)
            else:
                self.assertEqual(Decimal(hit['max']), Decimal(value), text)

    def test_open_zh_lower_higher_forms(self):
        """低于 / 高于 / 不高于 / 不低于 bounds with signs and multipliers."""
        probes = (
            ('延迟低于500ms', 'open_upper', '500', 'ms'),
            ('误差高于0.5%', 'open_lower', '0.5', '%'),
            ('薪资高于20万', 'open_lower', '200000', None),
            ('不高于-2℃', 'open_upper', '-2', '℃'),
            ('不低于-5%', 'open_lower', '-5', '%'),
            ('流量低于10GB', 'open_upper', '10', 'GB'),
        )
        for text, kind, value, unit in probes:
            hit = self._single(text)
            self.assertEqual(hit['kind'], kind, text)
            if kind == 'open_lower':
                self.assertEqual(Decimal(hit['min']), Decimal(value), text)
            else:
                self.assertEqual(Decimal(hit['max']), Decimal(value), text)
            self.assertEqual(hit['unit'], unit, text)

    # ------------------------------------------------------------------
    # Hostile review regressions: directional connectors
    # ------------------------------------------------------------------

    def test_directional_en_connectors(self):
        """X up to Y closes a range; X down to Y keeps the inverted note."""
        hit = self._single('Earn from 5 up to 10 points.')
        self.assertEqual(hit['kind'], 'closed')
        self.assertEqual(Decimal(hit['min']), Decimal('5'))
        self.assertEqual(Decimal(hit['max']), Decimal('10'))
        self.assertEqual(hit['unit'], 'points')

        hit = self._single('usage 8GB down to 2GB')
        self.assertEqual(Decimal(hit['min']), Decimal('8'))
        self.assertEqual(Decimal(hit['max']), Decimal('2'))
        self.assertIn('inverted_range', hit['notes'])

    def test_directional_zh_connectors(self):
        """降至/降到/升至/升到 connect; 升 is not read as a left unit."""
        hit = self._single('产量由20升到30吨')
        self.assertEqual(Decimal(hit['min']), Decimal('20'))
        self.assertEqual(Decimal(hit['max']), Decimal('30'))
        self.assertEqual(hit['unit'], '吨')
        self.assertEqual(hit['notes'], [])

        hit = self._single('效率从60升至90分')
        self.assertEqual(Decimal(hit['min']), Decimal('60'))
        self.assertEqual(Decimal(hit['max']), Decimal('90'))
        self.assertEqual(hit['unit'], '分')

        hit = self._single('从2000降到1000点')
        self.assertEqual(Decimal(hit['min']), Decimal('2000'))
        self.assertEqual(Decimal(hit['max']), Decimal('1000'))
        self.assertIn('inverted_range', hit['notes'])

    def test_up_to_standalone_is_open_upper(self):
        """A standalone up to X is an upper bound, not part of a range."""
        hit = self._single('Scales up to 10,000 requests.')
        self.assertEqual(hit['kind'], 'open_upper')
        self.assertEqual(Decimal(hit['max']), Decimal('10000'))
        self.assertIsNone(hit['min'])
        self.assertEqual(hit['unit'], 'requests')

    # ------------------------------------------------------------------
    # Hostile review regressions: adjacency and mixed corpus
    # ------------------------------------------------------------------

    def test_adjacent_ranges_sharing_endpoint(self):
        """Two ranges sharing the middle number both extract."""
        hits = self._extract('5 to 10 and 10 to 20')
        self.assertEqual([(h['min'], h['max']) for h in hits],
                         [('5', '10'), ('10', '20')])

    def test_business_corpus_slice(self):
        """Representative hostile-corpus sentences extract end to end."""
        text = ('本套餐价格¥3,000-5,000元，覆盖5万-10万用户，'
                '支持-10 to -5°C冷藏，延迟不超过500ms。')
        hits = self._extract(text)
        self.assertEqual([(h['min'], h['max'], h['unit'], h['kind'])
                          for h in hits],
                         [('3000', '5000', '元', 'closed'),
                          ('50000', '100000', None, 'closed'),
                          ('-10', '-5', '°C', 'closed'),
                          (None, '500', 'ms', 'open_upper')])
        for hit in hits:
            self.assertEqual(hit['notes'], [], hit['text'])

    def test_guard_corpus_slice(self):
        """Version, phone and year guards hold on corpus sentences."""
        self.assertEqual(
            self._extract('Supports firmware v2.1-3 and later.'), [])
        self.assertEqual(
            self._extract('Operations ran 2020-2025 profitably.'), [])
        hits = self._extract('Hotline 010-88886666 is staffed 9-5.')
        self.assertEqual(len(hits), 1)
        self.assertEqual((hits[0]['min'], hits[0]['max']), ('9', '5'))


if __name__ == '__main__':
    unittest.main()
