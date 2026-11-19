# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_number_conflict_detector.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.number_conflict_detector import NumberConflictDetector
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestNumberConflictDetector(unittest.TestCase):
    """Comprehensive offline test suite for NumberConflictDetector."""

    def setUp(self):
        self.detector = NumberConflictDetector()
        self.query = Query(query_str="number conflicts")

    # ------------------------------------------------------------- #
    # Helpers
    # ------------------------------------------------------------- #

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _process(self, text):
        """Run the detector on one text and return the metadata stamped."""
        doc = Document(text=text)
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(len(result), 1)
        return result[0].metadata

    def _conflicts(self, text):
        """Return the conflict list for one text."""
        return self._process(text)["number_conflicts"]

    def _one(self, text):
        """Assert exactly one conflict exists and return it."""
        conflicts = self._conflicts(text)
        self.assertEqual(len(conflicts), 1,
                         f"expected one conflict, got {conflicts!r}")
        return conflicts[0]

    def _values(self, text):
        """Return the (anchor, dimension, [values]) of the single conflict."""
        conflict = self._one(text)
        return (conflict["anchor"], conflict["dimension"],
                [v["value"] for v in conflict["values"]])

    # ========== Initialization and configuration ==========

    def test_default_configuration(self):
        """Defaults: window 3, cap 20, exact tolerance with 0.1% ratio."""
        detector = NumberConflictDetector()
        self.assertEqual(detector.window_size, 3)
        self.assertEqual(detector.max_conflicts, 20)
        self.assertEqual(detector.tolerance, 0)
        self.assertEqual(detector.near_conflict_ratio, 0.001)
        self.assertEqual(detector.conflicts_key, "number_conflicts")
        self.assertEqual(detector.count_key, "conflict_count")
        self.assertEqual(detector.consistency_key, "numeric_consistency")
        self.assertEqual(detector.repeats_key, "consistent_repeats")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'number_conflict_detector',
            'description': 'number conflict detector',
            'window_size': 5,
            'max_conflicts': 3,
            'tolerance': 0.5,
            'near_conflict_ratio': 0.01,
            'conflicts_key': 'conflicts',
            'count_key': 'n_conflicts',
            'consistency_key': 'verdict',
            'repeats_key': 'repeats',
        })
        detector = NumberConflictDetector()
        detector._initialize_by_component_configer(configer)
        self.assertEqual(detector.window_size, 5)
        self.assertEqual(detector.max_conflicts, 3)
        self.assertEqual(detector.tolerance, 0.5)
        self.assertEqual(detector.near_conflict_ratio, 0.01)
        self.assertEqual(detector.conflicts_key, "conflicts")
        self.assertEqual(detector.count_key, "n_conflicts")
        self.assertEqual(detector.consistency_key, "verdict")
        self.assertEqual(detector.repeats_key, "repeats")
        self.assertEqual(detector.name, "number_conflict_detector")
        self.assertEqual(detector.description, "number conflict detector")

    def test_invalid_configuration_raises(self):
        """Bad window, cap, tolerances and keys fail eagerly."""
        base = {
            'name': 'd', 'description': 'd',
            'window_size': 3, 'max_conflicts': 10,
            'tolerance': 0, 'near_conflict_ratio': 0.001,
            'conflicts_key': 'number_conflicts',
            'count_key': 'conflict_count',
            'consistency_key': 'numeric_consistency',
            'repeats_key': 'consistent_repeats',
        }
        cases = (
            ('window_size', 0), ('window_size', 6), ('window_size', 2.5),
            ('window_size', True),
            ('max_conflicts', 0), ('max_conflicts', -1),
            ('max_conflicts', 2.5), ('max_conflicts', True),
            ('tolerance', -1), ('tolerance', "0"),
            ('near_conflict_ratio', -0.1), ('near_conflict_ratio', "x"),
            ('near_conflict_ratio', {'a': 1}),
            ('conflicts_key', 5), ('count_key', None if False else 7),
            ('consistency_key', ['x']), ('repeats_key', {'a': 1}),
        )
        for key, value in cases:
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                NumberConflictDetector()._initialize_by_component_configer(
                    self._create_configer(config))

    def test_valid_boundary_configuration(self):
        """Boundary values pass: window 1 and 5, tolerance 0 int/float."""
        for window in (1, 5):
            configer = self._create_configer(
                {'name': 'd', 'description': 'd', 'window_size': window})
            detector = NumberConflictDetector()
            detector._initialize_by_component_configer(configer)
            self.assertEqual(detector.window_size, window)
        for tolerance in (0, 0.5, 1):
            configer = self._create_configer(
                {'name': 'd', 'description': 'd', 'tolerance': tolerance})
            detector = NumberConflictDetector()
            detector._initialize_by_component_configer(configer)
            self.assertEqual(detector.tolerance, tolerance)

    # ========== English conflict ground truths ==========

    def test_en_revenue_conflict(self):
        """"revenue was 5 million" vs "revenue reached 6 million" —
        the canonical example: same anchor, different numbers."""
        anchor, dimension, values = self._values(
            "Revenue was 5 million in the first quarter. "
            "Revenue reached 6 million in the same quarter.")
        self.assertEqual(anchor, "revenue")
        self.assertEqual(dimension, "amount")
        self.assertEqual(values, [5000000, 6000000])

    def test_en_revenue_conflict_record_shape(self):
        """The conflict record carries texts, spans, sentence indices
        and the relative gap 1M/6M = 0.166667."""
        conflict = self._one(
            "Revenue was 5 million. Revenue reached 6 million.")
        self.assertEqual(conflict["anchor"], "revenue")
        self.assertEqual(conflict["relative_gap"], 0.166667)
        texts = [v["text"] for v in conflict["values"]]
        self.assertEqual(texts, ["5 million", "6 million"])
        indices = [v["sentence_index"] for v in conflict["values"]]
        self.assertEqual(indices, [0, 1])
        for value in conflict["values"]:
            start, end = value["span"]
            self.assertEqual(
                "Revenue was 5 million. Revenue reached 6 million."
                [start:end], value["text"])

    def test_en_users_conflict_via_unit_anchor(self):
        """Unit words anchor the claim: "onboarded 1,200 users" vs
        "added 1,500 users" both anchor on the unit "user"."""
        anchor, dimension, values = self._values(
            "The team onboarded 1,200 users. The team added 1,500 users.")
        self.assertEqual(anchor, "user")
        self.assertEqual(dimension, "amount")
        self.assertEqual(values, [1200, 1500])

    def test_en_cost_conflict(self):
        """Cost claims conflict across 万 and bare forms: "cost was 5万"
        vs "cost reached 60000"."""
        anchor, dimension, values = self._values(
            "Production cost was 5万. Production cost reached 60000.")
        self.assertEqual(anchor, "cost")
        self.assertEqual(dimension, "amount")
        self.assertEqual(values, [50000, 60000])

    def test_en_conflict_verdict_and_count_metadata(self):
        """Conflicts stamp count, verdict and zero repeats together."""
        meta = self._process(
            "Revenue was 5 million. Revenue reached 6 million.")
        self.assertEqual(meta["conflict_count"], 1)
        self.assertEqual(meta["numeric_consistency"], "conflicts_found")
        self.assertEqual(meta["consistent_repeats"], 0)

    def test_en_different_anchors_do_not_conflict(self):
        """Different subjects with different numbers are not conflicts."""
        meta = self._process(
            "Revenue was 5 million. The headcount grew to 6,000 staff "
            "that year.")
        self.assertEqual(meta["number_conflicts"], [])
        self.assertEqual(meta["numeric_consistency"], "consistent")

    def test_en_stemming_aligns_singular_and_plural(self):
        """"1,200 users" vs "1,500 user accounts" still anchor alike
        (light stem user) — plural drift does not split the group."""
        anchor, _, values = self._values(
            "The tool serves 1,200 users. The tool serves 1,500 user "
            "accounts.")
        self.assertEqual(anchor, "user")
        self.assertEqual(values, [1200, 1500])

    # ========== 万 / 亿 normalization ==========

    def test_wan_yi_equal_after_normalization_not_conflict(self):
        """5万 vs 50000: equal after normalization, so a consistent
        repeat — not a conflict."""
        meta = self._process("用户数达到5万，用户数突破50000。")
        self.assertEqual(meta["number_conflicts"], [])
        self.assertEqual(meta["conflict_count"], 0)
        self.assertEqual(meta["numeric_consistency"], "consistent")
        self.assertEqual(meta["consistent_repeats"], 1)

    def test_wan_conflict_when_values_differ(self):
        """5万 vs 60000 under the same anchor disagree after exact
        Decimal normalization."""
        anchor, dimension, values = self._values(
            "用户数达到5万，用户数突破60000。")
        self.assertEqual(anchor, "用户数")
        self.assertEqual(dimension, "amount")
        self.assertEqual(values, [50000, 60000])

    def test_yi_decimal_scaling_exact(self):
        """1.13亿 scales to exactly 113000000 (Decimal, no float ulp):
        the repeat stays consistent and the wider gap conflicts."""
        meta = self._process(
            "营收约为1.13亿，营收达到113000000。")
        self.assertEqual(meta["number_conflicts"], [])
        self.assertEqual(meta["consistent_repeats"], 1)

        anchor, _, values = self._values(
            "营收约为1.13亿，营收达到120000000。")
        self.assertEqual(anchor, "营收")
        self.assertEqual(values, [113000000, 120000000])

    def test_en_million_scaling_normalization(self):
        """3 million vs 3000000 is a consistent repeat, not a
        conflict."""
        meta = self._process(
            "Revenue reached 3 million dollars. Later files state "
            "revenue reached 3000000 dollars.")
        self.assertEqual(meta["number_conflicts"], [])
        self.assertEqual(meta["consistent_repeats"], 1)

    # ========== CJK conflicts ==========

    def test_cjk_conflict_parallel_phrasing(self):
        """营收为5万 vs 营收达到6万: tail-strip (为/达到) aligns the
        anchors and the values conflict."""
        anchor, dimension, values = self._values("营收为5万，营收达到6万。")
        self.assertEqual(anchor, "营收")
        self.assertEqual(dimension, "amount")
        self.assertEqual(values, [50000, 60000])

    def test_cjk_conflict_with_head_prefix(self):
        """Time-prefixed subjects reduce to the same anchor: 2024年营收
        vs 2024年10月营收 both anchor 营收."""
        anchor, _, values = self._values(
            "2024年营收5万。2024年10月营收达到6万。")
        self.assertEqual(anchor, "营收")
        self.assertEqual(values, [50000, 60000])

    def test_cjk_conflict_with_unit_anchor(self):
        """Unit-anchored claims: 5万元 vs 6万元 anchor on 元."""
        anchor, _, values = self._values("年费为5万元，次年年费涨到6万元。")
        self.assertEqual(anchor, "元")
        self.assertEqual(values, [50000, 60000])

    def test_cjk_short_word_protected_from_head_strip(self):
        """日活 (2 chars) survives head-stripping as an anchor."""
        anchor, _, values = self._values("日活达到5万，日活突破6万。")
        self.assertEqual(anchor, "日活")
        self.assertEqual(values, [50000, 60000])

    # ========== Percentages ==========

    def test_percent_conflict_sign_forms(self):
        """45% vs 50% under the same anchor conflict in the percent
        dimension."""
        anchor, dimension, values = self._values(
            "Conversion rose to 45%. Conversion climbed to 50%.")
        self.assertEqual(anchor, "conversion")
        self.assertEqual(dimension, "percent")
        self.assertEqual(values, [45, 50])

    def test_percent_word_and_cjk_forms(self):
        """45 percent and 百分之六十 parse into comparable normalized
        values (word form vs CJK numeral form)."""
        anchor, dimension, values = self._values(
            "外部占比45 percent，外部占比是百分之六十。")
        self.assertEqual(anchor, "外部占比")
        self.assertEqual(dimension, "percent")
        self.assertEqual(values, [45, 60])

    def test_percent_cjk_numeral_parsing(self):
        """Direct checks for the CJK numeral parser used by 百分之."""
        parse = NumberConflictDetector._parse_cjk_numeral
        self.assertEqual(parse("四十五"), 45)
        self.assertEqual(parse("三点五"), 3.5)
        self.assertEqual(parse("百"), 100)
        self.assertEqual(parse("二十三"), 23)
        self.assertIsNone(parse(""))

    def test_percent_and_amount_not_conflated(self):
        """45% and 45 million never compare: different dimensions, no
        conflict."""
        meta = self._process(
            "Growth was 45 percent. Growth hit 45 million.")
        self.assertEqual(meta["number_conflicts"], [])
        self.assertEqual(meta["numeric_consistency"], "consistent")
        self.assertEqual(meta["consistent_repeats"], 0)

    def test_percent_consistent_repeat(self):
        """45% repeated stays consistent."""
        meta = self._process(
            "Conversion rose to 45%. A recap restated conversion at "
            "45%.")
        self.assertEqual(meta["number_conflicts"], [])
        self.assertEqual(meta["consistent_repeats"], 1)

    # ========== Guards: dates, years, ordinals, versions, URLs ==========

    def test_year_context_guard(self):
        """in 2024 / in 2023 are years, not claims: only the revenue
        figures conflict."""
        conflict = self._one(
            "In 2024 the revenue was 5 million. A year earlier, in "
            "2023, revenue was 4 million.")
        self.assertEqual(conflict["anchor"], "revenue")
        self.assertEqual([v["value"] for v in conflict["values"]],
                         [5000000, 4000000])

    def test_year_word_and_fiscal_guard(self):
        """FY2024 / 2024 fiscal year stay out of the values; the sales
        figures conflict on their own."""
        conflict = self._one(
            "FY2024 sales hit 3 million. The 2024 fiscal year saw "
            "sales reach 4 million.")
        self.assertEqual(conflict["anchor"], "sale")
        self.assertEqual([v["value"] for v in conflict["values"]],
                         [3000000, 4000000])

    def test_cjk_calendar_guard(self):
        """2024年 / 2024年10月 fragments are calendar spans and never
        become values."""
        meta = self._process("2024年营收5万。2024年10月会议召开。")
        self.assertEqual(meta["conflict_count"], 0)
        meta = self._process("成立于1999年，1999年正式上线。")
        self.assertEqual(meta["conflict_count"], 0)
        self.assertEqual(meta["numeric_consistency"], "consistent")

    def test_iso_date_guard(self):
        """ISO and US dates are guarded out entirely."""
        meta = self._process(
            "Released 2024-10-19 with v1.2.3. Q4 shipped 10/19/2024.")
        self.assertEqual(meta["number_conflicts"], [])
        self.assertEqual(meta["numeric_consistency"], "consistent")

    def test_ordinal_guard(self):
        """21st / 1,000th / 第3 ordinals never become values: repeated
        3rd place is not a numeric conflict."""
        meta = self._process(
            "The 1st batch held 3rd place. The 2nd batch also finished "
            "3rd.")
        self.assertEqual(meta["number_conflicts"], [])
        meta = self._process("第3版与第5版内容一致。")
        self.assertEqual(meta["conflict_count"], 0)

    def test_url_guard(self):
        """Numbers inside URLs are paths, not claims."""
        meta = self._process(
            "See https://example.com/a/50000/b and www.site.cn/60000 "
            "for the archive.")
        self.assertEqual(meta["number_conflicts"], [])

    def test_version_and_multidot_guard(self):
        """v1.2.3 / 1.2.3 / IPs are guarded out."""
        meta = self._process(
            "Upgraded to v1.2.3 from 1.2.3 at 10.0.0.1 today.")
        self.assertEqual(meta["number_conflicts"], [])

    def test_multiplier_suffix_guard(self):
        """5000x / 5000倍 multipliers are not amounts."""
        meta = self._process("负载增长了5000倍。峰值是5000x基准。")
        self.assertEqual(meta["number_conflicts"], [])

    # ========== Consistent repeats ==========

    def test_identical_repeats_counted_not_flagged(self):
        """Identical values repeated are consistent repeats, never
        conflicts."""
        meta = self._process(
            "Revenue was 5 million. The report restated revenue at "
            "5 million.")
        self.assertEqual(meta["number_conflicts"], [])
        self.assertEqual(meta["conflict_count"], 0)
        self.assertEqual(meta["numeric_consistency"], "consistent")
        self.assertEqual(meta["consistent_repeats"], 1)

    def test_consistent_repeats_count_multiple_groups(self):
        """Two anchors repeating identically count as two repeat
        groups."""
        meta = self._process(
            "Revenue was 5 million and revenue stayed 5 million. "
            "The tool serves 800 users and serves 800 users again.")
        self.assertEqual(meta["number_conflicts"], [])
        self.assertEqual(meta["consistent_repeats"], 2)

    def test_repeat_plus_conflict_in_one_document(self):
        """One repeating anchor and one conflicting anchor coexist."""
        meta = self._process(
            "Revenue was 5 million. Revenue reached 6 million. "
            "Churn held at 3%. Churn stayed 3%.")
        self.assertEqual(meta["conflict_count"], 1)
        self.assertEqual(meta["consistent_repeats"], 1)
        self.assertEqual(meta["number_conflicts"][0]["anchor"], "revenue")

    # ========== Tolerance options ==========

    def test_near_conflict_ratio_default_tolerates_rounding(self):
        """0.05% relative drift (1,000,000 vs 1,000,500) stays
        consistent under the default 0.001 ratio."""
        meta = self._process(
            "Revenue was 1000000 dollars. A rounding pass wrote "
            "revenue at 1000500 dollars.")
        self.assertEqual(meta["number_conflicts"], [])
        self.assertEqual(meta["consistent_repeats"], 1)

    def test_near_conflict_ratio_zero_flags_rounding(self):
        """With near_conflict_ratio 0 the same drift becomes a
        conflict."""
        detector = NumberConflictDetector()
        detector.near_conflict_ratio = 0
        doc = Document(text="Revenue was 1000000 dollars. A rounding "
                            "pass wrote revenue at 1000500 dollars.")
        detector.process_docs([doc])
        self.assertEqual(doc.metadata["conflict_count"], 1)

    def test_tolerance_absolute_option(self):
        """tolerance 15 with ratio 0 absorbs a difference of 10; the
        defaults flag it (0.001 ratio at scale 5000 permits only 5)."""
        text = ("Sensors reported 5000 events. Sensors later reported "
                "5010 events.")
        detector = NumberConflictDetector()
        detector.tolerance = 15
        detector.near_conflict_ratio = 0
        doc = Document(text=text)
        detector.process_docs([doc])
        self.assertEqual(doc.metadata["number_conflicts"], [])
        self.assertEqual(doc.metadata["consistent_repeats"], 1)

        meta = self._process(text)
        self.assertEqual(meta["conflict_count"], 1)
        self.assertEqual(meta["consistent_repeats"], 0)

    # ========== Window semantics ==========

    def test_window_boundary_sentences_1_and_4(self):
        """Same anchor in sentences 1 and 4 (distance 3 >= window 3):
        separate chains, no conflict — the documented boundary."""
        meta = self._process(
            "Revenue was 5 million. Filler one. Filler two. "
            "Revenue reached 6 million.")
        self.assertEqual(meta["number_conflicts"], [])
        self.assertEqual(meta["conflict_count"], 0)
        self.assertEqual(meta["numeric_consistency"], "consistent")

    def test_window_boundary_wider_window_reunites(self):
        """window_size 5 compares the sentences 1-and-4 mentions and
        finds the conflict."""
        detector = NumberConflictDetector()
        detector.window_size = 5
        doc = Document(text="Revenue was 5 million. Filler one. "
                            "Filler two. Revenue reached 6 million.")
        detector.process_docs([doc])
        self.assertEqual(doc.metadata["conflict_count"], 1)

    def test_window_distance_two_conflicts(self):
        """Distance 2 (sentences 1 and 3) sits inside the default
        window and conflicts."""
        meta = self._process(
            "Revenue was 5 million. Filler. Revenue reached 6 million.")
        self.assertEqual(meta["conflict_count"], 1)

    def test_window_size_one_same_sentence_only(self):
        """window_size 1 compares mentions only inside one sentence."""
        detector = NumberConflictDetector()
        detector.window_size = 1
        doc = Document(text="Revenue was 5 million. "
                            "Revenue reached 6 million.")
        detector.process_docs([doc])
        self.assertEqual(doc.metadata["conflict_count"], 0)
        same_sentence = Document(
            text="Revenue was 5 million but revenue hit 6 million.")
        detector.process_docs([same_sentence])
        self.assertEqual(same_sentence.metadata["conflict_count"], 1)

    # ========== Cap ==========

    def test_conflict_list_capped_count_full(self):
        """25 conflicting anchors: the list is capped at 20 while
        conflict_count reports 25."""
        pairs = [("pumps", 3, 4), ("motors", 5, 6), ("valves", 7, 8),
                 ("sensors", 9, 10), ("panels", 11, 12)]
        parts = []
        for block in range(5):
            for unit, low, high in pairs:
                parts.append(f"Site{block} shipped {low} {unit}. "
                             f"Site{block} shipped {high} {unit}.")
        meta = self._process(" ".join(parts))
        self.assertEqual(len(meta["number_conflicts"]), 20)
        self.assertEqual(meta["conflict_count"], 25)
        self.assertEqual(meta["numeric_consistency"], "conflicts_found")

    def test_max_conflicts_configurable(self):
        """max_conflicts 2 keeps two records; the count stays full."""
        detector = NumberConflictDetector()
        detector.max_conflicts = 2
        doc = Document(text="Alpha shipped 3 pumps. Alpha shipped 4 "
                            "pumps. Beta ordered 5 motors. Beta "
                            "ordered 6 motors. Gamma holds 7 valves. "
                            "Gamma holds 8 valves.")
        detector.process_docs([doc])
        self.assertEqual(len(doc.metadata["number_conflicts"]), 2)
        self.assertEqual(doc.metadata["conflict_count"], 3)

    def test_values_shown_capped_at_five(self):
        """Six mentions of one anchor show at most five value records
        (the earliest five), while the gap math sees them all."""
        conflict = self._one(
            "Alpha shipped 3 pumps. Alpha shipped 4 pumps. Alpha "
            "shipped 5 pumps. Alpha shipped 6 pumps. Alpha shipped 7 "
            "pumps. Alpha shipped 8 pumps.")
        self.assertEqual(len(conflict["values"]), 5)
        self.assertEqual([v["value"] for v in conflict["values"]],
                         [3, 4, 5, 6, 7])
        # Worst pair 3 vs 8: gap 5/8 = 0.625.
        self.assertEqual(conflict["relative_gap"], 0.625)

    # ========== Passthrough and hygiene ==========

    def test_no_conflict_passthrough(self):
        """No numbers: verdict consistent, empty list, zero counts;
        text and id untouched."""
        text = "A calm paragraph without any figures at all."
        doc = Document(text=text)
        before_id = doc.id
        result = self.detector.process_docs([doc], self.query)[0]
        self.assertEqual(result.text, text)
        self.assertEqual(result.id, before_id)
        self.assertEqual(result.metadata["number_conflicts"], [])
        self.assertEqual(result.metadata["conflict_count"], 0)
        self.assertEqual(result.metadata["numeric_consistency"],
                         "consistent")
        self.assertEqual(result.metadata["consistent_repeats"], 0)

    def test_unanchored_numbers_dropped(self):
        """Numbers without a noun in any window are dropped: no
        conflict from bare drifting figures."""
        meta = self._process(
            "It grew to 5 million and later to 6 million.")
        self.assertEqual(meta["number_conflicts"], [])
        self.assertEqual(meta["consistent_repeats"], 0)

    def test_empty_batch_returns_empty(self):
        """An empty document list comes straight back."""
        self.assertEqual(self.detector.process_docs([], self.query), [])

    def test_none_text_treated_as_empty(self):
        """An empty-text document yields the consistent verdict."""
        doc = Document(text="")
        result = self.detector.process_docs([doc], self.query)[0]
        self.assertEqual(result.metadata["numeric_consistency"],
                         "consistent")
        self.assertEqual(result.metadata["conflict_count"], 0)

    def test_batch_order_and_isolation(self):
        """Multiple docs keep their order and never share groups."""
        docs = [
            Document(text="Revenue was 5 million. Revenue reached "
                          "6 million."),
            Document(text="Everything here agrees."),
            Document(text="Revenue was 5 million. Revenue reached "
                          "7 million."),
        ]
        results = self.detector.process_docs(docs, self.query)
        self.assertEqual([r.text for r in results],
                         [d.text for d in docs])
        self.assertEqual(results[0].metadata["conflict_count"], 1)
        self.assertEqual(results[1].metadata["conflict_count"], 0)
        self.assertEqual(results[2].metadata["conflict_count"], 1)
        self.assertNotEqual(results[0].metadata["number_conflicts"],
                            results[2].metadata["number_conflicts"])

    def test_existing_metadata_preserved_and_not_mutated(self):
        """Pre-existing metadata survives stamping and the original
        mapping is never mutated in place."""
        original = {"source": "report.docx", "page": 3}
        doc = Document(text="Revenue was 5 million. Revenue reached "
                            "6 million.", metadata=original)
        self.detector.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["source"], "report.docx")
        self.assertEqual(doc.metadata["page"], 3)
        self.assertIn("number_conflicts", doc.metadata)
        self.assertEqual(original, {"source": "report.docx", "page": 3})

    def test_empty_keys_disable_stamping(self):
        """Empty key values disable the corresponding metadata
        stamps."""
        detector = NumberConflictDetector()
        detector.conflicts_key = ""
        detector.count_key = ""
        detector.consistency_key = ""
        detector.repeats_key = ""
        doc = Document(text="Revenue was 5 million. Revenue reached "
                            "6 million.")
        detector.process_docs([doc])
        self.assertEqual(doc.metadata, {})

    # ========== Determinism ==========

    def test_deterministic_output(self):
        """The same text yields byte-identical metadata across runs."""
        text = ("Revenue was 5 million. Revenue reached 6 million. "
                "用户数达到5万，用户数突破60000。Conversion rose to 45%. "
                "Conversion climbed to 50%. In 2024 the cost was 5万; "
                "a later note put cost at 60000.")
        first = self._process(text)
        second = self._process(text)
        self.assertEqual(first, second)

    def test_anchor_and_stem_helpers(self):
        """Direct checks for the anchor word normalizer and stemmer."""
        anchor = NumberConflictDetector._anchor_word
        self.assertEqual(anchor("Users"), "user")
        self.assertEqual(anchor("revenues"), "revenue")
        self.assertIsNone(anchor("reached"))
        self.assertIsNone(anchor("was"))
        self.assertIsNone(anchor("million"))
        self.assertIsNone(anchor("approximately"))
        self.assertEqual(anchor("营收达到"), "营收")
        self.assertEqual(anchor("营收为"), "营收")
        self.assertEqual(anchor("年营收"), "营收")
        self.assertEqual(anchor("次年营收达到"), "营收")
        self.assertEqual(anchor("日活达到"), "日活")
        stem = NumberConflictDetector._stem
        self.assertEqual(stem("users"), "user")
        self.assertEqual(stem("reached"), "reach")
        self.assertEqual(stem("revenues"), "revenue")
        self.assertEqual(stem("its"), "its")


if __name__ == "__main__":
    unittest.main()
