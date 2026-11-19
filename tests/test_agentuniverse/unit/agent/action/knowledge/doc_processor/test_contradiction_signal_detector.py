# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_contradiction_signal_detector.py

"""Tests for the ContradictionSignalDetector doc processor."""

import os
import unittest
from types import SimpleNamespace

import agentuniverse.agent.action.knowledge.doc_processor.\
    contradiction_signal_detector as csd_module
from agentuniverse.agent.action.knowledge.doc_processor.\
    contradiction_signal_detector import ContradictionSignalDetector
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer

_YAML_PATH = os.path.join(os.path.dirname(csd_module.__file__),
                          "contradiction_signal_detector.yaml")

_FLIP_TEXT = ("The export service supports batching. "
              "However, the export service rejects batching.")


def _run(text, query=None, **kwargs):
    """Process a single text doc through ContradictionSignalDetector."""
    detector = ContradictionSignalDetector(**kwargs)
    out = detector.process_docs([Document(text=text)], query)
    return out[0]


def _kinds(doc):
    """Return the signal kinds recorded for one processed doc."""
    return [s["kind"] for s in doc.metadata["contradiction_signals"]]


class TestContrastFlip(unittest.TestCase):
    """contrast_flip: later sentence opens with a contrast marker."""

    def test_flip_with_two_shared_terms_is_high(self) -> None:
        """A however-flip sharing >= 2 content terms yields a high signal."""
        doc = _run(_FLIP_TEXT)
        signals = doc.metadata["contradiction_signals"]
        self.assertEqual(len(signals), 1)
        signal = signals[0]
        self.assertEqual(signal["kind"], "contrast_flip")
        self.assertEqual(signal["confidence"], "high")
        self.assertEqual(signal["shared_terms"],
                         ["batch", "export", "service"])
        self.assertEqual(doc.metadata["signal_count"], 1)
        self.assertEqual(doc.metadata["contradiction_risk"], "medium")

    def test_flip_spans_slice_back_to_sentences(self) -> None:
        """Recorded spans are [start, end) offsets into the doc text."""
        doc = _run(_FLIP_TEXT)
        signal = doc.metadata["contradiction_signals"][0]
        a_start, a_end = signal["sentence_a_span"]
        b_start, b_end = signal["sentence_b_span"]
        self.assertEqual(doc.text[a_start:a_end],
                         "The export service supports batching.")
        self.assertEqual(doc.text[b_start:b_end],
                         "However, the export service rejects batching.")
        self.assertEqual((a_start, a_end), (0, 37))
        self.assertEqual((b_start, b_end), (38, 83))

    def test_flip_with_one_shared_term_is_medium(self) -> None:
        """A however-flip sharing one content term yields medium only."""
        doc = _run("Our router supports mesh mode. "
                   "However, the printer lacks duplex support.")
        signals = doc.metadata["contradiction_signals"]
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["kind"], "contrast_flip")
        self.assertEqual(signals[0]["confidence"], "medium")
        self.assertEqual(signals[0]["shared_terms"], ["support"])
        self.assertEqual(doc.metadata["contradiction_risk"], "low")

    def test_other_contrast_markers(self) -> None:
        """but / conversely / on the contrary / in contrast all flip."""
        for marker in ("But", "Conversely", "On the contrary,", "In contrast,"):
            with self.subTest(marker=marker):
                doc = _run(f"Batch mode helps throughput. "
                           f"{marker} batch mode hides errors.")
                kinds = _kinds(doc)
                self.assertIn("contrast_flip", kinds)

    def test_cjk_contrast_marker_flips(self) -> None:
        """A sentence opening with 但是 flips a matching earlier claim."""
        doc = _run("系统支持批量导出。但是系统不支持批量导出。")
        signals = doc.metadata["contradiction_signals"]
        self.assertIn("contrast_flip", _kinds(doc))
        flip = next(s for s in signals if s["kind"] == "contrast_flip")
        self.assertEqual(flip["confidence"], "high")
        self.assertEqual(flip["sentence_a_span"], [0, 9])
        self.assertEqual(flip["sentence_b_span"], [9, 21])
        self.assertEqual(
            doc.text[9:21], "但是系统不支持批量导出。")

    def test_cjk_xiangfan_marker_flips(self) -> None:
        """相反 at the start of the later sentence flips too."""
        doc = _run("方案降低了延迟。相反方案提高了延迟。")
        self.assertIn("contrast_flip", _kinds(doc))

    def test_contrast_without_overlap_not_flagged(self) -> None:
        """A however about a different topic produces no signal."""
        doc = _run("Cats sleep most of the day. "
                   "However, the stockmarket rally continued.")
        self.assertEqual(doc.metadata["contradiction_signals"], [])
        self.assertEqual(doc.metadata["signal_count"], 0)
        self.assertEqual(doc.metadata["contradiction_risk"], "none")

    def test_marker_mid_sentence_does_not_flip(self) -> None:
        """A contrast marker NOT at the start of B is not a flip."""
        doc = _run("系统支持导出但是速度很慢。系统不支持导出。")
        self.assertNotIn("contrast_flip", _kinds(doc))
        self.assertIn("negation_repeat", _kinds(doc))


class TestNegationRepeat(unittest.TestCase):
    """negation_repeat: same topic, negation polarity differs."""

    def test_negation_repeat_with_overlap_is_medium(self) -> None:
        """Exactly one negated sentence over shared terms yields medium."""
        doc = _run("The gateway accepts oauth tokens. "
                   "The gateway does not accept oauth tokens.")
        signals = doc.metadata["contradiction_signals"]
        self.assertEqual(len(signals), 1)
        signal = signals[0]
        self.assertEqual(signal["kind"], "negation_repeat")
        self.assertEqual(signal["confidence"], "medium")
        self.assertEqual(signal["shared_terms"],
                         ["accept", "gateway", "oauth", "token"])
        self.assertEqual(doc.metadata["contradiction_risk"], "low")

    def test_negation_repeat_with_one_term_is_low(self) -> None:
        """A single shared term downgrades negation_repeat to low."""
        doc = _run("The printer needs maintenance. The printer never jams.")
        signals = doc.metadata["contradiction_signals"]
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["kind"], "negation_repeat")
        self.assertEqual(signals[0]["confidence"], "low")
        self.assertEqual(signals[0]["shared_terms"], ["printer"])
        self.assertEqual(doc.metadata["contradiction_risk"], "low")

    def test_contraction_negation_counts(self) -> None:
        """n't contractions and cannot act as negation markers."""
        doc = _run("The parser handles nested lists. "
                   "The parser doesn't handle nested lists.")
        self.assertIn("negation_repeat", _kinds(doc))

    def test_cjk_negation_repeat(self) -> None:
        """不 in exactly one of two overlapping sentences diverges."""
        doc = _run("接口返回数据。接口不返回数据。")
        self.assertEqual(_kinds(doc), ["negation_repeat"])

    def test_negation_in_both_not_flagged(self) -> None:
        """Two negated sentences with different openers yield nothing."""
        doc = _run("The primary node is not reachable. "
                   "The standby node is not reachable either.")
        self.assertEqual(doc.metadata["contradiction_signals"], [])
        self.assertEqual(doc.metadata["contradiction_risk"], "none")


class TestMutualNegation(unittest.TestCase):
    """mutual_negation: same opener, both negated, different sentences."""

    def test_same_opener_both_negated_is_low(self) -> None:
        """Identical subject-ish openers with negation flag as low."""
        doc = _run("The agent cannot read pdf files. "
                   "The agent cannot write pdf files.")
        signals = doc.metadata["contradiction_signals"]
        self.assertEqual(len(signals), 1)
        signal = signals[0]
        self.assertEqual(signal["kind"], "mutual_negation")
        self.assertEqual(signal["confidence"], "low")
        self.assertEqual(signal["shared_terms"], ["agent", "file", "pdf"])
        # both sentences negated -> negation_repeat must NOT fire
        self.assertNotIn("negation_repeat", _kinds(doc))

    def test_identical_sentences_not_flagged(self) -> None:
        """A sentence repeated verbatim is not a contradiction."""
        doc = _run("The cache is not updated. The cache is not updated.")
        self.assertEqual(doc.metadata["contradiction_signals"], [])
        self.assertEqual(doc.metadata["contradiction_risk"], "none")

    def test_different_openers_not_mutual(self) -> None:
        """Both-negated sentences with different subjects stay silent."""
        doc = _run("The parser does not support yaml. "
                   "The loader does not support yaml.")
        self.assertEqual(doc.metadata["contradiction_signals"], [])


class TestSignalWindow(unittest.TestCase):
    """Pairs are compared within the configured sentence window."""

    _TEXT_DIST2 = ("Panels ship weekly. Noise sentence alpha. "
                   "However, panels never ship weekly.")
    _TEXT_DIST3 = ("Panels ship weekly. Noise sentence alpha. "
                   "Noise sentence beta. However, panels never ship weekly.")

    def test_distance_two_pair_flagged(self) -> None:
        """Default window 2 pairs sentence 0 with sentence 2."""
        doc = _run(self._TEXT_DIST2)
        kinds = _kinds(doc)
        self.assertEqual(kinds, ["contrast_flip", "negation_repeat"])
        flip = doc.metadata["contradiction_signals"][0]
        self.assertEqual(
            doc.text[flip["sentence_a_span"][0]:flip["sentence_a_span"][1]],
            "Panels ship weekly.")

    def test_distance_three_pair_not_flagged(self) -> None:
        """Beyond the window the same pattern stays silent."""
        doc = _run(self._TEXT_DIST3)
        self.assertEqual(doc.metadata["contradiction_signals"], [])

    def test_window_size_one_excludes_distance_two(self) -> None:
        """window_size=1 compares adjacent sentences only."""
        doc = _run(self._TEXT_DIST2, window_size=1)
        self.assertEqual(doc.metadata["contradiction_signals"], [])

    def test_window_size_one_still_flags_adjacent(self) -> None:
        """Adjacent flips keep working under window_size=1."""
        doc = _run(_FLIP_TEXT, window_size=1)
        self.assertIn("contrast_flip", _kinds(doc))


class TestRiskGrading(unittest.TestCase):
    """contradiction_risk follows the documented weight table."""

    def test_no_signals_is_none(self) -> None:
        """Zero signals grade as none."""
        doc = _run("Everything is fine here.")
        self.assertEqual(doc.metadata["contradiction_risk"], "none")

    def test_weight_one_is_low(self) -> None:
        """A single low signal (weight 1) grades low."""
        doc = _run("The printer needs maintenance. The printer never jams.")
        self.assertEqual(doc.metadata["contradiction_risk"], "low")

    def test_weight_two_is_low(self) -> None:
        """A single medium signal (weight 2) still grades low."""
        doc = _run("The gateway accepts oauth tokens. "
                   "The gateway does not accept oauth tokens.")
        self.assertEqual(doc.metadata["contradiction_risk"], "low")

    def test_weight_three_is_medium(self) -> None:
        """A single high flip (weight 3) grades medium."""
        doc = _run(_FLIP_TEXT)
        self.assertEqual(doc.metadata["contradiction_risk"], "medium")

    def test_weight_six_is_high(self) -> None:
        """Two independent high flips (3 + 3) grade high."""
        doc = _run("The mail gateway supports relaying. "
                   "However, the mail gateway forbids relaying. "
                   "The dns node supports caching. "
                   "However, the dns node disables caching.")
        signals = doc.metadata["contradiction_signals"]
        self.assertEqual([s["kind"] for s in signals],
                         ["contrast_flip", "contrast_flip"])
        self.assertTrue(all(s["confidence"] == "high" for s in signals))
        self.assertEqual(doc.metadata["contradiction_risk"], "high")

    def test_medium_plus_low_reaches_high(self) -> None:
        """Weights add across kinds and documents: 3 + 2 + 1 = high."""
        doc = _run(
            "系统支持批量导出。但是系统不支持批量导出。"
            "The printer needs maintenance. The printer never jams.")
        kinds = _kinds(doc)
        # CJK pair contributes flip(high=3) + negation_repeat(medium=2),
        # the English pair adds negation_repeat(low=1): total weight 6.
        self.assertEqual(kinds, ["contrast_flip", "negation_repeat",
                                 "negation_repeat"])
        self.assertEqual(doc.metadata["contradiction_risk"], "high")


class TestSignalCap(unittest.TestCase):
    """The recorded signal list honors max_signals."""

    @staticmethod
    def _many_claims(count):
        """Build alternating claim/flip sentences with CJK-clean text."""
        parts = []
        for i in range(count):
            parts.append(f"Claim {i}: alpha omega active.")
            parts.append(f"However, claim {i}: alpha omega not active.")
        return " ".join(parts)

    def test_default_cap_thirty(self) -> None:
        """A flood of flips is capped at 30 recorded signals."""
        doc = _run(self._many_claims(40))
        signals = doc.metadata["contradiction_signals"]
        self.assertEqual(len(signals), 30)
        self.assertEqual(doc.metadata["signal_count"], 30)
        self.assertEqual(doc.metadata["contradiction_risk"], "high")

    def test_configured_cap(self) -> None:
        """A smaller max_signals truncates the recorded list."""
        doc = _run(self._many_claims(40), max_signals=5)
        self.assertEqual(len(doc.metadata["contradiction_signals"]), 5)
        self.assertEqual(doc.metadata["signal_count"], 5)


class TestSharedTerms(unittest.TestCase):
    """shared_terms content, ordering, stemming and per-signal cap."""

    def test_terms_sorted_and_capped_at_five(self) -> None:
        """Terms are sorted and at most max_shared_terms are kept."""
        doc = _run("系统支持批量导出。但是系统不支持批量导出。")
        for signal in doc.metadata["contradiction_signals"]:
            terms = signal["shared_terms"]
            self.assertEqual(len(terms), 5)
            self.assertEqual(terms, sorted(terms))

    def test_shared_terms_cap_configurable(self) -> None:
        """max_shared_terms=1 keeps a single term per signal."""
        doc = _run("The gateway accepts oauth tokens. "
                   "The gateway does not accept oauth tokens.",
                   max_shared_terms=1)
        signal = doc.metadata["contradiction_signals"][0]
        self.assertEqual(signal["shared_terms"], ["accept"])

    def test_plural_and_suffix_stems_match(self) -> None:
        """supports/support collapse to the same content term."""
        doc = _run("The api supports retries. "
                   "The api does not support retries.")
        signal = doc.metadata["contradiction_signals"][0]
        self.assertIn("support", signal["shared_terms"])
        self.assertNotIn("supports", signal["shared_terms"])

    def test_ed_and_s_stems_match_across_contrast(self) -> None:
        """exported vs exports overlap on the stem export."""
        doc = _run("Data was exported hourly. "
                   "However, the tool exports nothing.")
        signals = doc.metadata["contradiction_signals"]
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["kind"], "contrast_flip")
        self.assertEqual(signals[0]["shared_terms"], ["export"])
        self.assertEqual(signals[0]["confidence"], "medium")

    def test_stemmer_documented_behaviors(self) -> None:
        """Direct checks of the crude suffix-stripping stemmer."""
        stem = csd_module._stem
        self.assertEqual(stem("supports"), "support")
        self.assertEqual(stem("exported"), "export")
        self.assertEqual(stem("exports"), "export")
        self.assertEqual(stem("watches"), "watch")
        self.assertEqual(stem("batches"), "batch")
        self.assertEqual(stem("files"), "file")
        self.assertEqual(stem("file"), "file")
        # doubled consonants are not repaired (documented)
        self.assertEqual(stem("running"), "runn")
        # stems shorter than three letters refuse to strip
        self.assertEqual(stem("goes"), "goe")
        self.assertEqual(stem("using"), "using")
        self.assertEqual(stem("class"), "class")
        self.assertEqual(stem("bus"), "bus")


class TestPassthroughBehaviour(unittest.TestCase):
    """Documents pass through untouched; metadata is stamped safely."""

    def test_text_and_id_unchanged(self) -> None:
        """Text, id and existing metadata survive the scan."""
        original = Document(text=_FLIP_TEXT, metadata={"source": "faq"})
        out = ContradictionSignalDetector() \
            .process_docs([original])[0]
        self.assertEqual(out.text, _FLIP_TEXT)
        self.assertEqual(out.id, original.id)
        self.assertEqual(out.metadata["source"], "faq")
        self.assertIn("contradiction_signals", out.metadata)

    def test_empty_text_stamped_none(self) -> None:
        """Empty text yields no signals and a none grade."""
        doc = _run("")
        self.assertEqual(doc.metadata["contradiction_signals"], [])
        self.assertEqual(doc.metadata["signal_count"], 0)
        self.assertEqual(doc.metadata["contradiction_risk"], "none")

    def test_batch_order_and_length_preserved(self) -> None:
        """Every document is returned, once, in batch order."""
        docs = [Document(text=_FLIP_TEXT),
                Document(text="Nothing suspicious at all."),
                Document(text="The printer needs maintenance. "
                              "The printer never jams.")]
        out = ContradictionSignalDetector().process_docs(docs)
        self.assertEqual([d.id for d in out], [d.id for d in docs])
        self.assertEqual(out[1].metadata["contradiction_risk"], "none")
        self.assertEqual(out[2].metadata["contradiction_risk"], "low")

    def test_query_argument_accepted(self) -> None:
        """The optional query argument is accepted and ignored."""
        doc = _run(_FLIP_TEXT, query=Query(query_str="export policy"))
        self.assertEqual(doc.metadata["signal_count"], 1)

    def test_custom_metadata_keys(self) -> None:
        """All three metadata keys are configurable."""
        doc = _run(_FLIP_TEXT, signals_key="flags", count_key="flags_n",
                   risk_key="flags_risk")
        self.assertIn("flags", doc.metadata)
        self.assertEqual(doc.metadata["flags_n"], 1)
        self.assertEqual(doc.metadata["flags_risk"], "medium")
        self.assertNotIn("contradiction_signals", doc.metadata)

    def test_empty_key_disables_stamping(self) -> None:
        """An empty signals_key omits the list but keeps count and risk."""
        doc = _run(_FLIP_TEXT, signals_key="")
        self.assertNotIn("contradiction_signals", doc.metadata)
        self.assertEqual(doc.metadata["signal_count"], 1)
        self.assertEqual(doc.metadata["contradiction_risk"], "medium")

    def test_deterministic_output(self) -> None:
        """Repeated runs over identical docs produce identical metadata."""
        docs_a = [Document(text=t) for t in (_FLIP_TEXT, "系统支持批量导出。"
                                            "但是系统不支持批量导出。")]
        docs_b = [Document(text=t) for t in (_FLIP_TEXT, "系统支持批量导出。"
                                            "但是系统不支持批量导出。")]
        ContradictionSignalDetector().process_docs(docs_a)
        ContradictionSignalDetector().process_docs(docs_b)
        self.assertEqual([d.metadata for d in docs_a],
                         [d.metadata for d in docs_b])


class TestConfigurationValidation(unittest.TestCase):
    """Component config is validated eagerly at initialization."""

    @staticmethod
    def _detector(**config):
        """Build a detector through the component configer path."""
        configer = SimpleNamespace(
            name="csd", description="d", **config)
        return ContradictionSignalDetector() \
            ._initialize_by_component_configer(configer)

    def test_valid_config_applies(self) -> None:
        """Valid values populate the detector attributes."""
        proc = self._detector(window_size=1, max_signals=7,
                              max_shared_terms=2, signals_key="flags",
                              count_key="n", risk_key="r")
        self.assertEqual(proc.window_size, 1)
        self.assertEqual(proc.max_signals, 7)
        self.assertEqual(proc.max_shared_terms, 2)
        self.assertEqual(proc.signals_key, "flags")
        self.assertEqual(proc.count_key, "n")
        self.assertEqual(proc.risk_key, "r")
        self.assertEqual(proc.name, "csd")

    def test_bad_window_size_rejected(self) -> None:
        """window_size must be an integer within [1, 5]."""
        for bad in (0, 6, "2", 2.0, True):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self._detector(window_size=bad)

    def test_bad_max_signals_rejected(self) -> None:
        """max_signals must be an integer within [1, 1000]."""
        for bad in (0, 1001, "5", False):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self._detector(max_signals=bad)

    def test_bad_max_shared_terms_rejected(self) -> None:
        """max_shared_terms must be an integer within [1, 20]."""
        for bad in (0, 21, 1.5):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self._detector(max_shared_terms=bad)

    def test_bad_key_type_rejected(self) -> None:
        """Metadata keys must be strings."""
        with self.assertRaises(ValueError):
            self._detector(signals_key=5)
        with self.assertRaises(ValueError):
            self._detector(risk_key=["r"])


class TestContradictionRegistration(unittest.TestCase):
    """The shipped yaml resolves through the real framework loader."""

    def test_yaml_resolves_to_doc_processor_type(self) -> None:
        """The shipped yaml registers as a DOC_PROCESSOR component type."""
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.get_component_config_type(),
            ComponentEnum.DOC_PROCESSOR.value)

    def test_yaml_exposes_module_and_class(self) -> None:
        """The shipped yaml points at the ContradictionSignalDetector."""
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.metadata_module,
            "agentuniverse.agent.action.knowledge.doc_processor."
            "contradiction_signal_detector")
        self.assertEqual(component_configer.metadata_class,
                         "ContradictionSignalDetector")

    def test_signal_record_shape(self) -> None:
        """Every signal record carries exactly the documented keys."""
        doc = _run(_FLIP_TEXT)
        signal = doc.metadata["contradiction_signals"][0]
        self.assertEqual(set(signal.keys()),
                         {"kind", "sentence_a_span", "sentence_b_span",
                          "shared_terms", "confidence"})
        self.assertIsInstance(signal["sentence_a_span"], list)
        self.assertEqual(len(signal["sentence_a_span"]), 2)
        self.assertIsInstance(signal["sentence_b_span"], list)
        self.assertEqual(len(signal["sentence_b_span"]), 2)


if __name__ == '__main__':
    unittest.main()
