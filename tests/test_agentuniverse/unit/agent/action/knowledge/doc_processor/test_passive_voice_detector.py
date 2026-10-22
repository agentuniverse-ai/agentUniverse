# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_passive_voice_detector.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.passive_voice_detector import (
    IRREGULAR_PARTICIPLES,
    PassiveVoiceDetector,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Sentence banks with hand-verified hit counts. ACTIVE contains no be-form
# followed by a participle; each PASSIVE_* sentence holds exactly one
# English passive.
ACTIVE = "The team ships the module every week."
PASSIVE_A = "The module was shipped by the release team."
PASSIVE_B = "The report was reviewed before the deadline."
PASSIVE_C = "The invoice was paid after the audit."
PASSIVE_D = "The contract was signed in May."


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestPassiveVoiceDetector(unittest.TestCase):
    """Comprehensive offline test suite for PassiveVoiceDetector."""

    def setUp(self):
        self.detector = PassiveVoiceDetector()
        self.query = Query(query_str="passive voice")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _report(self, text: str) -> dict:
        """Analyze one text through a fresh document and return the report."""
        doc = _doc(text)
        result = self.detector.process_docs([doc], self.query)
        return result[0].metadata[self.detector.output_key]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: 10%/25% thresholds, cap 50, 'passive_voice' key."""
        d = PassiveVoiceDetector()
        self.assertEqual(d.moderate_threshold, 0.10)
        self.assertEqual(d.heavy_threshold, 0.25)
        self.assertEqual(d.max_hits, 50)
        self.assertEqual(d.output_key, "passive_voice")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'passive_voice_detector',
            'description': 'passive voice detector',
            'moderate_threshold': 0.2,
            'heavy_threshold': 0.4,
            'max_hits': 3,
            'output_key': 'pv',
        })
        d = PassiveVoiceDetector()
        d._initialize_by_component_configer(configer)
        self.assertEqual(d.moderate_threshold, 0.2)
        self.assertEqual(d.heavy_threshold, 0.4)
        self.assertEqual(d.max_hits, 3)
        self.assertEqual(d.output_key, 'pv')
        self.assertEqual(d.name, 'passive_voice_detector')

    def test_invalid_configuration_raises(self):
        """Out-of-range thresholds, crossed/equal bands, non-integer caps
        and non-string keys all fail at load time."""
        base = {
            'name': 'd', 'description': 'd',
            'moderate_threshold': 0.10, 'heavy_threshold': 0.25,
            'max_hits': 50, 'output_key': 'passive_voice',
        }
        for key, value in (
            ('moderate_threshold', -0.1),
            ('moderate_threshold', 1.5),
            ('moderate_threshold', 'x'),
            ('moderate_threshold', True),
            ('heavy_threshold', -1),
            ('heavy_threshold', 2),
            ('heavy_threshold', 0.05),   # below the default moderate band
            ('moderate_threshold', 0.3),  # above the default heavy bound
            ('moderate_threshold', 0.25),  # equal to heavy_threshold
            ('max_hits', 0),
            ('max_hits', -5),
            ('max_hits', 2.5),
            ('max_hits', True),
            ('output_key', 5),
            ('output_key', ['x']),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                PassiveVoiceDetector()._initialize_by_component_configer(
                    self._create_configer(config))

    def test_custom_thresholds_change_flags(self):
        """Bands are real knobs: ratio 0.5 is 'moderate' under 0.5/0.9
        bands where the defaults would say 'heavy'."""
        configer = self._create_configer({
            'name': 'd', 'description': 'd',
            'moderate_threshold': 0.5, 'heavy_threshold': 0.9,
        })
        d = PassiveVoiceDetector()
        d._initialize_by_component_configer(configer)
        doc = _doc(f"{ACTIVE} {PASSIVE_A}")  # 2 sentences, 1 passive
        report = d.process_docs([doc], self.query)[0].metadata['passive_voice']
        self.assertEqual(report['passive_ratio'], 0.5)
        self.assertEqual(report['style_flag'], 'moderate')

    # ========== English detection tests ==========

    def test_all_be_forms_detected(self):
        """was/were/is/are/be/been/being/am each anchor a passive; the
        perfect and progressive forms are caught by their inner
        be-form + participle pair."""
        for text in (
            "The letter was sent.",
            "The letters were sent.",
            "The letter is sent.",
            "The letters are sent.",
            "The letter will be sent.",
            "The letter has been sent.",
            "The letter is being sent.",
            "I am asked to help.",
        ):
            report = self._report(text)
            self.assertEqual(report['passive_count'], 1, text)
            self.assertEqual(report['total_sentences'], 1, text)

    def test_irregular_participle_sweep(self):
        """Every entry of the ~90-word irregular table is recognized as
        the participle of 'was <participle>'."""
        for participle in sorted(IRREGULAR_PARTICIPLES):
            text = f"The report was {participle} yesterday."
            report = self._report(text)
            self.assertEqual(report['passive_count'], 1, participle)
            hit = report['hits'][0]
            self.assertEqual(hit['text'], f"was {participle}")
            self.assertIsNone(hit['agent'])
            self.assertEqual(hit['lang'], 'en')

    def test_regular_ed_participles(self):
        """Regular '-ed' participles are recognized after every be-form."""
        for text in (
            "The form was submitted.",
            "The forms were approved.",
            "The claim is considered.",
            "The records are indexed.",
            "The draft will be published.",
        ):
            self.assertEqual(self._report(text)['passive_count'], 1, text)

    def test_short_ed_words_not_participles(self):
        """'red'/'bed'-style three-letter words ending in 'ed' letters do
        not count as participles; a genuine irregular in the same text
        still does."""
        for text in ("The sky is red.", "The bed is large."):
            self.assertEqual(self._report(text)['passive_count'], 0, text)
        self.assertEqual(
            self._report("The map was drawn but the sky was red.")
            ['passive_count'], 1)

    def test_adverb_interposition(self):
        """One adverb may sit between be-form and participle; negated
        contractions carry the adverb inside them."""
        cases = {
            "The report was not submitted.": "was not submitted",
            "Errors were often seen in logs.": "were often seen",
            "The cache is never cleared manually.": "is never cleared",
            "The guide is widely cited by engineers.": "is widely cited",
            "The form wasn't signed.": "wasn't signed",
        }
        for text, matched in cases.items():
            report = self._report(text)
            self.assertEqual(report['passive_count'], 1, text)
            self.assertEqual(report['hits'][0]['text'], matched)

    def test_adjectival_guards(self):
        """-ed words after be that describe states, plus 'used to' /
        'supposed to' semi-auxiliaries, are not passives."""
        for text in (
            "She is interested in astronomy.",
            "He was tired after the run.",
            "The kids are excited.",
            "They weren't interested in the offer.",
            "This tool is used to convert files.",
            "The train is supposed to arrive at noon.",
        ):
            self.assertEqual(self._report(text)['passive_count'], 0, text)

    def test_used_and_supposed_still_count_with_real_passive_reading(self):
        """'used'/'supposed' followed by anything but 'to' stay regular
        participles, with the by-agent captured when present."""
        report = self._report("This tool is used by the team.")
        self.assertEqual(report['passive_count'], 1)
        self.assertEqual(report['hits'][0]['text'], "is used")
        self.assertEqual(report['hits'][0]['agent'], "the team")

    def test_progressive_active_and_adjacent_not_counted(self):
        """Progressive ('is running') and bare be-adjacency without a
        participle do not fire."""
        for text in ("The engine is running.",
                     "The answer is here.",
                     "The idea was to leave early.",
                     "She will be there."):
            self.assertEqual(self._report(text)['passive_count'], 0, text)

    # ========== by-agent capture tests ==========

    def test_by_agent_captured(self):
        """'by X' within five tokens after the participle yields the
        agent phrase (up to three words, boundary words end it)."""
        cases = {
            "The proposal was approved by the committee.":
                "the committee",
            "The proposal was approved by the central bank on Friday.":
                "the central bank",
            "The policy was written by the very same committee.":
                "the very same",
            "The proposal was approved only after long debate by the board.":
                "the board",
        }
        for text, agent in cases.items():
            report = self._report(text)
            self.assertEqual(report['passive_count'], 1, text)
            self.assertEqual(report['hits'][0]['agent'], agent, text)

    def test_by_agent_absent(self):
        """No 'by', a 'by' beyond five tokens, or a 'by' in the next
        sentence all leave the agent null."""
        for text in (
            "The proposal was approved yesterday.",
            "The proposal was approved only after a long debate by the "
            "board.",
            "The proposal was approved. By the way, it ships.",
            "The report was reviewed internally.",
        ):
            report = self._report(text)
            self.assertEqual(report['passive_count'], 1, text)
            self.assertIsNone(report['hits'][0]['agent'], text)

    def test_agent_scan_stops_at_next_construction(self):
        """A second passive between the first participle and a distant
        'by' is not misattributed as the first hit's agent."""
        report = self._report(
            "The module was shipped and was reviewed by the team.")
        self.assertEqual(report['passive_count'], 2)
        shipped, reviewed = report['hits']
        self.assertEqual(shipped['text'], "was shipped")
        self.assertIsNone(shipped['agent'])
        self.assertEqual(reviewed['text'], "was reviewed")
        self.assertEqual(reviewed['agent'], "the team")

    # ========== Chinese detection tests ==========

    def test_chinese_markers(self):
        """被 / 受 / 受到 / 遭到 / 由...所 each flag exactly one hit with
        a zh language tag and no agent."""
        cases = {
            "报告被提交了。": "被提交了",
            "文件被修改了三次。": "被修改了三次",
            "公司受到调查。": "受到调查",
            "申请遭到拒绝。": "遭到拒绝",
            "该计划由委员会所批准。": "由委员会所批准",
        }
        for text, matched in cases.items():
            report = self._report(text)
            self.assertEqual(report['passive_count'], 1, text)
            hit = report['hits'][0]
            self.assertEqual(hit['text'], matched)
            self.assertEqual(hit['lang'], 'zh')
            self.assertIsNone(hit['agent'])
            self.assertEqual(report['total_sentences'], 1, text)

    def test_chinese_word_final_shou_guard(self):
        """受 is only matched word-initially, so 接受 / 享受 never fire."""
        for text in ("他接受了这个方案。",
                     "我们享受这个过程。",
                     "大家忍受了很长的时间。"):
            self.assertEqual(self._report(text)['passive_count'], 0, text)

    def test_chinese_sentence_counting(self):
        """Chinese terminators split sentences for the ratio baseline."""
        report = self._report("报告被提交了。该计划由委员会所批准。")
        self.assertEqual(report['total_sentences'], 2)
        self.assertEqual(report['passive_count'], 2)
        self.assertEqual(report['passive_ratio'], 1.0)
        self.assertEqual(report['style_flag'], 'heavy')

    def test_mixed_language_document(self):
        """English and Chinese hits coexist, sorted by span."""
        text = "The report was signed. 报告被签署了。"
        report = self._report(text)
        self.assertEqual(report['passive_count'], 2)
        self.assertEqual([hit['lang'] for hit in report['hits']],
                         ['en', 'zh'])
        self.assertEqual(report['total_sentences'], 2)
        self.assertEqual(report['passive_ratio'], 1.0)

    # ========== Ratio, flag and cap tests ==========

    def test_active_text_scores_zero(self):
        """Energetic active prose with be-adjacency but no participles
        scores zero across the board."""
        report = self._report(
            "The API is fast. We keep the docs short. The parser handles "
            "edge cases. It runs offline.")
        self.assertEqual(report['passive_count'], 0)
        self.assertEqual(report['total_sentences'], 4)
        self.assertEqual(report['passive_ratio'], 0.0)
        self.assertEqual(report['passive_density_per_100'], 0.0)
        self.assertEqual(report['style_flag'], 'active')
        self.assertEqual(report['hits'], [])

    def test_flag_boundaries(self):
        """Ratio bands: <10% active, [10%, 25%] moderate, >25% heavy —
        probed at both edges with exact sentence counts."""
        cases = [
            (ACTIVE * 10, 0.0, 'active'),
            (ACTIVE * 91 + PASSIVE_A * 9, 0.09, 'active'),
            (ACTIVE * 9 + PASSIVE_A, 0.1, 'moderate'),
            (ACTIVE * 3 + PASSIVE_A, 0.25, 'moderate'),
            (ACTIVE * 74 + PASSIVE_A * 26, 0.26, 'heavy'),
            (ACTIVE * 2 + PASSIVE_A + PASSIVE_B, 0.5, 'heavy'),
        ]
        for text, ratio, flag in cases:
            report = self._report(text)
            self.assertEqual(report['passive_ratio'], ratio, flag)
            self.assertEqual(report['style_flag'], flag)

    def test_density_per_100_sentences(self):
        """Density counts constructions (not sentences) per 100
        sentences; ratio counts sentences containing at least one."""
        text = " ".join([ACTIVE] * 10 + [PASSIVE_A, PASSIVE_B])
        report = self._report(text)
        self.assertEqual(report['total_sentences'], 12)
        self.assertEqual(report['passive_count'], 2)
        self.assertEqual(report['passive_ratio'], 0.1667)
        self.assertEqual(report['passive_density_per_100'], 16.67)
        self.assertEqual(report['style_flag'], 'moderate')

    def test_ratio_is_sentence_fraction_not_hit_fraction(self):
        """Two passives in one sentence: count 2, ratio 1.0 (not 2.0),
        density 200.0, flag heavy."""
        report = self._report(
            "The draft was written, was reviewed, and was approved in "
            "one day.")
        self.assertEqual(report['total_sentences'], 1)
        self.assertEqual(report['passive_count'], 3)
        self.assertEqual(report['passive_ratio'], 1.0)
        self.assertEqual(report['passive_density_per_100'], 300.0)
        self.assertEqual([hit['text'] for hit in report['hits']],
                         ["was written", "was reviewed", "was approved"])

    def test_max_hits_cap(self):
        """The cap bounds the recorded hits (earliest spans kept) while
        passive_count, ratio and density keep counting everything."""
        text = " ".join([PASSIVE_A, PASSIVE_B, PASSIVE_C, PASSIVE_D])
        self.detector.max_hits = 2
        report = self._report(text)
        self.assertEqual(report['passive_count'], 4)
        self.assertEqual(report['total_sentences'], 4)
        self.assertEqual(len(report['hits']), 2)
        self.assertTrue(report['hits_truncated'])
        self.assertEqual(report['hits'][0]['text'], "was shipped")
        self.assertEqual(report['hits'][1]['text'], "was reviewed")
        self.assertEqual(report['passive_ratio'], 1.0)

        self.detector.max_hits = 50
        report = self._report(text)
        self.assertEqual(len(report['hits']), 4)
        self.assertFalse(report['hits_truncated'])

    # ========== Report shape and determinism tests ==========

    def test_report_and_hit_structure(self):
        """Report and hit dicts carry exactly the documented keys, and
        every span slices back to its recorded text."""
        report = self._report(
            f"{PASSIVE_A} {PASSIVE_B} 报告被提交了。")
        self.assertEqual(
            set(report.keys()),
            {'passive_count', 'total_sentences', 'passive_ratio',
             'passive_density_per_100', 'style_flag', 'hits',
             'hits_truncated'})
        text = f"{PASSIVE_A} {PASSIVE_B} 报告被提交了。"
        for hit in report['hits']:
            self.assertEqual(set(hit.keys()),
                             {'text', 'span', 'lang', 'agent'})
            start, end = hit['span']
            self.assertEqual(text[start:end], hit['text'])
            self.assertTrue(0 <= start < end <= len(text))

    def test_determinism(self):
        """Repeated analysis of the same text produces byte-identical
        reports across fresh detector instances."""
        text = f"{ACTIVE} {PASSIVE_A} 报告被提交了。申请遭到拒绝。"
        first = self._report(text)
        for _ in range(3):
            self.assertEqual(self._report(text), first)

    # ========== Pipeline-shape tests ==========

    def test_documents_kept_in_order_with_text_and_id_intact(self):
        """The analyzer filters nothing: same objects, same order, same
        text and ids."""
        docs = [_doc(PASSIVE_A, source="a"), _doc(ACTIVE, source="b"),
                _doc("报告被提交了。", source="c")]
        ids = [doc.id for doc in docs]
        result = self.detector.process_docs(docs, self.query)
        self.assertEqual(len(result), 3)
        for original, kept in zip(docs, result):
            self.assertIs(kept, original)
        self.assertEqual([doc.id for doc in result], ids)
        self.assertEqual(result[0].text, PASSIVE_A)
        self.assertEqual(result[2].text, "报告被提交了。")

    def test_metadata_stamped_through_copy(self):
        """Pre-existing metadata survives; the stamp goes through a
        copied mapping so the caller's original dict is not mutated."""
        doc = _doc(PASSIVE_A, source="wire", rank=1)
        meta_ref = doc.metadata
        result = self.detector.process_docs([doc], self.query)
        kept = result[0]
        self.assertIn('passive_voice', kept.metadata)
        self.assertEqual(kept.metadata['source'], 'wire')
        self.assertEqual(kept.metadata['rank'], 1)
        self.assertIsNot(kept.metadata, meta_ref)
        self.assertNotIn('passive_voice', meta_ref)

    def test_empty_output_key_disables_stamping(self):
        """output_key '' leaves document metadata untouched."""
        self.detector.output_key = ""
        doc = _doc(PASSIVE_A, source="wire")
        result = self.detector.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata, {"source": "wire"})

    def test_empty_batch_and_blank_documents(self):
        """Empty batches give empty lists; blank or None text gives a
        zero report with the 'active' flag."""
        self.assertEqual(self.detector.process_docs([], self.query), [])

        for text in ("", "   "):
            doc = _doc(text)
            report = self.detector.process_docs([doc], self.query)[0] \
                .metadata['passive_voice']
            self.assertEqual(report['passive_count'], 0)
            self.assertEqual(report['total_sentences'], 0)
            self.assertEqual(report['passive_ratio'], 0.0)
            self.assertEqual(report['passive_density_per_100'], 0.0)
            self.assertEqual(report['style_flag'], 'active')
            self.assertEqual(report['hits'], [])
            self.assertFalse(report['hits_truncated'])

        # None text is normalized to "" by the analyzer itself.
        report = self.detector._analyze(None)
        self.assertEqual(report['passive_count'], 0)
        self.assertEqual(report['total_sentences'], 0)
        self.assertEqual(report['style_flag'], 'active')


if __name__ == '__main__':
    unittest.main()
