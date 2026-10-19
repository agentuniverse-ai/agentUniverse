# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_reading_level_scorer.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.reading_level_scorer import ReadingLevelScorer
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Twelve monosyllabic words in two six-word sentences.
# Hand counts: W=12, S=2, Y=12, complex=0 -> W/S=6.0, Y/W=1.0.
SIMPLE = "The cat sat on the mat. The dog ran to the pen."

# Academic-register prose of the same word count.
# Hand counts (heuristic): W=30, S=2, Y=114, complex=24.
ACADEMIC = (
    "Consequently, the interdisciplinary investigation demonstrated that "
    "institutional implementations of asynchronous communication "
    "technologies necessitate comprehensive evaluation methodologies. "
    "Furthermore, researchers established statistically significant "
    "correlations between organizational transformation and perceived "
    "individual productivity deterioration."
)

# Polysyllabic one-sentence probe.
# Hand counts: the=1, interdisciplinary=7, committee=2 (silent terminal e),
# organized=3 (-ed after 'z' is silent), unnecessary=5, evaluations=4
# -> W=6, S=1, Y=22; complex = all except 'The' and 'committee' -> 4.
POLY = "The interdisciplinary committee organized unnecessary evaluations."

# Proper-noun exclusion pair: identical except the capitalization of
# 'philadelphia'; committee=2 syllables is not complex, organization=5 is.
PROP_CAPS = "The Philadelphia committee met the organization."
PROP_LOWER = "The philadelphia committee met the organization."

# Hyphenation pair: no part of 'state-of-the-art' reaches 3 syllables,
# while 'computer' alone does for the compound variant.
HYPHEN_SIMPLE = "The state-of-the-art system works."
HYPHEN_COMPLEX = "The computer-communication-application system works."

# Abbreviation guard probe: 'Dr.', 'p.m.' must not split sentences.
# Hand counts: W=13 (dr smith went to washington | he arrived at 3 p m on
# tuesday), S=2, Y=16 (dr clamps to 1, washington=3, arrived=2, tuesday=2).
ABBREV = "Dr. Smith went to Washington. He arrived at 3 p.m. on Tuesday."

# Pure CJK: 9 + 7 = 16 characters (each a word), 2 sentences, 0 syllables.
CJK = "机器学习改变了世界。它正在加速发展！"

# CJK characters are 2 of 23 letters (ratio 0.087 <= 0.3): Latin path.
MIXED_LOW = "The report mentions 研究 once."

# CJK characters are 7 of 13 letters (ratio 0.538 > 0.3): non-Latin path.
MIXED_HIGH = "See 研究方向和目标 now."


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestReadingLevelScorer(unittest.TestCase):
    """Comprehensive test suite for ReadingLevelScorer."""

    def setUp(self):
        self.scorer = ReadingLevelScorer()
        self.query = Query(query_str="readability")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: no grade bounds (stamp only), 'reading_level' and
        'readability_note' metadata keys."""
        s = ReadingLevelScorer()
        self.assertIsNone(s.min_grade)
        self.assertIsNone(s.max_grade)
        self.assertEqual(s.reading_level_key, "reading_level")
        self.assertEqual(s.note_key, "readability_note")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'reading_level_scorer',
            'description': 'reading level scorer',
            'min_grade': 1,
            'max_grade': 12.5,
            'reading_level_key': 'level',
            'note_key': 'note',
        })
        s = ReadingLevelScorer()
        s._initialize_by_component_configer(configer)
        self.assertEqual(s.min_grade, 1.0)
        self.assertEqual(s.max_grade, 12.5)
        self.assertEqual(s.reading_level_key, "level")
        self.assertEqual(s.note_key, "note")
        self.assertEqual(s.name, "reading_level_scorer")

    def test_invalid_configuration_raises(self):
        """Non-number grades, bools, an empty grade range and non-string
        metadata keys all fail at load time."""
        base = {
            'name': 'r', 'description': 'd',
            'min_grade': None, 'max_grade': None,
            'reading_level_key': 'reading_level', 'note_key': 'note',
        }
        cases = [
            {'min_grade': 'six'},
            {'min_grade': True},
            {'max_grade': []},
            {'max_grade': '9'},
            {'min_grade': 5, 'max_grade': 3},  # empty grade range
            {'reading_level_key': 5},
            {'note_key': ['x']},
        ]
        for delta in cases:
            config = dict(base, **delta)
            with self.assertRaises(ValueError, msg=f"{delta!r}"):
                ReadingLevelScorer()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Syllable heuristic tests ==========

    def test_syllable_counts_pinned(self):
        """Hand-verified syllable estimates for the standard heuristic:
        vowel groups, silent terminal e (kept for -le), silent -ed unless
        after t/d; every lettered token counts at least one syllable."""
        cases = {
            "reading": 2,            # rea-ding
            "algorithm": 3,          # heuristic; true count is 4
            "committee": 2,          # heuristic; terminal e subtracted
            "the": 1, "cat": 1, "bee": 1, "hmm": 1,
            "table": 2, "simple": 2, "made": 1,
            "jumped": 1, "wanted": 2, "organized": 3,
            "washington": 3, "arrived": 2, "tuesday": 2,
            "organization": 5, "philadelphia": 4,
            "interdisciplinary": 7, "unnecessary": 5, "evaluations": 4,
            "science": 1, "idea": 2,
            "state-of-the-art": 3,  # hyphens stripped: stateoftheart
            "123": 0, "研究": 0, "": 0,
        }
        for word, expected in cases.items():
            self.assertEqual(ReadingLevelScorer._token_syllables(word),
                             expected, word)

    def test_syllables_are_case_insensitive(self):
        """Capitalization never changes the syllable estimate."""
        for word in ("Reading", "WASHINGTON", "TaBLe"):
            self.assertEqual(ReadingLevelScorer._token_syllables(word),
                             ReadingLevelScorer._token_syllables(word.lower()),
                             word)

    # ========== Sentence segmentation tests ==========

    def test_sentence_splitting_basic(self):
        """ASCII terminators split only when followed by whitespace or end
        of text; terminator runs collapse; unterminated tails count."""
        split = ReadingLevelScorer._split_sentences
        self.assertEqual(len(split(SIMPLE)), 2)
        self.assertEqual(
            len(split("One space.  Two spaces!!! And a third? End")), 4)
        self.assertEqual(len(split("just words no terminator")), 1)
        self.assertEqual(len(split("")), 0)

    def test_sentence_splitting_abbreviations_guarded(self):
        """Known abbreviations, multi-dot forms and single uppercase
        initials do not end sentences; decimals never split."""
        split = ReadingLevelScorer._split_sentences
        self.assertEqual(len(split(ABBREV)), 2)  # Dr. / p.m. guarded
        self.assertEqual(
            len(split("Mr. J. Smith Jr. visited the U.S. capital. "
                      "It rained.")), 2)
        self.assertEqual(len(split("This is e.g. a test. Another sentence "
                                   "here.")), 2)
        self.assertEqual(len(split("The value of pi is 3.14 exactly. "
                                   "Yes!")), 2)  # 3.14 never splits
        self.assertEqual(len(split("etc. and so on. Next one.")), 2)

    def test_sentence_splitting_cjk(self):
        """CJK terminators split without requiring trailing whitespace."""
        split = ReadingLevelScorer._split_sentences
        self.assertEqual(len(split(CJK)), 2)
        self.assertEqual(split("你好。世界！"),
                         ["你好。", "世界！"])

    # ========== CJK ratio tests ==========

    def test_cjk_ratio(self):
        """Ratio of CJK characters over all letters; 0 without letters."""
        ratio = ReadingLevelScorer._cjk_ratio
        self.assertEqual(ratio("hello"), 0.0)
        self.assertEqual(ratio("你好"), 1.0)
        self.assertEqual(ratio("ab你好"), 0.5)
        self.assertEqual(ratio(""), 0.0)
        self.assertAlmostEqual(ratio(MIXED_LOW), 2 / 23)
        self.assertAlmostEqual(ratio(MIXED_HIGH), 7 / 13)

    # ========== Formula arithmetic tests ==========

    def test_formula_arithmetic_against_hand_calculation(self):
        """The stamped SIMPLE scores match hand arithmetic exactly:
        W=12, S=2, Y=12, complex=0 -> W/S=6, Y/W=1 ->
        Flesch = 206.835 - 1.015*6 - 84.6*1 = 116.145,
        FK grade = 0.39*6 + 11.8*1 - 15.59 = -1.45,
        Fog = 0.4*(6 + 100*0/12) = 2.4."""
        level = self.scorer._analyze(SIMPLE)
        self.assertEqual(level["word_count"], 12)
        self.assertEqual(level["sentence_count"], 2)
        self.assertEqual(level["syllable_count"], 12)

        words_per_sentence = 12 / 2
        syllables_per_word = 12 / 12
        expected_ease = (206.835 - 1.015 * words_per_sentence
                         - 84.6 * syllables_per_word)
        expected_grade = (0.39 * words_per_sentence
                          + 11.8 * syllables_per_word - 15.59)
        expected_fog = 0.4 * (words_per_sentence + 100 * 0 / 12)
        self.assertAlmostEqual(level["flesch_reading_ease"],
                               round(expected_ease, 2), places=6)
        self.assertAlmostEqual(level["flesch_kincaid_grade"],
                               round(expected_grade, 2), places=6)
        self.assertAlmostEqual(level["gunning_fog"],
                               round(expected_fog, 2), places=6)

    def test_polysyllabic_paragraph_hand_computed(self):
        """Hand-counted probe: W=6, S=1, Y=22, complex=4 ->
        Flesch = -109.455, FK = 30.0167, Fog = 29.0667 (rounded)."""
        level = self.scorer._analyze(POLY)
        self.assertEqual(level["word_count"], 6)
        self.assertEqual(level["sentence_count"], 1)
        self.assertEqual(level["syllable_count"], 22)
        self.assertAlmostEqual(level["flesch_reading_ease"], -109.455,
                               places=2)
        self.assertAlmostEqual(level["flesch_kincaid_grade"], 30.0167,
                               places=2)
        self.assertAlmostEqual(level["gunning_fog"], 29.0667, places=2)
        self.assertEqual(level["flesch_reading_ease"], -109.45)
        self.assertEqual(level["flesch_kincaid_grade"], 30.02)
        self.assertEqual(level["gunning_fog"], 29.07)

    def test_simple_text_easier_than_academic_text(self):
        """Monosyllabic prose scores higher ease / lower grade and fog than
        academic-register prose."""
        simple = self.scorer._analyze(SIMPLE)
        academic = self.scorer._analyze(ACADEMIC)
        self.assertGreater(simple["flesch_reading_ease"],
                           academic["flesch_reading_ease"])
        self.assertLess(simple["flesch_kincaid_grade"],
                        academic["flesch_kincaid_grade"])
        self.assertLess(simple["gunning_fog"], academic["gunning_fog"])
        # Sanity pins for the academic direction.
        self.assertLess(academic["flesch_reading_ease"], 0.0)
        self.assertGreater(academic["flesch_kincaid_grade"], 20.0)
        self.assertEqual(academic["word_count"], 30)
        self.assertEqual(academic["syllable_count"], 114)

    # ========== Gunning-Fog complex-word rules ==========

    def test_proper_noun_capitalization_excluded_from_fog(self):
        """A capitalized non-initial token is not complex, so the
        capitalized variant yields a lower fog than the lowercase one
        (complex words 1 vs 2 -> fog 9.07 vs 15.73)."""
        caps = self.scorer._analyze(PROP_CAPS)
        lower = self.scorer._analyze(PROP_LOWER)
        self.assertEqual(caps["word_count"], lower["word_count"])
        self.assertEqual(caps["syllable_count"],
                         lower["syllable_count"])  # syllables unaffected
        self.assertEqual(caps["gunning_fog"], 9.07)
        self.assertEqual(lower["gunning_fog"], 15.73)

        # Sentence-initial capitals are NOT excluded as proper-noun-ish.
        self.assertTrue(self.scorer._is_complex("Philadelphia", True))
        self.assertFalse(self.scorer._is_complex("Philadelphia", False))
        self.assertTrue(self.scorer._is_complex("philadelphia", False))

    def test_hyphenated_compound_simplification(self):
        """A hyphenated token counts as complex only when one part alone
        reaches 3 syllables (fog 1.6 vs 11.6)."""
        simple = self.scorer._analyze(HYPHEN_SIMPLE)
        compound = self.scorer._analyze(HYPHEN_COMPLEX)
        self.assertEqual(simple["gunning_fog"], 1.6)
        self.assertEqual(compound["gunning_fog"], 11.6)
        self.assertFalse(self.scorer._is_complex("state-of-the-art", False))
        self.assertTrue(
            self.scorer._is_complex("computer-communication-application",
                                    False))

    # ========== Non-Latin (CJK) path tests ==========

    def test_cjk_text_gets_note_and_stats_without_formulas(self):
        """Pure CJK text: formulas are None, stats are recorded and the
        readability note is stamped; hand counts W=16 (9+7 chars), S=2."""
        level = self.scorer._analyze(CJK)
        self.assertIsNone(level["flesch_reading_ease"])
        self.assertIsNone(level["flesch_kincaid_grade"])
        self.assertIsNone(level["gunning_fog"])
        self.assertEqual(level["word_count"], 16)
        self.assertEqual(level["sentence_count"], 2)
        self.assertEqual(level["syllable_count"], 0)

        docs = self.scorer.process_docs([_doc(CJK)], self.query)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].metadata["readability_note"],
                         "syllable formulas apply to English text only")
        self.assertIsNone(docs[0].metadata["reading_level"]
                          ["flesch_reading_ease"])

    def test_cjk_ratio_threshold_boundary(self):
        """Latin-heavy text (ratio 0.087) takes the formula path; CJK-heavy
        text (ratio 0.538) takes the note path — both record word stats."""
        low = self.scorer._analyze(MIXED_LOW)
        self.assertIsNotNone(low["flesch_reading_ease"])
        self.assertEqual(low["word_count"], 6)  # 研究 = two char-words
        self.assertEqual(low["syllable_count"], 6)

        high = self.scorer._analyze(MIXED_HIGH)
        self.assertIsNone(high["flesch_reading_ease"])
        self.assertEqual(high["word_count"], 9)  # See + 7 chars + now
        self.assertEqual(high["sentence_count"], 1)
        docs = self.scorer.process_docs([_doc(MIXED_HIGH)], self.query)
        self.assertIn("readability_note", docs[0].metadata)

    # ========== Empty / degenerate input tests ==========

    def test_empty_and_blank_text(self):
        """Empty, whitespace-only and None text yield zero counts with
        None formulas and no note; the documents survive processing."""
        for text in ("", "   ", None):
            level = self.scorer._analyze(text)
            self.assertEqual(level["word_count"], 0)
            self.assertEqual(level["sentence_count"], 0)
            self.assertEqual(level["syllable_count"], 0)
            self.assertIsNone(level["flesch_reading_ease"])
            self.assertIsNone(level["flesch_kincaid_grade"])
            self.assertIsNone(level["gunning_fog"])

        docs = [_doc(""), _doc("   ")]
        # A None text cannot pass the Document constructor's id validator,
        # but the processor still tolerates it if one exists downstream.
        none_doc = Document(text="")
        none_doc.text = None
        docs.append(none_doc)
        result = self.scorer.process_docs(docs, self.query)
        self.assertEqual(len(result), 3)
        for doc in result:
            self.assertEqual(doc.metadata["reading_level"]["word_count"], 0)
            self.assertNotIn("readability_note", doc.metadata)

    def test_empty_input_list_and_punctuation_only(self):
        """An empty batch returns empty; punctuation-only text has
        sentences but no words, so formulas stay None."""
        self.assertEqual(self.scorer.process_docs([], self.query), [])
        level = self.scorer._analyze("!!! ???")
        self.assertEqual(level["sentence_count"], 2)
        self.assertEqual(level["word_count"], 0)
        self.assertIsNone(level["flesch_kincaid_grade"])

    # ========== Metadata stamping tests ==========

    def test_metadata_shape_and_values(self):
        """The stamped dictionary holds exactly the six public fields with
        the pinned SIMPLE values."""
        docs = self.scorer.process_docs([_doc(SIMPLE)], self.query)
        level = docs[0].metadata["reading_level"]
        self.assertEqual(set(level), {
            "flesch_reading_ease", "flesch_kincaid_grade", "gunning_fog",
            "word_count", "sentence_count", "syllable_count"})
        self.assertEqual(level, {
            "flesch_reading_ease": 116.15,
            "flesch_kincaid_grade": -1.45,
            "gunning_fog": 2.4,
            "word_count": 12,
            "sentence_count": 2,
            "syllable_count": 12})

    def test_existing_metadata_preserved_and_not_mutated(self):
        """Pre-existing metadata survives; stamping writes through a copy;
        text and id are untouched."""
        doc = _doc(SIMPLE, source="wiki", rank=3)
        meta_ref = doc.metadata
        result = self.scorer.process_docs([doc], self.query)
        self.assertIs(result[0], doc)
        self.assertEqual(doc.text, SIMPLE)
        self.assertEqual(doc.id, result[0].id)
        self.assertEqual(doc.metadata["source"], "wiki")
        self.assertEqual(doc.metadata["rank"], 3)
        self.assertIn("reading_level", doc.metadata)
        self.assertNotIn("reading_level", meta_ref)
        self.assertIsNot(doc.metadata, meta_ref)

    def test_disabled_keys_stamp_nothing(self):
        """Empty reading_level_key / note_key disable both stamps."""
        self.scorer.reading_level_key = ""
        self.scorer.note_key = ""
        latin = _doc(SIMPLE, keep="yes")
        cjk = _doc(CJK, keep="too")
        result = self.scorer.process_docs([latin, cjk], self.query)
        self.assertEqual(len(result), 2)
        self.assertEqual(latin.metadata, {"keep": "yes"})
        self.assertEqual(cjk.metadata, {"keep": "too"})

    def test_custom_metadata_keys(self):
        """Both metadata keys are configurable."""
        self.scorer.reading_level_key = "difficulty"
        self.scorer.note_key = "why_no_score"
        result = self.scorer.process_docs([_doc(CJK)], self.query)
        self.assertIn("difficulty", result[0].metadata)
        self.assertIn("why_no_score", result[0].metadata)

    # ========== Filter mode tests ==========

    def test_default_stamp_only_keeps_everything(self):
        """Without grade bounds every document survives, in order."""
        docs = [_doc(SIMPLE), _doc(ACADEMIC), _doc(CJK), _doc("")]
        result = self.scorer.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result],
                         [SIMPLE, ACADEMIC, CJK, ""])

    def test_min_grade_filter(self):
        """min_grade=0 drops the simple text (grade -1.45) and keeps the
        academic text (grade 35.1); the dropped document is still
        stamped."""
        self.scorer.min_grade = 0
        simple, academic = _doc(SIMPLE), _doc(ACADEMIC)
        result = self.scorer.process_docs([simple, academic], self.query)
        self.assertEqual([d.text for d in result], [ACADEMIC])
        self.assertIn("reading_level", simple.metadata)
        self.assertEqual(simple.metadata["reading_level"]
                         ["flesch_kincaid_grade"], -1.45)

    def test_max_grade_filter(self):
        """max_grade=10 keeps the simple text and drops the academic
        text."""
        self.scorer.max_grade = 10
        simple, academic = _doc(SIMPLE), _doc(ACADEMIC)
        result = self.scorer.process_docs([simple, academic], self.query)
        self.assertEqual([d.text for d in result], [SIMPLE])

    def test_grade_band_and_ungradable_documents_kept(self):
        """In a [0, 12] band both Latin texts fall outside while documents
        without a computable grade (CJK, blank) are always kept."""
        self.scorer.min_grade = 0
        self.scorer.max_grade = 12
        docs = [_doc(CJK), _doc(SIMPLE), _doc(""), _doc(ACADEMIC)]
        result = self.scorer.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result], [CJK, ""])

    def test_filter_bounds_are_inclusive(self):
        """Bounds equal to a document's exact grade keep it."""
        self.scorer.min_grade = -1.45
        self.assertEqual(
            len(self.scorer.process_docs([_doc(SIMPLE)], self.query)), 1)
        self.scorer.min_grade = None
        self.scorer.max_grade = -1.45
        self.assertEqual(
            len(self.scorer.process_docs([_doc(SIMPLE)], self.query)), 1)

    # ========== Determinism tests ==========

    def test_deterministic_across_instances_and_runs(self):
        """Two instances and repeated runs produce identical metadata
        (pure stdlib, no randomness, no salted hashing)."""
        other = ReadingLevelScorer()
        for text in (SIMPLE, ACADEMIC, POLY, CJK, MIXED_LOW, ""):
            first = self.scorer._analyze(text)
            first.pop("_non_latin")
            second = other._analyze(text)
            second.pop("_non_latin")
            self.assertEqual(first, second, text[:30])
            again = self.scorer._analyze(text)
            again.pop("_non_latin")
            self.assertEqual(first, again, text[:30])

        doc_a, doc_b = _doc(ABBREV), _doc(ABBREV)
        self.scorer.process_docs([doc_a], self.query)
        self.scorer.process_docs([doc_b], None)
        self.assertEqual(doc_a.metadata["reading_level"],
                         doc_b.metadata["reading_level"])
        self.assertEqual(doc_a.metadata["reading_level"], {
            "flesch_reading_ease": 96.11,
            "flesch_kincaid_grade": 1.47,
            "gunning_fog": 2.6,
            "word_count": 13,
            "sentence_count": 2,
            "syllable_count": 16})

    def test_query_does_not_affect_results(self):
        """The optional query never influences document-side metrics."""
        with_query = ReadingLevelScorer().process_docs(
            [_doc(POLY)], self.query)[0].metadata["reading_level"]
        without = ReadingLevelScorer().process_docs([_doc(POLY)], None)[0] \
            .metadata["reading_level"]
        self.assertEqual(with_query, without)


if __name__ == '__main__':
    unittest.main()
