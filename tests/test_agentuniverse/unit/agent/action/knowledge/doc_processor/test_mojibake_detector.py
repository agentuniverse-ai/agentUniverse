# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_mojibake_detector.py

import copy
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.mojibake_detector import MojibakeDetector
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _latin1(text: str) -> str:
    """Corrupt text exactly the way a UTF-8-as-Latin-1 misread does."""
    return text.encode("utf-8").decode("latin-1")


def _cp1252(text: str) -> str:
    """Corrupt text exactly the way a UTF-8-as-CP1252 misread does."""
    return text.encode("utf-8").decode("cp1252")


# Authentic corrupted ground truths (generated through real codecs).
CHINESE_MOJIBAKE = _latin1("中文文本")            # 4 hits, len 12
PORTUGUESE_MOJIBAKE = _latin1("São Paulo é linda")  # 2 hits
CURLY_MOJIBAKE = _cp1252("don’t “think — it’s fine…")  # 5 hits
EMOJI_MOJIBAKE = _cp1252("hi 😀 there")            # 1 four-byte hit
LATIN1_CURLY_TWICE = _latin1("don’t") + " " + _latin1("don’t")  # 2 hits

# Legitimate European prose that must stay clean (false-positive guards).
PORTUGUESE_CLEAN = "São Paulo é uma cidade à beira-mar, ótima para visitar"
GERMAN_CLEAN = "der schönste Lauf läuft übermäßigen Ärger mit üblen Mühen"
NORDIC_CLEAN = "i året på åsen finns en sjö med flott öga mot façaden"
FRENCH_GUILLEMETS_CLEAN = "il a dit «ça va» puis «très bien» à café"
ASCII_CLEAN = "The quick brown fox jumps over the lazy dog."


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestMojibakeDetector(unittest.TestCase):
    """Comprehensive test suite for MojibakeDetector."""

    def setUp(self):
        self.detector = MojibakeDetector()
        self.query = Query(query_str="encoding")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _kinds(self, text):
        """Findings of `text` as a {kind: count} mapping."""
        findings, _, _ = self.detector._analyze(text)
        return {f["kind"]: f["count"] for f in findings}

    def _verdict(self, text):
        """Verdict of `text` under default configuration."""
        return self.detector._analyze(text)[2]

    def _score(self, text):
        """Score of `text` under default configuration."""
        return self.detector._analyze(text)[1]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: 0.5/5.0 thresholds, stamp-only mode, standard keys,
        no disabled signals."""
        d = MojibakeDetector()
        self.assertEqual(d.clean_below, 0.5)
        self.assertEqual(d.corrupted_above, 5.0)
        self.assertFalse(d.drop_corrupted)
        self.assertEqual(d.score_key, "mojibake_score")
        self.assertEqual(d.verdict_key, "mojibake_verdict")
        self.assertEqual(d.findings_key, "mojibake_findings")
        self.assertEqual(d.disabled_signals, [])

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'mojibake_detector',
            'description': 'mojibake detector',
            'clean_below': 1.0,
            'corrupted_above': 10.0,
            'drop_corrupted': True,
            'score_key': 'enc_score',
            'verdict_key': 'enc_verdict',
            'findings_key': 'enc_findings',
            'disabled_signals': ['percent_encoding', 'html_entity'],
        })
        d = MojibakeDetector()
        d._initialize_by_component_configer(configer)
        self.assertEqual(d.clean_below, 1.0)
        self.assertEqual(d.corrupted_above, 10.0)
        self.assertTrue(d.drop_corrupted)
        self.assertEqual(d.score_key, 'enc_score')
        self.assertEqual(d.verdict_key, 'enc_verdict')
        self.assertEqual(d.findings_key, 'enc_findings')
        self.assertEqual(d.disabled_signals,
                         ['percent_encoding', 'html_entity'])
        self.assertEqual(d.name, 'mojibake_detector')

    def test_invalid_configuration_raises(self):
        """Non-numeric/negative thresholds, inverted threshold order,
        non-string keys and malformed disabled_signals all fail eagerly."""
        base = {'name': 'd', 'description': 'x'}
        cases = [
            {'clean_below': 'high'},
            {'clean_below': True},
            {'clean_below': -0.1},
            {'corrupted_above': 'low'},
            {'corrupted_above': 0.4},           # <= default clean_below 0.5
            {'clean_below': 5.0},               # not < default corrupted 5
            {'score_key': 7},
            {'verdict_key': []},
            {'findings_key': {}},
            {'disabled_signals': 'percent_encoding'},
            {'disabled_signals': ['nonsense']},
            {'disabled_signals': [42]},
        ]
        for extra in cases:
            with self.subTest(extra=extra):
                configer = self._create_configer({**base, **extra})
                with self.assertRaises(ValueError):
                    MojibakeDetector()._initialize_by_component_configer(
                        configer)

    # ========== Ground-truth detection tests ==========

    def test_detects_utf8_read_as_latin1_chinese(self):
        """Real UTF-8-as-Latin-1 corruption of CJK text: 4 hits (one per
        character), corrupted verdict, exact normalized score."""
        self.assertEqual(self._kinds(CHINESE_MOJIBAKE),
                         {"utf8_as_latin1": 4})
        self.assertEqual(self._verdict(CHINESE_MOJIBAKE), "corrupted")
        self.assertEqual(self._score(CHINESE_MOJIBAKE),
                         round(4 * 1.0 * 1000 / len(CHINESE_MOJIBAKE), 2))

    def test_detects_utf8_read_as_latin1_european(self):
        """Accented Latin text misread as Latin-1 (São -> SÃ£o, é -> Ã©)
        crosses the two-hit minimum and is flagged corrupted."""
        self.assertEqual(self._kinds(PORTUGUESE_MOJIBAKE),
                         {"utf8_as_latin1": 2})
        self.assertEqual(self._verdict(PORTUGUESE_MOJIBAKE), "corrupted")

    def test_detects_utf8_read_as_cp1252_signatures(self):
        """Curly quotes / dashes / ellipsis misread as CP1252 produce the
        classic â€™ â€œ â€" â€¦ artifacts under the cp1252 signal."""
        self.assertEqual(self._kinds(CURLY_MOJIBAKE),
                         {"utf8_as_cp1252": 5})
        self.assertEqual(self._verdict(CURLY_MOJIBAKE), "corrupted")
        self.assertIn("â€™", CURLY_MOJIBAKE)
        self.assertIn("â€œ", CURLY_MOJIBAKE)
        self.assertIn("â€¦", CURLY_MOJIBAKE)

    def test_detects_cp1252_four_byte_emoji(self):
        """An emoji misread as CP1252 (ðŸ˜€) is a single four-byte hit and
        still yields a corrupted verdict."""
        self.assertEqual(self._kinds(EMOJI_MOJIBAKE),
                         {"utf8_as_cp1252": 1})
        self.assertEqual(self._verdict(EMOJI_MOJIBAKE), "corrupted")

    def test_detects_cp1252_undefined_byte_controls(self):
        """Tolerant CP1252 decoders pass undefined bytes (0x9D) through as
        controls; â€\x9d (from ”) still matches the cp1252 pattern."""
        tolerant = "â€\u009d and â€\u009d"
        self.assertEqual(self._kinds(tolerant), {"utf8_as_cp1252": 2})

    def test_latin1_hits_shadow_cp1252_no_double_count(self):
        """A misread counted under the Latin-1 signal is not counted again
        under CP1252: curly quotes decoded via Latin-1 (â + controls) appear
        only as utf8_as_latin1 findings."""
        self.assertEqual(self._kinds(LATIN1_CURLY_TWICE),
                         {"utf8_as_latin1": 2})

    def test_single_strong_cp1252_hit_qualifies_alone(self):
        """A hit with at least two C1-mapped continuations (â€™, ðŸ˜€) is
        unambiguous corruption and qualifies the signal on its own."""
        self.assertEqual(self._kinds("donâ€™t"),
                         {"utf8_as_cp1252": 1})
        self.assertEqual(self._verdict("donâ€™t"), "corrupted")
        self.assertEqual(self._kinds(EMOJI_MOJIBAKE),
                         {"utf8_as_cp1252": 1})

    def test_single_weak_cp1252_hit_stays_clean(self):
        """A hit whose continuations include only one C1-mapped character
        (â€¦, the shape of the ellipsis artifact) is ambiguous — French
        «café»… prose produces the identical é»… shape — so a lone weak
        hit does not flag, mirroring the Latin-1 two-hit guard."""
        # Real corruption, single weak artifact: stays clean by design.
        self.assertEqual(self._kinds("waitâ€¦ what"), {})
        self.assertEqual(self._verdict("waitâ€¦ what"), "clean")
        # Legitimate French typography with the same shape: clean.
        french = "Il murmura «j’ai préféré ce café-là»… puis partit."
        self.assertEqual(self._kinds(french), {})
        self.assertEqual(self._verdict(french), "clean")
        # Two weak hits — corruption or typography — do flag.
        self.assertEqual(self._kinds("waitâ€¦ whatâ€¦ hmm"),
                         {"utf8_as_cp1252": 2})
        self.assertEqual(self._verdict("waitâ€¦ whatâ€¦ hmm"), "corrupted")

    def test_detects_replacement_characters(self):
        """U+FFFD replacement characters are counted 1:1 with the loudest
        weight."""
        text = "abc\ufffddef\ufffdghi"
        self.assertEqual(self._kinds(text), {"replacement_char": 2})
        self.assertEqual(self._score(text),
                         round(2 * 2.0 * 1000 / len(text), 2))
        self.assertEqual(self._verdict(text), "corrupted")

    def test_detects_percent_encoding_residue(self):
        """Percent-escape runs (>= 4 chars) flag the document, one %XX
        unit per hit; lone %XX pairs stay silent."""
        residue = "a=1&b=%E4%B8%AD&c=%E6%96%87"
        # Two runs of three %XX units each -> six unit hits.
        self.assertEqual(self._kinds(residue), {"percent_encoding": 6})
        self.assertEqual(self._score(residue),
                         round(6 * 0.5 * 1000 / len(residue), 2))

        # A single contiguous blob weighs the same evidence as the same
        # bytes split across runs; it must not fall below the two-hit
        # minimum just because it is contiguous.
        blob = "error: %E5%8F%82%E6%95%B0%E9%94%99%E8%AF%AF fixed"
        self.assertEqual(self._kinds(blob), {"percent_encoding": 12})
        self.assertEqual(self._verdict(blob), "corrupted")

        single_url = "see https://example.com/wiki/%E4%B8%AD for details"
        self.assertEqual(self._kinds(single_url), {})
        self.assertEqual(self._score(single_url), 0.0)

        stray = "battery at 45% E4ff and 3% OFF today"
        self.assertEqual(self._kinds(stray), {})

    def test_urls_with_percent_escapes_never_score(self):
        """Correctly escaped URLs are healthy text: percent runs inside
        URL tokens (whitespace-delimited tokens containing '://') are
        exempt no matter how many segments or parameters they escape."""
        urls = [
            "docs: https://example.com/wiki/%E4%B8%AD/%E6%96%87 end",
            "compare https://a.io/%E4%B8%AD and https://b.io/%E8%8B%B1",
            "search https://example.com/search?q=%E4%B8%AD&x=%E6%96%87",
            "download http://files.io/a%20b%20c%20d%20e%20f.txt now",
            "See [中文](https://zh.wikipedia.org/wiki/%E4%B8%AD%E6%96%87)",
        ]
        for text in urls:
            with self.subTest(text=text):
                self.assertEqual(self._kinds(text), {})
                self.assertEqual(self._score(text), 0.0)
                self.assertEqual(self._verdict(text), "clean")

        # Residue outside a URL token still counts on the same document.
        mixed = ("source: https://log.io/view?u=%2Ftmp body: "
                 "%E5%8F%82%E6%95%B0 bad")
        self.assertEqual(self._kinds(mixed), {"percent_encoding": 6})

    def test_detects_html_entity_residue(self):
        """Numeric character references and double-escaping runs are
        residue; a single named entity is not."""
        numeric = "mix &#x4E2D;&#25991; entities"
        self.assertEqual(self._kinds(numeric), {"html_entity": 2})
        self.assertEqual(self._score(numeric),
                         round(2 * 0.25 * 1000 / len(numeric), 2))

        escaped = "a &amp;amp; b &amp;lt; c"
        self.assertEqual(self._kinds(escaped), {"html_entity": 2})

        single = "just one &amp; entity here"
        self.assertEqual(self._kinds(single), {})
        self.assertEqual(self._score(single), 0.0)

    def test_single_latin1_bigram_stays_clean(self):
        """One ambiguous bigram (cafÃ© alone) does not flag: the Latin-1
        signal requires two hits."""
        self.assertEqual(self._kinds("cafÃ©"), {})
        self.assertEqual(self._verdict("cafÃ©"), "clean")

    # ========== False-positive guards ==========

    def test_legitimate_european_text_is_clean(self):
        """Portuguese, German, Nordic and French prose containing lawful
        ã é ü ö å ä ç « » characters yield no findings and verdict clean."""
        for name, text in [
            ("portuguese", PORTUGUESE_CLEAN),
            ("german", GERMAN_CLEAN),
            ("nordic", NORDIC_CLEAN),
            ("french-guillemets", FRENCH_GUILLEMETS_CLEAN),
            ("ascii", ASCII_CLEAN),
        ]:
            with self.subTest(language=name):
                findings, score, verdict = self.detector._analyze(text)
                self.assertEqual(findings, [])
                self.assertEqual(score, 0.0)
                self.assertEqual(verdict, "clean")

    def test_lead_char_followed_by_ascii_is_not_a_hit(self):
        """The patterns require the second character to sit in the
        continuation range: Ã© matches, Ãa does not."""
        self.assertEqual(self._kinds("Ãa Ão Ãe Ãu"), {})

    def test_plain_text_with_ampersand_and_percent(self):
        """Ordinary ampersands, percentages and quotes never score."""
        text = "AT&T charges 50% & more, isn't it \"fine\"?"
        self.assertEqual(self._score(text), 0.0)
        self.assertEqual(self._verdict(text), "clean")

    # ========== Score normalization and verdict boundaries ==========

    def test_score_is_a_per_1000_character_rate(self):
        """One replacement character in 5000 characters is clean (0.4),
        in 4000 exactly hits the clean boundary (0.5 -> suspect), and the
        same evidence in a tiny string is corrupted."""
        diluted = "x" * 4999 + "\ufffd"
        self.assertEqual(self._score(diluted), 0.4)
        self.assertEqual(self._verdict(diluted), "clean")

        boundary = "x" * 4000 + "\ufffd"
        self.assertEqual(self._score(boundary), 0.5)
        self.assertEqual(self._verdict(boundary), "suspect")

        dense = "x\ufffd"
        self.assertEqual(self._score(dense), 1000.0)
        self.assertEqual(self._verdict(dense), "corrupted")

    def test_verdict_boundaries_are_inclusive(self):
        """Score == corrupted_above is suspect, one step above is
        corrupted; score == clean_below is suspect, below is clean."""
        # 5 hits over 2000 chars -> round(5*2.0*1000/2000, 2) == 5.0
        text = "\ufffd" * 5 + "x" * 1995
        self.assertEqual(len(text), 2000)
        self.assertEqual(self._score(text), 5.0)
        self.assertEqual(self._verdict(text), "suspect")

        text = "\ufffd" * 6 + "x" * 1994
        self.assertEqual(self._score(text), 6.0)
        self.assertEqual(self._verdict(text), "corrupted")

    def test_configurable_thresholds_move_verdicts(self):
        """Custom thresholds reclassify identical evidence."""
        configer = self._create_configer({
            'name': 'd', 'description': 'x',
            'clean_below': 2.5, 'corrupted_above': 50.0,
        })
        d = MojibakeDetector()
        d._initialize_by_component_configer(configer)
        score = 2.0
        self.assertEqual(d._verdict(score), "clean")

        configer = self._create_configer({
            'name': 'd', 'description': 'x',
            'clean_below': 0.5, 'corrupted_above': 1.5,
        })
        d = MojibakeDetector()
        d._initialize_by_component_configer(configer)
        self.assertEqual(d._verdict(2.0), "corrupted")

    def test_score_rounding_and_zero_length(self):
        """Scores are rounded to two decimals; empty text scores 0.0 and
        is clean."""
        findings, score, verdict = self.detector._analyze("")
        self.assertEqual(score, 0.0)
        self.assertEqual(verdict, "clean")
        self.assertEqual(findings, [])
        self.assertIsInstance(score, float)

    # ========== Findings structure ==========

    def test_findings_structure_and_sample_cap(self):
        """Findings carry kind/count/samples with at most three samples;
        snippets include context and spans mark the matches."""
        findings = self.detector._analyze(CHINESE_MOJIBAKE)[0]
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding["kind"], "utf8_as_latin1")
        self.assertEqual(finding["count"], 4)
        self.assertEqual(len(finding["samples"]), 3)
        for sample in finding["samples"]:
            start, end = sample["start"], sample["end"]
            self.assertEqual(
                sample["snippet"],
                CHINESE_MOJIBAKE[max(0, start - 10):
                                 min(len(CHINESE_MOJIBAKE), end + 10)])
            self.assertTrue(0 <= start < end <= len(CHINESE_MOJIBAKE))
        self.assertEqual([s["start"] for s in finding["samples"]], [0, 3, 6])

    def test_findings_order_is_canonical_and_deterministic(self):
        """Multiple signals appear in canonical order and identical runs
        produce identical results."""
        text = (CHINESE_MOJIBAKE + "\ufffd\ufffd"
                + " &a=%E4%B8%AD&b=%E6%96%87")
        first = self.detector._analyze(text)
        second = self.detector._analyze(text)
        other = MojibakeDetector()._analyze(text)
        self.assertEqual(first, second)
        self.assertEqual(first, other)
        self.assertEqual([f["kind"] for f in first[0]],
                         ["replacement_char", "utf8_as_latin1",
                          "percent_encoding"])

    def test_disabled_signals_skip_analysis(self):
        """Disabling a signal removes its findings and its score share."""
        configer = self._create_configer({
            'name': 'd', 'description': 'x',
            'disabled_signals': ['percent_encoding'],
        })
        d = MojibakeDetector()
        d._initialize_by_component_configer(configer)
        residue = "a=1&b=%E4%B8%AD&c=%E6%96%87"
        findings, score, verdict = d._analyze(residue)
        self.assertEqual(findings, [])
        self.assertEqual(score, 0.0)
        self.assertEqual(verdict, "clean")
        # The Latin-1 signal still fires on the same detector.
        self.assertEqual(
            {f["kind"]: f["count"] for f in d._analyze(
                CHINESE_MOJIBAKE)[0]},
            {"utf8_as_latin1": 4})

    # ========== Document pipeline behavior ==========

    def test_stamp_only_mode_keeps_every_document(self):
        """Default mode stamps and returns all documents in order."""
        docs = [_doc(CHINESE_MOJIBAKE, src="crawl"),
                _doc(PORTUGUESE_CLEAN, src="crawl")]
        result = self.detector.process_docs(docs, self.query)
        self.assertEqual(len(result), 2)
        self.assertIs(result[0], docs[0])
        self.assertEqual(result[0].metadata["mojibake_verdict"], "corrupted")
        self.assertEqual(result[1].metadata["mojibake_verdict"], "clean")
        self.assertEqual(result[1].metadata["mojibake_score"], 0.0)
        self.assertEqual(result[1].metadata["mojibake_findings"], [])

    def test_drop_corrupted_mode_filters_only_corrupted(self):
        """Filter mode drops corrupted documents but keeps clean and
        suspect ones, preserving order; dropped originals keep stamps."""
        configer = self._create_configer({
            'name': 'd', 'description': 'x', 'drop_corrupted': True,
        })
        d = MojibakeDetector()
        d._initialize_by_component_configer(configer)
        suspect_text = "x" * 4000 + "\ufffd"   # score 0.5 -> suspect
        docs = [_doc(PORTUGUESE_CLEAN), _doc(CHINESE_MOJIBAKE),
                _doc(suspect_text), _doc(ASCII_CLEAN)]
        result = d.process_docs(docs)
        self.assertEqual([doc.text for doc in result],
                         [PORTUGUESE_CLEAN, suspect_text, ASCII_CLEAN])
        self.assertEqual(docs[1].metadata["mojibake_verdict"], "corrupted")
        self.assertNotIn(docs[1], result)

    def test_text_and_id_are_never_modified(self):
        """Detection never rewrites text or ids, corrupt or not."""
        docs = [_doc(CHINESE_MOJIBAKE), _doc(CURLY_MOJIBAKE),
                _doc(PORTUGUESE_CLEAN)]
        originals = [(doc.id, copy.deepcopy(doc.text)) for doc in docs]
        self.detector.process_docs(docs, self.query)
        for doc, (doc_id, text) in zip(docs, originals):
            self.assertEqual(doc.id, doc_id)
            self.assertEqual(doc.text, text)

    def test_metadata_is_copied_before_mutation(self):
        """Existing metadata survives, new keys are added, and the mapping
        originally handed to the document is not touched in place."""
        shared = {"src": "web", "lang": "pt"}
        doc = Document(text=CHINESE_MOJIBAKE, metadata=shared)
        self.detector.process_docs([doc])
        self.assertEqual(doc.metadata["src"], "web")
        self.assertEqual(doc.metadata["lang"], "pt")
        self.assertIn("mojibake_score", doc.metadata)
        self.assertIn("mojibake_verdict", doc.metadata)
        self.assertIn("mojibake_findings", doc.metadata)
        self.assertIsNot(doc.metadata, shared)
        self.assertNotIn("mojibake_score", shared)

    def test_custom_and_empty_metadata_keys(self):
        """Keys are configurable; an empty key disables that stamp."""
        configer = self._create_configer({
            'name': 'd', 'description': 'x',
            'score_key': 'enc_score', 'verdict_key': '',
            'findings_key': 'enc_findings',
        })
        d = MojibakeDetector()
        d._initialize_by_component_configer(configer)
        doc = _doc(CHINESE_MOJIBAKE)
        d.process_docs([doc])
        self.assertIn("enc_score", doc.metadata)
        self.assertIn("enc_findings", doc.metadata)
        self.assertNotIn("mojibake_verdict", doc.metadata)
        self.assertNotIn("enc_verdict", doc.metadata)

    def test_none_text_and_empty_batch(self):
        """None text analyses as empty (clean) and empty batches pass
        through unchanged."""
        findings, score, verdict = self.detector._analyze(None)
        self.assertEqual((findings, score, verdict), ([], 0.0, "clean"))
        doc = Document(text="")
        result = self.detector.process_docs([doc])
        self.assertEqual(len(result), 1)
        self.assertEqual(doc.metadata["mojibake_score"], 0.0)
        self.assertEqual(doc.metadata["mojibake_verdict"], "clean")
        self.assertEqual(doc.metadata["mojibake_findings"], [])
        self.assertEqual(self.detector.process_docs([]), [])

    def test_query_is_ignored(self):
        """The optional query never influences analysis."""
        docs = [_doc(CHINESE_MOJIBAKE)]
        without = self.detector.process_docs(docs)
        with_query = self.detector.process_docs(
            [_doc(CHINESE_MOJIBAKE)], Query(query_str="anything"))
        self.assertEqual(without[0].metadata, with_query[0].metadata)


if __name__ == "__main__":
    unittest.main()
