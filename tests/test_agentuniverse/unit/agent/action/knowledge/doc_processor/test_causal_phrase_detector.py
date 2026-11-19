# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_causal_phrase_detector.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.causal_phrase_detector import CausalPhraseDetector
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestCausalPhraseDetector(unittest.TestCase):
    """Comprehensive test suite for CausalPhraseDetector."""

    def setUp(self):
        self.detector = CausalPhraseDetector()
        self.query = Query(query_str="causal")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _analyze(self, text: str):
        """Run detection on one text and return the relation list."""
        relations, _ = self.detector._analyze(text)
        return relations

    def _single(self, text: str) -> dict:
        """Assert exactly one relation and return it."""
        relations = self._analyze(text)
        self.assertEqual(len(relations), 1,
                         f"expected one relation, got {relations}")
        return relations[0]

    def _none(self, text: str):
        """Assert zero relations for the text."""
        relations = self._analyze(text)
        self.assertEqual(relations, [],
                         f"expected no relations, got {relations}")

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: cap 50, span limit 200, default metadata keys."""
        d = CausalPhraseDetector()
        self.assertEqual(d.max_relations, 50)
        self.assertEqual(d.span_char_limit, 200)
        self.assertEqual(d.relations_key, "causal_relations")
        self.assertEqual(d.count_key, "causal_count")
        self.assertEqual(d.density_key, "causal_density")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'causal_phrase_detector',
            'description': 'causal detector',
            'max_relations': 10,
            'span_char_limit': 64,
            'relations_key': 'causes',
            'count_key': 'n_causes',
            'density_key': 'cause_density',
        })
        d = CausalPhraseDetector()
        d._initialize_by_component_configer(configer)
        self.assertEqual(d.max_relations, 10)
        self.assertEqual(d.span_char_limit, 64)
        self.assertEqual(d.relations_key, "causes")
        self.assertEqual(d.count_key, "n_causes")
        self.assertEqual(d.density_key, "cause_density")
        self.assertEqual(d.name, "causal_phrase_detector")

    def test_invalid_configuration_raises(self):
        """Out-of-range caps, non-integer limits and non-string keys all
        fail at load time."""
        base = {
            'name': 'd', 'description': 'd',
            'max_relations': 50, 'span_char_limit': 200,
            'relations_key': 'causal_relations',
            'count_key': 'causal_count',
            'density_key': 'causal_density',
        }
        for key, value in (
            ('max_relations', 0),
            ('max_relations', -5),
            ('max_relations', 2.5),
            ('max_relations', True),
            ('span_char_limit', 0),
            ('span_char_limit', 1.5),
            ('span_char_limit', False),
            ('relations_key', 5),
            ('count_key', None.__class__),
            ('density_key', ['x']),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                CausalPhraseDetector()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== English pattern tests ==========

    def test_en_because_reverse(self):
        """"X because Y": cause is the clause after the marker, effect
        the clause before it; direction reverse."""
        hit = self._single("The flight was cancelled because fog "
                           "covered the runway.")
        self.assertEqual(hit["cause"], "fog covered the runway")
        self.assertEqual(hit["effect"], "The flight was cancelled")
        self.assertEqual(hit["marker"], "because")
        self.assertEqual(hit["direction"], "reverse")
        self.assertEqual(hit["span"],
                         "The flight was cancelled because fog "
                         "covered the runway")
        self.assertFalse(hit["cause_truncated"])
        self.assertFalse(hit["effect_truncated"])

    def test_en_because_clause_initial_forward(self):
        """Clause-initial "Because X, Y" degenerates to the forward
        reading: cause up to the comma, effect after it."""
        hit = self._single("Because fog covered the runway, the flight "
                           "was cancelled.")
        self.assertEqual(hit["cause"], "fog covered the runway")
        self.assertEqual(hit["effect"], "the flight was cancelled")
        self.assertEqual(hit["direction"], "forward")

    def test_en_because_of(self):
        """"because of X, Y": prepositional forward pattern."""
        hit = self._single("Because of fog, the flight was cancelled.")
        self.assertEqual(hit["cause"], "fog")
        self.assertEqual(hit["effect"], "the flight was cancelled")
        self.assertEqual(hit["marker"], "because of")
        self.assertEqual(hit["direction"], "forward")

    def test_en_due_to(self):
        """"due to X, Y": prepositional forward pattern."""
        hit = self._single("Due to a strike, shipments stalled.")
        self.assertEqual(hit["cause"], "a strike")
        self.assertEqual(hit["effect"], "shipments stalled")
        self.assertEqual(hit["marker"], "due to")
        self.assertEqual(hit["direction"], "forward")

    def test_en_as_a_result_of(self):
        """"as a result of X, Y": prepositional variant."""
        hit = self._single("As a result of the merger, two offices "
                           "closed.")
        self.assertEqual(hit["cause"], "the merger")
        self.assertEqual(hit["effect"], "two offices closed")
        self.assertEqual(hit["marker"], "as a result of")
        self.assertEqual(hit["direction"], "forward")

    def test_en_comma_so(self):
        """"X, so Y": comma before so is required; cause before the
        comma, effect after the marker."""
        hit = self._single("The flight was cancelled, so travellers "
                           "slept in the terminal.")
        self.assertEqual(hit["cause"], "The flight was cancelled")
        self.assertEqual(hit["effect"], "travellers slept in the terminal")
        self.assertEqual(hit["marker"], "so")
        self.assertEqual(hit["direction"], "forward")

    def test_en_so_without_comma_no_match(self):
        """Comma-less "so" (purpose / result without punctuation) is not
        the pattern and yields nothing."""
        self._none("Bring an umbrella so you stay dry.")

    def test_en_so_that_purpose_blocked(self):
        """, so that ..." is purpose, not cause: suppressed."""
        self._none("He saved hard, so that he could travel.")

    def test_en_since_causal(self):
        """"Y since X" with a verb-bearing clause after since: reverse
        causal reading."""
        hit = self._single("The market rallied since inflation had "
                           "eased.")
        self.assertEqual(hit["cause"], "inflation had eased")
        self.assertEqual(hit["effect"], "The market rallied")
        self.assertEqual(hit["marker"], "since")
        self.assertEqual(hit["direction"], "reverse")

    def test_en_since_temporal_dates_skipped(self):
        """Temporal "since <noun/date>" has no verb-ish token: no match."""
        self._none("The archive has been offline since 2019.")
        self._none("The bridge has been closed since Monday.")

    def test_en_since_temporal_noun_phrase_skipped(self):
        """Temporal "since the accident" (bare noun phrase): no match."""
        self._none("Traffic detours have run since the accident.")

    def test_en_leads_to_family(self):
        """"leads to / led to / leading to" all extract forward."""
        hit = self._single("Chronic underfunding leads to staff burnout.")
        self.assertEqual(hit["cause"], "Chronic underfunding")
        self.assertEqual(hit["effect"], "staff burnout")
        self.assertEqual(hit["marker"], "leads to")

        hit = self._single("The blackout led to a recall.")
        self.assertEqual(hit["cause"], "The blackout")
        self.assertEqual(hit["effect"], "a recall")
        self.assertEqual(hit["marker"], "led to")

        hit = self._single("Errors leading to outages were traced.")
        self.assertEqual(hit["marker"], "leading to")
        self.assertEqual(hit["cause"], "Errors")
        self.assertEqual(hit["effect"], "outages were traced")

    def test_en_results_in_family(self):
        """"results in / resulted in / resulting in" extract forward."""
        hit = self._single("Skipping review results in defects.")
        self.assertEqual(hit["cause"], "Skipping review")
        self.assertEqual(hit["effect"], "defects")
        self.assertEqual(hit["marker"], "results in")

        hit = self._single("The breach resulted in a fine.")
        self.assertEqual(hit["cause"], "The breach")
        self.assertEqual(hit["effect"], "a fine")
        self.assertEqual(hit["marker"], "resulted in")

    def test_en_causes_verb(self):
        """"X causes / cause / caused Y" extracts forward."""
        hit = self._single("Smoking causes cancer.")
        self.assertEqual(hit["cause"], "Smoking")
        self.assertEqual(hit["effect"], "cancer")
        self.assertEqual(hit["marker"], "causes")
        self.assertEqual(hit["direction"], "forward")

        hit = self._single("Delays caused resentment.")
        self.assertEqual(hit["cause"], "Delays")
        self.assertEqual(hit["effect"], "resentment")
        self.assertEqual(hit["marker"], "caused")

    def test_en_caused_by_reverse(self):
        """"X (was) caused by Y": effect before, cause after."""
        hit = self._single("The outage was caused by a bad deploy.")
        self.assertEqual(hit["cause"], "a bad deploy")
        self.assertEqual(hit["effect"], "The outage was")
        self.assertEqual(hit["marker"], "caused by")
        self.assertEqual(hit["direction"], "reverse")

    def test_en_therefore_connective(self):
        """"A, therefore B": cause is the preceding clause."""
        hit = self._single("Costs doubled, therefore the project was "
                           "halted.")
        self.assertEqual(hit["cause"], "Costs doubled")
        self.assertEqual(hit["effect"], "the project was halted")
        self.assertEqual(hit["marker"], "therefore")
        self.assertEqual(hit["direction"], "forward")

    def test_en_as_a_result_connective(self):
        """Parenthetical "A, and as a result, B": the conjunction-only
        clause is hopped, so the cause is A."""
        hit = self._single("The dam failed, and as a result, the valley "
                           "flooded.")
        self.assertEqual(hit["cause"], "The dam failed")
        self.assertEqual(hit["effect"], "the valley flooded")
        self.assertEqual(hit["marker"], "as a result")
        self.assertEqual(hit["direction"], "forward")

    def test_en_sentence_initial_therefore_skipped(self):
        """"Therefore" without an in-sentence antecedent clause is out of
        scope (cross-sentence anaphora): no relation."""
        self._none("Therefore the project was halted.")

    # ========== Chinese pattern tests ==========

    def test_zh_because_so_pair(self):
        """"因为X所以Y" splits at 所以; forward direction."""
        hit = self._single("因为暴雨所以航班取消了。")
        self.assertEqual(hit["cause"], "暴雨")
        self.assertEqual(hit["effect"], "航班取消了")
        self.assertEqual(hit["marker"], "因为...所以")
        self.assertEqual(hit["direction"], "forward")
        self.assertEqual(hit["span"], "因为暴雨所以航班取消了")

    def test_zh_because_without_so_no_match(self):
        """A 因为 without a closing 所以 in the same sentence yields no
        relation (the effect is usually elliptical)."""
        self._none("因为天气原因我们决定改期，下次另行通知。")

    def test_zh_youyu(self):
        """"由于X，Y": prepositional forward pattern."""
        hit = self._single("由于设备老化，产量下降了。")
        self.assertEqual(hit["cause"], "设备老化")
        self.assertEqual(hit["effect"], "产量下降了")
        self.assertEqual(hit["marker"], "由于")
        self.assertEqual(hit["direction"], "forward")

    def test_zh_daozhi(self):
        """"X导致Y" (with and without the aspect particle 了)."""
        hit = self._single("供应链中断导致交付延期。")
        self.assertEqual(hit["cause"], "供应链中断")
        self.assertEqual(hit["effect"], "交付延期")
        self.assertEqual(hit["marker"], "导致")

        hit = self._single("高温导致了路面变形。")
        self.assertEqual(hit["cause"], "高温")
        self.assertEqual(hit["effect"], "路面变形")
        self.assertEqual(hit["marker"], "导致")

    def test_zh_zaocheng(self):
        """"X造成Y" extracts forward."""
        hit = self._single("操作失误造成数据丢失。")
        self.assertEqual(hit["cause"], "操作失误")
        self.assertEqual(hit["effect"], "数据丢失")
        self.assertEqual(hit["marker"], "造成")

    def test_zh_yinqi(self):
        """"X引起Y" extracts forward."""
        hit = self._single("电池缺陷引起召回。")
        self.assertEqual(hit["cause"], "电池缺陷")
        self.assertEqual(hit["effect"], "召回")
        self.assertEqual(hit["marker"], "引起")

    def test_zh_shide(self):
        """"X使得Y" extracts forward."""
        hit = self._single("新规使得成本上升。")
        self.assertEqual(hit["cause"], "新规")
        self.assertEqual(hit["effect"], "成本上升")
        self.assertEqual(hit["marker"], "使得")

    def test_zh_yinci(self):
        """"A，因此B": cause is the clause before 因此."""
        hit = self._single("需求激增，因此交货周期延长。")
        self.assertEqual(hit["cause"], "需求激增")
        self.assertEqual(hit["effect"], "交货周期延长")
        self.assertEqual(hit["marker"], "因此")
        self.assertEqual(hit["direction"], "forward")

    # ========== Guard tests ==========

    def test_noun_phrase_the_cause_of_skipped(self):
        """"the cause of ..." is a noun phrase: suppressed by the
        followed-by-"of" guard."""
        self._none("Investigators cited the cause of the outage.")

    def test_noun_phrase_the_result_of_skipped(self):
        """"the result of ..." is a noun phrase: never extracted."""
        self._none("The result of the audit was clean.")

    def test_noun_phrase_determiner_before_results_in_skipped(self):
        """A determiner directly before "results in" ("the results in
        the appendix") marks a noun reading: suppressed."""
        self._none("The results in the appendix were disputed.")

    def test_noun_phrase_determiner_before_causes_skipped(self):
        """A determiner directly before "cause" ("a cause") marks a noun
        reading: suppressed."""
        self._none("Regulators listed a cause for concern in the filing.")

    def test_quote_immunity_english(self):
        """Markers inside a double-quoted region never fire."""
        self._none('The guide says "restart the node because the kernel '
                   'leaks" during maintenance windows.')

    def test_quote_immunity_chinese(self):
        """Markers inside CJK corner quotes never fire."""
        self._none("「因为预算不足所以项目延期」被记录在案。")

    def test_contractions_do_not_open_quotes(self):
        """The apostrophe in "didn't" is not a quote opener, so the
        following because still matches."""
        hit = self._single("It didn't fail because the test was wrong.")
        self.assertEqual(hit["cause"], "the test was wrong")
        self.assertEqual(hit["effect"], "It didn't fail")
        self.assertEqual(hit["direction"], "reverse")

    def test_since_guard_fires_both_ways(self):
        """The same sentence frame flips with the post-since clause:
        a verb-ish clause matches, a bare noun phrase does not."""
        causal = self._single("The market rallied since inflation had "
                              "eased.")
        self.assertEqual(causal["direction"], "reverse")
        self._none("The market rallied since March.")

    # ========== Span hygiene tests ==========

    def test_span_truncation_flags(self):
        """A cause longer than span_char_limit is cut to the limit and
        flagged; the effect is untouched."""
        filler = "x" * 300
        text = f"Vendor {filler} concentration leads to churn."
        self.assertGreater(len(f"Vendor {filler} concentration"), 200)
        hit = self._single(text)
        self.assertEqual(hit["cause"], ("Vendor " + filler +
                                        " concentration")[:200])
        self.assertEqual(len(hit["cause"]), 200)
        self.assertTrue(hit["cause_truncated"])
        self.assertEqual(hit["effect"], "churn")
        self.assertFalse(hit["effect_truncated"])

    def test_effect_truncation_flag(self):
        """An effect longer than the limit is cut and flagged."""
        filler = " cascading failures across regions and tenants" * 12
        text = f"The breach leads to{filler}."
        hit = self._single(text)
        self.assertEqual(len(hit["effect"]), 200)
        self.assertTrue(hit["effect_truncated"])
        self.assertFalse(hit["cause_truncated"])
        self.assertEqual(hit["cause"], "The breach")
        self.assertTrue(hit["effect"].startswith("cascading failures"))

    def test_span_char_limit_configurable(self):
        """A smaller span_char_limit shortens the cut on both sides."""
        self.detector.span_char_limit = 12
        hit = self._single("Chronic underfunding leads to staff burnout.")
        self.assertEqual(hit["cause"], "Chronic unde")
        self.assertTrue(hit["cause_truncated"])
        self.assertEqual(hit["effect"], "staff burnou")
        self.assertTrue(hit["effect_truncated"])

    def test_clause_local_spans_in_multi_clause_sentence(self):
        """Spans are the clauses adjacent to the marker, bounded at
        commas, not whole-sentence grabs."""
        hit = self._single("The audit finished late, and the vendor "
                           "missed the deadline, because the data feed "
                           "failed twice.")
        self.assertEqual(hit["cause"], "the data feed failed twice")
        self.assertEqual(hit["effect"], "the vendor missed the deadline")

    def test_overlapping_markers_resolve_to_one_hit(self):
        """"A because B, so C": the because- and so-candidates share the
        opening clause; the longer same-start region (the so reading)
        wins, exactly one relation results — the so-cause is the whole
        first clause, which legitimately contains the because phrase."""
        relations = self._analyze(
            "The flight was cancelled because fog rolled in, so "
            "travellers slept in the terminal.")
        self.assertEqual(len(relations), 1)
        self.assertEqual(relations[0]["marker"], "so")
        self.assertEqual(relations[0]["cause"],
                         "The flight was cancelled because fog rolled in")
        self.assertEqual(relations[0]["effect"],
                         "travellers slept in the terminal")

    # ========== Metadata stamping tests ==========

    def test_metadata_stamped_with_relations_count_density(self):
        """The three metadata entries are stamped on each document."""
        doc = _doc("Rain caused flooding. Heat led to outages. "
                   "Wind toppled pylons, so power failed. Skies cleared.")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(len(result), 1)
        meta = result[0].metadata
        self.assertEqual(meta["causal_count"], 3)
        self.assertEqual(len(meta["causal_relations"]), 3)
        self.assertEqual(meta["causal_density"], 75.0)
        markers = [r["marker"] for r in meta["causal_relations"]]
        self.assertEqual(markers, ["caused", "led to", "so"])

    def test_relations_in_document_order(self):
        """Relations keep textual order across sentences; spans stay
        clause-local ("Later," is a separate temporal clause)."""
        doc = _doc("A strike caused delays. Later, heat led to outages.")
        result = self.detector.process_docs([doc], self.query)
        relations = result[0].metadata["causal_relations"]
        self.assertEqual([r["cause"] for r in relations],
                         ["A strike", "heat"])
        self.assertEqual([r["effect"] for r in relations],
                         ["delays", "outages"])

    def test_hit_dict_shape(self):
        """Each hit carries exactly the documented keys."""
        hit = self._single("Smoking causes cancer.")
        self.assertEqual(set(hit), {"cause", "effect", "marker", "span",
                                    "direction", "cause_truncated",
                                    "effect_truncated"})

    def test_cap_fifty_relations(self):
        """A document with more than max_relations detections is capped
        at 50; count reflects the cap; density is computed from the
        stamped list (50 / 60 sentences = 83.33)."""
        text = " ".join(f"Item {i} leads to failure {i}." for i in range(60))
        doc = _doc(text)
        result = self.detector.process_docs([doc], self.query)
        meta = result[0].metadata
        self.assertEqual(meta["causal_count"], 50)
        self.assertEqual(len(meta["causal_relations"]), 50)
        self.assertEqual(meta["causal_density"], 83.33)
        # Cap keeps document order.
        self.assertEqual(meta["causal_relations"][0]["cause"], "Item 0")
        self.assertEqual(meta["causal_relations"][49]["cause"], "Item 49")

    def test_cap_configurable(self):
        """max_relations is a real knob."""
        self.detector.max_relations = 2
        doc = _doc("Ann caused delays. Cold caused outages. "
                   "Ice caused floods.")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["causal_count"], 2)
        self.assertEqual(len(result[0].metadata["causal_relations"]), 2)

    def test_density_arithmetic_rounding(self):
        """Density is relations per 100 sentences, 2-decimal rounding:
        1 relation over 3 sentences -> 33.33."""
        doc = _doc("Rain caused flooding. Skies cleared. Winds eased.")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["causal_density"], 33.33)

    def test_no_causal_passthrough(self):
        """A causal-free document passes through with empty relations,
        zero count and zero density; text and id are untouched."""
        text = ("The quarterly report covers revenue. Growth remained "
                "stable.")
        doc = _doc(text, source=" filings")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].text, text)
        self.assertEqual(result[0].id, doc.id)
        self.assertEqual(result[0].metadata["causal_relations"], [])
        self.assertEqual(result[0].metadata["causal_count"], 0)
        self.assertEqual(result[0].metadata["causal_density"], 0.0)
        self.assertEqual(result[0].metadata["source"], " filings")

    def test_disabled_keys_stamp_nothing(self):
        """Empty key strings disable the individual stamps."""
        self.detector.relations_key = ""
        self.detector.density_key = ""
        doc = _doc("Rain caused flooding.")
        result = self.detector.process_docs([doc], self.query)
        self.assertNotIn("causal_relations", result[0].metadata)
        self.assertNotIn("causal_density", result[0].metadata)
        self.assertEqual(result[0].metadata["causal_count"], 1)

    def test_documents_not_corrupted_and_metadata_copied(self):
        """Text/id untouched, pre-existing metadata survives, and
        stamping writes through a copy rather than mutating the original
        mapping."""
        text = "Rain caused flooding."
        doc = _doc(text, source="met", rank=1)
        meta_ref = doc.metadata
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, text)
        self.assertEqual(result[0].metadata["source"], "met")
        self.assertEqual(result[0].metadata["rank"], 1)
        self.assertNotIn("causal_relations", meta_ref)
        self.assertIsNot(doc.metadata, meta_ref)

    def test_empty_batch_and_none_text(self):
        """Empty batches return []; None text is tolerated and analyzed
        as empty."""
        self.assertEqual(self.detector.process_docs([], self.query), [])
        doc = Document(text="placeholder")
        doc.text = None
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["causal_relations"], [])
        self.assertEqual(result[0].metadata["causal_count"], 0)
        self.assertEqual(result[0].metadata["causal_density"], 0.0)

    # ========== Sentence segmentation family tests ==========

    def test_abbreviations_do_not_split_sentences(self):
        """A "because" clause after an abbreviated title stays in one
        sentence with its effect."""
        hit = self._single("Dr. Smith cancelled the trial because "
                           "funding lapsed.")
        self.assertEqual(hit["cause"], "funding lapsed")
        self.assertEqual(hit["effect"], "Dr. Smith cancelled the trial")

    def test_sentence_count_feeds_density(self):
        """Sentence counting uses the conservative splitter: two
        sentences, one relation -> 50.0."""
        doc = _doc("The bank raised rates because inflation persisted. "
                   "Markets dipped.")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["causal_count"], 1)
        self.assertEqual(result[0].metadata["causal_density"], 50.0)

    # ========== Determinism tests ==========

    def test_deterministic_across_instances_and_runs(self):
        """Identical inputs yield identical output across instances and
        repeated runs, including dict key order."""
        text = ("The flight was cancelled because fog rolled in. "
                "因为暴雨所以航班取消了。 Costs doubled, therefore the "
                "project was halted. 供应链中断导致交付延期。")
        first = CausalPhraseDetector()._analyze(text)
        for _ in range(3):
            self.assertEqual(
                self.detector._analyze(text), first)

    def test_mixed_language_document(self):
        """English and Chinese markers coexist in one document."""
        doc = _doc("Rain caused flooding. 因为暴雨所以航班取消了。")
        result = self.detector.process_docs([doc], self.query)
        relations = result[0].metadata["causal_relations"]
        self.assertEqual(len(relations), 2)
        self.assertEqual(relations[0]["marker"], "caused")
        self.assertEqual(relations[1]["marker"], "因为...所以")
        self.assertEqual(result[0].metadata["causal_density"], 100.0)


if __name__ == '__main__':
    unittest.main()
