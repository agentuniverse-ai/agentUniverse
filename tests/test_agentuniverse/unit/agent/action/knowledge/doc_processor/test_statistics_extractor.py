# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_statistics_extractor.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.statistics_extractor import StatisticsExtractor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# A mixed corpus paragraph exercising every kind at once.
MIXED_TEXT = (
    "Adoption grew to 45% of seats while churn fell to 12.5%, and the "
    "team onboarded 1,200 users across 3 million sessions; the split "
    "was 3:2 and roughly 3/4 renewed."
)


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


def _spans(extractor, text):
    """Return {(kind, text): [start, end]} spans for quick assertions."""
    return {(hit["kind"], hit["text"]): hit["span"]
            for hit in extractor._extract(text)}


class TestStatisticsExtractor(unittest.TestCase):
    """Comprehensive test suite for StatisticsExtractor."""

    def setUp(self):
        self.extractor = StatisticsExtractor()
        self.query = Query(query_str="statistics")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _hits(self, text):
        """Run extraction and return the hit list."""
        return self.extractor._extract(text)

    def _only(self, text):
        """Assert exactly one hit exists and return it."""
        hits = self._hits(text)
        self.assertEqual(len(hits), 1, f"expected one hit, got {hits!r}")
        return hits[0]

    def _kinds_texts(self, value):
        """Return the (kind, text) pairs of every hit, in order.

        Accepts either raw text or an already-extracted hit list."""
        hits = value if isinstance(value, list) else self._hits(value)
        return [(hit["kind"], hit["text"]) for hit in hits]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: cap 100, 'statistics' / 'statistics_summary' keys."""
        ex = StatisticsExtractor()
        self.assertEqual(ex.max_statistics, 100)
        self.assertEqual(ex.statistics_key, "statistics")
        self.assertEqual(ex.summary_key, "statistics_summary")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'statistics_extractor',
            'description': 'numeric claim extractor',
            'max_statistics': 7,
            'statistics_key': 'stats',
            'summary_key': 'stats_digest',
        })
        ex = StatisticsExtractor()
        ex._initialize_by_component_configer(configer)
        self.assertEqual(ex.max_statistics, 7)
        self.assertEqual(ex.statistics_key, "stats")
        self.assertEqual(ex.summary_key, "stats_digest")
        self.assertEqual(ex.name, "statistics_extractor")
        self.assertEqual(ex.description, "numeric claim extractor")

    def test_invalid_configuration_raises(self):
        """Non-integer / too-small caps and non-string keys fail eagerly."""
        base = {
            'name': 'e', 'description': 'd',
            'max_statistics': 10, 'statistics_key': 'statistics',
            'summary_key': 'statistics_summary',
        }
        for key, value in (
            ('max_statistics', 0),
            ('max_statistics', -3),
            ('max_statistics', 2.5),
            ('max_statistics', True),
            ('statistics_key', 5),
            ('summary_key', ['x']),
            ('summary_key', None if False else {'a': 1}),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                StatisticsExtractor()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Percentage extraction ==========

    def test_percentage_sign_forms(self):
        """45%, 12.5%, 45.0% and the full-width 45％ all parse; integral
        values normalize to int."""
        cases = [
            ("Growth hit 45% of seats", 45, "45%"),
            ("churn fell to 12.5% overall", 12.5, "12.5%"),
            ("full-width 45％ usage", 45, "45％"),
            ("a hefty 45.0% margin", 45, "45.0%"),
            ("spaced 45 % of total", 45, "45 %"),
        ]
        for text, value, matched in cases:
            with self.subTest(text=text):
                hit = self._only(text)
                self.assertEqual(hit["kind"], "percentage")
                self.assertEqual(hit["value"], value)
                self.assertEqual(hit["unit"], "%")
                self.assertEqual(hit["text"], matched)

    def test_percentage_word_forms(self):
        """45.3 percent / 45 per cent / case-insensitive PERCENT."""
        cases = [
            ("about 45.3 percent of seats", 45.3, "45.3 percent"),
            ("roughly 45 per cent agreed", 45, "45 per cent"),
            ("some 12 PERCENT replied", 12, "12 PERCENT"),
        ]
        for text, value, matched in cases:
            with self.subTest(text=text):
                hit = self._only(text)
                self.assertEqual(hit["kind"], "percentage")
                self.assertEqual(hit["value"], value)
                self.assertEqual(hit["text"], matched)

    def test_percentage_cjk_forms(self):
        """Basic 百分之 numerals: 四十五->45, 十->10, 百->100, 三点五->3.5,
        plus Arabic digits after 百分之."""
        cases = [
            ("百分之四十五的用户", 45, "百分之四十五"),
            ("误差百分之三点五以内", 3.5, "百分之三点五"),
            ("百分之百通过", 100, "百分之百"),
            ("流失率百分之十", 10, "百分之十"),
            ("外部占比百分之二十三", 23, "百分之二十三"),
            ("约百分之0.5的偏差", 0.5, "百分之0.5"),
            ("命中率百分之65", 65, "百分之65"),
        ]
        for text, value, matched in cases:
            with self.subTest(text=text):
                hit = self._only(text)
                self.assertEqual(hit["kind"], "percentage")
                self.assertEqual(hit["value"], value)
                self.assertEqual(hit["text"], matched)

    def test_parse_cjk_numeral_unit_math(self):
        """Direct arithmetic checks for the CJK numeral parser."""
        parse = StatisticsExtractor._parse_cjk_numeral
        self.assertEqual(parse("四十五"), 45.0)
        self.assertEqual(parse("十"), 10.0)
        self.assertEqual(parse("二十"), 20.0)
        self.assertEqual(parse("一百二十三"), 123.0)
        self.assertEqual(parse("百"), 100.0)
        self.assertEqual(parse("三点五"), 3.5)
        self.assertEqual(parse("零"), 0.0)
        self.assertIsNone(parse(""))

    # ========== Count extraction ==========

    def test_count_plain_units(self):
        """1,200 users — separators dropped, unit word captured."""
        cases = [
            ("we onboarded 1,200 users", 1200, "users", "1,200 users"),
            ("logged 999 items today", 999, "items", "999 items"),
            ("ran 42 kilometers", 42, "kilometers", "42 kilometers"),
        ]
        for text, value, unit, matched in cases:
            with self.subTest(text=text):
                hit = self._only(text)
                self.assertEqual(hit["kind"], "count")
                self.assertEqual(hit["value"], value)
                self.assertEqual(hit["unit"], unit)
                self.assertEqual(hit["text"], matched)

    def test_count_english_multipliers_resolved(self):
        """3 million items -> 3000000; 7 billion (no unit) -> 7000000000
        with an empty unit."""
        cases = [
            ("shipped 3 million items", 3000000, "items"),
            ("about 7 billion people", 7000000000, "people"),
            ("saw 2 thousand orders", 2000, "orders"),
            ("counted 5 hundred birds", 500, "birds"),
            ("lost 1.2 trillion dollars", 1200000000000, "dollars"),
        ]
        for text, value, unit in cases:
            with self.subTest(text=text):
                hit = self._only(text)
                self.assertEqual(hit["value"], value)
                self.assertEqual(hit["unit"], unit)
        hit = self._only("a crowd of 7 billion")
        self.assertEqual(hit["value"], 7000000000)
        self.assertEqual(hit["unit"], "")

    def test_count_cjk_multipliers_resolved(self):
        """5万次 -> 50000 unit 次; 1.5亿人 -> 150000000 unit 人; the
        multiplier is folded into value, never left as the unit."""
        cases = [
            ("缓存命中5万次", 50000, "次"),
            ("服务1.5亿人", 150000000, "人"),
            ("下载量3.5万", 35000, ""),
            ("预算3万亿日元", 3000000000000, "日元"),
            ("充值5元话费", 5, "元话费"),
        ]
        for text, value, unit in cases:
            with self.subTest(text=text):
                hit = self._only(text)
                self.assertEqual(hit["kind"], "count")
                self.assertEqual(hit["value"], value)
                self.assertEqual(hit["unit"], unit)

    def test_count_cjk_fused_and_plain(self):
        """5次 (no space) and 45 次 (spaced) both count with unit 次."""
        for text in ("点击5次", "clicked 45 次 daily"):
            with self.subTest(text=text):
                hits = [h for h in self._hits(text)
                        if h["kind"] == "count" and h["unit"] == "次"]
                self.assertEqual(len(hits), 1)
                self.assertIn(hits[0]["value"], (5, 45))

    def test_count_rejects_function_and_calendar_words(self):
        """Numbers followed by function words or month/weekday names are
        not counts — "3 of the users", "3 May", "12 and rising" yield
        no count hit at all."""
        for text in ("3 of the users left",
                     "on 3 May we shipped",
                     "about 12 and rising",
                     "seen 90 percent wide"):
            with self.subTest(text=text):
                for hit in self._hits(text):
                    if hit["kind"] == "count":
                        self.assertNotIn(
                            hit["unit"],
                            ("of", "the", "May", "and", "percent", "wide"))

    def test_count_no_fused_english_suffix(self):
        """"1st" never parses as unit "st": no space, no count."""
        hits = [h for h in self._hits("her 21st visit")
                if h["kind"] == "count"]
        self.assertEqual(hits, [])

    # ========== Ratio extraction ==========

    def test_ratio_colon_forms(self):
        """3:2 -> 1.5; 16:9 -> 16/9; full-width colon 3：2 -> 1.5."""
        hit = self._only("the ratio is 3:2 today")
        self.assertEqual(hit["kind"], "ratio")
        self.assertEqual(hit["value"], 1.5)
        self.assertEqual(hit["text"], "3:2")
        self.assertEqual(hit["unit"], "")

        hit = self._only("a 16:9 panel")
        self.assertEqual(hit["value"], 16 / 9)
        self.assertEqual(hit["text"], "16:9")

        hit = self._only("宽高比3：2")
        self.assertEqual(hit["value"], 1.5)
        self.assertEqual(hit["text"], "3：2")

    def test_ratio_slash_forms(self):
        """3/4 -> 0.75 and 50/50 -> 1 (integral quotient normalizes to
        int); both survive the date guard because neither reads as
        month/day (both parts <= 12 or first part > 12)."""
        hit = self._only("roughly 3/4 renewed")
        self.assertEqual(hit["kind"], "ratio")
        self.assertEqual(hit["value"], 0.75)
        self.assertEqual(hit["text"], "3/4")

        hit = self._only("they split costs 50/50")
        self.assertEqual(hit["value"], 1)
        self.assertIsInstance(hit["value"], int)

    def test_ratio_clock_times_excluded(self):
        """10:05 (leading-zero minute), 10:30 am and at 10:30 are clock
        times, not ratios — and their right halves never leak out as
        counts either."""
        for text in ("meet at 10:05 sharp",
                     "the call is 10:30 am",
                     "see you 10:30 p.m.",
                     "dial in at 10:30"):
            with self.subTest(text=text):
                self.assertEqual(self._hits(text), [])

    def test_ratio_slash_dates_excluded(self):
        """Month/day shapes (a <= 12, 13 <= b <= 31) read as dates:
        10/19 and 11/30 drop while 3/4, 45/60 and 12/12 survive."""
        for text in ("it happened on 10/19 last", "due 11/30 sharp"):
            with self.subTest(text=text):
                self.assertEqual(
                    [h for h in self._hits(text) if h["kind"] == "ratio"],
                    [])
        for text, expected in (("kept 3/4 here", "3/4"),
                               ("rate 45/60 now", "45/60"),
                               ("an even 12/12 split", "12/12")):
            with self.subTest(text=text):
                ratios = [h for h in self._hits(text)
                          if h["kind"] == "ratio"]
                self.assertEqual(len(ratios), 1)
                self.assertEqual(ratios[0]["text"], expected)

    def test_ratio_full_dates_and_chains_excluded(self):
        """2026-10-19, 2026/10/19, 10/19/2026 and slash chains (a/3/4)
        yield no ratio hits at all."""
        for text in ("released on 2026-10-19 globally",
                     "published 2026/10/19 early",
                     "signed 10/19/2026 in full",
                     "path /items/3/4 shown",
                     "fetch docs/a/3/4 now"):
            with self.subTest(text=text):
                self.assertEqual(
                    [h for h in self._hits(text) if h["kind"] == "ratio"],
                    [])

    def test_ratio_url_fractions_excluded(self):
        """Slash pairs inside URLs are paths, not fractions."""
        text = "see https://example.com/a/3/4 for details"
        self.assertEqual(self._hits(text), [])
        text = "visit www.site.io/x/5/6 today"
        self.assertEqual(
            [h for h in self._hits(text) if h["kind"] == "ratio"], [])

    def test_ratio_denominator_not_double_counted(self):
        """"3/4 preferred it" keeps the ratio but never emits a phantom
        count "4 preferred" for the denominator."""
        hits = self._hits("about 3/4 preferred it loud")
        self.assertEqual(self._kinds_texts(hits), [("ratio", "3/4")])

    def test_ratio_zero_denominator_excluded(self):
        """3/0 and 5:0 never divide by zero; they are dropped."""
        self.assertEqual(self._hits("a weird 3/0 case"), [])
        self.assertEqual(self._hits("an odd 5:0 score"), [])

    # ========== Raw number extraction ==========

    def test_raw_number_forms(self):
        """Comma-grouped bare numbers parse with separators dropped;
        the >= 1000 cap holds by construction (1,000 is the floor).
        Contexts use function words after the number so the count kind
        does not claim a unit."""
        cases = [
            ("revenue reached 1,234,567 in total", 1234567, "1,234,567"),
            ("a floor of 1,000 at most", 1000, "1,000"),
            ("precise 2,000,000.5 or so", 2000000.5, "2,000,000.5"),
        ]
        for text, value, matched in cases:
            with self.subTest(text=text):
                hit = self._only(text)
                self.assertEqual(hit["kind"], "raw_number")
                self.assertEqual(hit["value"], value)
                self.assertEqual(hit["unit"], "")
                self.assertEqual(hit["text"], matched)

    def test_raw_number_noise_excluded(self):
        """Small bare numbers, invalid groupings and ordinals with
        separators never become raw numbers."""
        for text in ("only 999 items", "plain 42 here",
                     "odd 12,34 grouping", "the 1,000th visitor"):
            with self.subTest(text=text):
                self.assertEqual(
                    [h for h in self._hits(text)
                     if h["kind"] == "raw_number"], [])

    def test_count_wins_over_raw_number_on_overlap(self):
        """"1,200 users" yields exactly one hit — the count — and never
        a duplicate raw number for the same digits."""
        hits = self._hits("we onboarded 1,200 users")
        self.assertEqual(self._kinds_texts(hits), [("count", "1,200 users")])
        hits = self._hits("shipped 1,234,567 units total")
        self.assertEqual(self._kinds_texts(hits),
                         [("count", "1,234,567 units")])

    # ========== Guard batteries ==========

    def test_dates_versions_ordinals_excluded(self):
        """The canonical false positives produce no hits of any kind."""
        guarded = [
            "released on 2026-10-19",
            "build v1.2.3 is green",
            "version 1.2.3 shipped",
            "host 192.168.1.1 replied",
            "her 21st attempt",
            "the 2nd of May",
            "his 103rd try",
            "released 2026年10月19日",
            "in 2026年 we grew",
            "during 10月 only",
            "by 5日 it closed",
        ]
        for text in guarded:
            with self.subTest(text=text):
                self.assertEqual(self._hits(text), [])

    def test_cjk_calendar_fragments_still_allow_real_counts(self):
        """Calendar guards reject 2026年/10月/5日 but keep genuine counts
        like 5年 (5 years) and 3个月 (3 months)."""
        text = "2026年10月19日发布，持续5年，共3个月"
        self.assertEqual(self._kinds_texts(self._hits(text)),
                         [("count", "5年"), ("count", "3个月")])

    def test_cjk_percentage_not_shadowed_by_count(self):
        """百分之四十五 is one percentage hit, not a count on 五."""
        self.assertEqual(self._kinds_texts(self._hits("百分之四十五通过")),
                         [("percentage", "百分之四十五")])

    # ========== Span correctness ==========

    def test_spans_slice_back_to_matched_text(self):
        """For every hit in mixed texts, text[start:end] == hit text —
        including full-width and CJK characters."""
        for text in (MIXED_TEXT,
                     "缓存命中5万次，服务1.5亿人，占比百分之四十五",
                     "mixed 45％ and 3：2 ratios",
                     "see 1,234,567 and v1.2.3 on 2026-10-19"):
            with self.subTest(text=text):
                for hit in self._hits(text):
                    start, end = hit["span"]
                    self.assertEqual(text[start:end], hit["text"])

    def test_hits_are_in_document_order(self):
        """Hits come back sorted by span start."""
        starts = [hit["span"][0] for hit in self._hits(MIXED_TEXT)]
        self.assertEqual(starts, sorted(starts))

    # ========== Pipeline behavior ==========

    def test_mixed_text_full_ground_truth(self):
        """The MIXED_TEXT paragraph yields exactly these six hits with
        these values, in order."""
        hits = self._hits(MIXED_TEXT)
        ground_truth = [
            ("percentage", 45, "%", "45%"),
            ("percentage", 12.5, "%", "12.5%"),
            ("count", 1200, "users", "1,200 users"),
            ("count", 3000000, "sessions", "3 million sessions"),
            ("ratio", 1.5, "", "3:2"),
            ("ratio", 0.75, "", "3/4"),
        ]
        self.assertEqual([(h["kind"], h["value"], h["unit"], h["text"])
                          for h in hits], ground_truth)

    def test_metadata_statistics_and_summary_stamped(self):
        """Both metadata keys appear; existing metadata survives; text
        and id are untouched."""
        text = "45% of 1,200 users with a 3:2 split"
        doc = _doc(text, source="report", rank=3)
        doc_id = doc.id
        result = self.extractor.process_docs([doc], self.query)

        self.assertEqual(len(result), 1)
        self.assertIs(result[0], doc)
        self.assertEqual(doc.text, text)
        self.assertEqual(doc.id, doc_id)
        self.assertEqual(doc.metadata["source"], "report")
        self.assertEqual(doc.metadata["rank"], 3)

        stats = doc.metadata["statistics"]
        self.assertEqual([h["kind"] for h in stats],
                         ["percentage", "count", "ratio"])
        summary = doc.metadata["statistics_summary"]
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["counts"],
                         {"count": 1, "percentage": 1, "ratio": 1})
        self.assertEqual(summary["min"], {"count": 1200,
                                          "percentage": 45, "ratio": 1.5})
        self.assertEqual(summary["max"], {"count": 1200,
                                          "percentage": 45, "ratio": 1.5})

    def test_summary_min_max_arithmetic(self):
        """min/max per kind track the extremes across several hits."""
        doc = _doc("12.5% then 45% then 3.2%, with 10 users and 900 users")
        self.extractor.process_docs([doc], self.query)
        summary = doc.metadata["statistics_summary"]
        self.assertEqual(summary["total"], 5)
        self.assertEqual(summary["counts"], {"count": 2,
                                             "percentage": 3})
        self.assertEqual(summary["min"]["percentage"], 3.2)
        self.assertEqual(summary["max"]["percentage"], 45)
        self.assertEqual(summary["min"]["count"], 10)
        self.assertEqual(summary["max"]["count"], 900)

    def test_metadata_written_through_copy(self):
        """Stamping writes through a copied mapping: the caller's
        original dict never gains the new keys in place."""
        doc = _doc("grew 45% fast", source="wire")
        original = doc.metadata
        self.extractor.process_docs([doc], self.query)
        self.assertNotIn("statistics", original)
        self.assertNotIn("statistics_summary", original)
        self.assertIsNot(doc.metadata, original)
        self.assertEqual(original, {"source": "wire"})

    def test_no_statistics_passthrough(self):
        """Documents without numeric claims keep their metadata object
        entirely untouched — no keys stamped, same mapping."""
        doc = _doc("nothing numeric in this note", source="memo")
        original = doc.metadata
        result = self.extractor.process_docs([doc], self.query)
        self.assertIs(result[0], doc)
        self.assertIs(doc.metadata, original)
        self.assertNotIn("statistics", doc.metadata)
        self.assertNotIn("statistics_summary", doc.metadata)

    def test_disabled_keys_stamp_nothing(self):
        """Empty statistics_key / summary_key disable both stamps while
        extraction still runs (no error)."""
        self.extractor.statistics_key = ""
        self.extractor.summary_key = ""
        doc = _doc("grew 45% fast", source="wire")
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(result), 1)
        self.assertEqual(doc.metadata, {"source": "wire"})

    def test_cap_behavior(self):
        """The statistics list truncates to max_statistics while the
        summary still counts every hit found."""
        text = " ".join(f"{value}%," for value in range(150))
        doc = _doc(text)
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(doc.metadata["statistics"]), 100)
        self.assertEqual(doc.metadata["statistics_summary"]["total"], 150)
        self.assertEqual(
            doc.metadata["statistics_summary"]["counts"]["percentage"], 150)

        capped = StatisticsExtractor()
        capped.max_statistics = 3
        doc2 = _doc(text)
        capped.process_docs([doc2], self.query)
        self.assertEqual(len(doc2.metadata["statistics"]), 3)
        self.assertEqual(doc2.metadata["statistics_summary"]["total"], 150)

    def test_cap_keeps_first_hits_in_document_order(self):
        """Truncation keeps the earliest hits, not a later slice."""
        capped = StatisticsExtractor()
        capped.max_statistics = 2
        doc = _doc("10% then 20% then 30%")
        capped.process_docs([doc], self.query)
        self.assertEqual([h["value"] for h in doc.metadata["statistics"]],
                         [10, 20])

    def test_batch_documents_processed_independently(self):
        """Each document gets its own hits; order and ids are stable."""
        doc_a = _doc("grew 45%", tag="a")
        doc_b = _doc("1,234,567 in total", tag="b")
        doc_c = _doc("plain prose", tag="c")
        ids = [d.id for d in (doc_a, doc_b, doc_c)]
        result = self.extractor.process_docs([doc_a, doc_b, doc_c],
                                             self.query)
        self.assertEqual([d.metadata["tag"] for d in result],
                         ["a", "b", "c"])
        self.assertEqual([d.id for d in result], ids)
        self.assertEqual([h["kind"] for h in doc_a.metadata["statistics"]],
                         ["percentage"])
        self.assertEqual([h["kind"] for h in doc_b.metadata["statistics"]],
                         ["raw_number"])
        self.assertNotIn("statistics", doc_c.metadata)

    def test_empty_and_degenerate_inputs(self):
        """Empty batch -> []; empty / blank / None text -> no hits."""
        self.assertEqual(self.extractor.process_docs([], self.query), [])
        self.assertEqual(self._hits(""), [])
        self.assertEqual(self._hits("   "), [])
        self.assertEqual(self._hits(None), [])
        doc = _doc("")
        self.extractor.process_docs([doc], self.query)
        self.assertNotIn("statistics", doc.metadata or {})

    def test_multiplier_arithmetic_is_exact(self):
        """Magnitude scaling is exact Decimal arithmetic: two-decimal
        inputs that float multiplication would knock an ulp off
        ("1.13万" -> 11299.999999999998) come out as clean ints."""
        cases = [
            ("增长1.13万倍", 11300),
            ("增速1.09亿", 109000000),
            ("规模1.11万亿", 1110000000000),
            ("成本2.15亿", 215000000),
            ("下载3.5万", 35000),
            ("about 2.01 million items", 2010000),
            ("some 1.07 billion items", 1070000000),
            ("roughly 2.03 thousand items", 2030),
            ("nearly 1.11 trillion items", 1110000000000),
        ]
        for text, value in cases:
            with self.subTest(text=text):
                hit = self._only(text)
                self.assertEqual(hit["value"], value)
                self.assertIsInstance(hit["value"], int)

    def test_scaled_number_helper(self):
        """_scaled_number: exact ints for integral products, floats for
        fractional ones, comma separators dropped."""
        scaled = StatisticsExtractor._scaled_number
        self.assertEqual(scaled("1.13", 10000), 11300)
        self.assertIsInstance(scaled("1.13", 10000), int)
        self.assertEqual(scaled("1.23456", 10000), 12345.6)
        self.assertEqual(scaled("2,000", 1000000), 2000000000)
        self.assertEqual(scaled("0.5", 1000), 500)

    def test_multiplier_function_word_not_a_unit(self):
        """"5 billion in cash": a function word after the magnitude word
        is not a unit — the hit trims back to "5 billion" with unit ""."""
        for text, matched in (("5 billion in cash", "5 billion"),
                              ("3 million are active", "3 million"),
                              ("2 million of these", "2 million"),
                              ("7 thousand was paid", "7 thousand")):
            with self.subTest(text=text):
                hit = self._only(text)
                self.assertEqual(hit["kind"], "count")
                self.assertEqual(hit["unit"], "")
                self.assertEqual(hit["text"], matched)

    def test_calendar_fragment_must_head_its_number(self):
        """1,000日元 / 1,500月产能 extract as counts: the guard only
        fires when the 月/日 fragment heads its own number, while bare
        fragments (during 10月) stay guarded."""
        cases = [
            ("票价1,000日元", 1000, "日元"),
            ("每1,500月产能提升", 1500, "月产能提升"),
        ]
        for text, value, unit in cases:
            with self.subTest(text=text):
                hit = self._only(text)
                self.assertEqual(hit["kind"], "count")
                self.assertEqual(hit["value"], value)
                self.assertEqual(hit["unit"], unit)
        self.assertEqual(self._hits("during 10月 only"), [])
        self.assertEqual(self._hits("by 5日 it closed"), [])
        self.assertEqual(
            self._kinds_texts("2026年10月19日发布，持续5年"),
            [("count", "5年")])

    def test_hms_clock_and_iso_datetime_excluded(self):
        """10:30:45 / 12:34:56 / 2026-10-19T10:30 are clock readings,
        not ratios; a 1:2:4 mix chain with one-digit middles still
        parses."""
        for text in ("log 12:34:56", "10:30:45 sharp",
                     "Meeting 2026-10-19T10:30:00Z",
                     "at 2026-10-19T10:30"):
            with self.subTest(text=text):
                self.assertEqual(
                    [h for h in self._hits(text) if h["kind"] == "ratio"],
                    [])
        self.assertEqual(self._kinds_texts("mix 1:2:4 by weight"),
                         [("ratio", "1:2")])
        self.assertEqual(self._kinds_texts("aspect 16:9"), [("ratio", "16:9")])

    def test_slash_year_month_excluded(self):
        """2026/10 reads as October 2026, not a ratio of 202.6; a
        2016/17 season span and a 1920/1080 resolution survive."""
        self.assertEqual(
            [h for h in self._hits("in 2026/10 we grew") if h["kind"] == "ratio"],
            [])
        self.assertEqual(
            [h for h in self._hits("the 2026/3 report") if h["kind"] == "ratio"],
            [])
        ratios = [h for h in self._hits("the 2016/17 season")
                  if h["kind"] == "ratio"]
        self.assertEqual(len(ratios), 1)
        ratios = [h for h in self._hits("screen 1920/1080 ok")
                  if h["kind"] == "ratio"]
        self.assertEqual(len(ratios), 1)

    def test_percent_cjk_sectioned_numerals(self):
        """百分之三万 -> 30000 and 百分之三百万 -> 3000000: the 万/亿
        section characters parse inside CJK percentages too."""
        cases = [
            ("百分之三万", 30000),
            ("百分之三百万", 3000000),
            ("百分之四十五", 45),
        ]
        for text, value in cases:
            with self.subTest(text=text):
                hit = self._only(text)
                self.assertEqual(hit["kind"], "percentage")
                self.assertEqual(hit["value"], value)

    def test_determinism(self):
        """The same text always yields the identical hit list, across
        fresh extractor instances too."""
        first = self._hits(MIXED_TEXT)
        second = self._hits(MIXED_TEXT)
        self.assertEqual(first, second)
        other = StatisticsExtractor()._extract(MIXED_TEXT)
        self.assertEqual(first, other)

    def test_query_is_ignored(self):
        """Processing is identical with and without a query object."""
        doc_a = _doc(MIXED_TEXT)
        doc_b = _doc(MIXED_TEXT)
        self.extractor.process_docs([doc_a], self.query)
        self.extractor.process_docs([doc_b], None)
        self.assertEqual(doc_a.metadata["statistics"],
                         doc_b.metadata["statistics"])


if __name__ == '__main__':
    unittest.main()
