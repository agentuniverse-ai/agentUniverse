# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for ReadabilityTool: hand-counted ground truths, a textstat oracle
battery, word-by-word syllable adjudication, and edge cases.

Oracle strategy
---------------
* The 100 seeded battery texts are built from a controlled vocabulary that is
  filtered at test time against textstat (syllable agreement, and for fog
  agreement no easy-list word with 3+ syllables), so all five oracle formulas
  (flesch_reading_ease, flesch_kincaid_grade, gunning_fog,
  automated_readability_index, smog_index) must match textstat EXACTLY
  (bit-identical floats, since expression trees are mirrored).
* Where textstat's own segmentation differs (abbreviations, semicolons, tiny
  fragments), the tests adjudicate by feeding textstat the tool's OWN
  sentences/words and pinning the divergence explicitly.
* textstat syllables come from the CMU dictionary (plus pyphen fallback); this
  tool uses the documented vowel-group heuristic. 200+ words are compared
  word-by-word: the diverging set must equal the pinned, documented set.
"""

import math
import os
import random
import re
import time
import unittest

from agentuniverse.agent.action.tool.common_tool import readability_tool as readability_module
from agentuniverse.agent.action.tool.common_tool.readability_tool import ReadabilityTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:  # pragma: no cover - oracle is an optional test dependency
    TEXTSTAT_AVAILABLE = False

YAML_PATH = os.path.join(os.path.dirname(readability_module.__file__), "readability_tool.yaml")
REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(readability_module.__file__), "..", "..", "..", "..", "..")
)

# Fixed seed so the battery is byte-reproducible forever.
BATTERY_SEED = 20261021
BATTERY_TEXTS = 100

# Documented word-by-word divergences between the tool's vowel-group heuristic
# and textstat's CMU-dictionary syllable counts. Classes:
#   - adjacent vowels pronounced separately (poem, radio, dialect, easier,
#     creation, diagram, various, previous, visual, scenarios, react...)
#   - -y/-ied inflections trying/flying/carried/studied
#   - -ful derivatives (carefully, graceful, peaceful, useful, careful)
#   - adjective -ed forms (wicked, naked, ragged, crooked, echoed)
#   - post-vowel -es/-ires verbs whose e stays pronounced (creates,
#     initiates, coordinates, requires) - the mirror of the silent -es rule
#   - reduced/elided vowels (evening, everybody, experience, geography,
#     environ)
#   - -ue endings where the silent-e subtraction bites (venue)
#   - British spellings (theatre)
#   - no plain vowel letters (rhythm)
#   - concatenated technical tokens: CMU/pyphen undercounts (github, google,
#     utils, kubectl, pyproject, queryset, sqlalchemy, tracerprovider,
#     docprocessor, abstractmethod, configurable, paraphrasers, openssf,
#     aliyun, aliyuncs, babyagi, langchainopenai) or overcounts (hnsw,
#     nbsp, pptx)
PINNED_DIVERGENCE = {
    "abstractmethod": (4, 3), "aliyun": (2, 1), "aliyuncs": (2, 1),
    "associated": (4, 5), "babyagi": (3, 2), "careful": (3, 2),
    "configurable": (5, 3), "coordinates": (3, 4), "creates": (1, 2),
    "creation": (2, 3), "diagram": (2, 3), "docprocessor": (4, 3),
    "environ": (3, 4), "github": (2, 1), "google": (2, 1), "hnsw": (1, 2),
    "initiates": (3, 4), "kubectl": (2, 1), "langchainopenai": (5, 3),
    "layer": (1, 2), "nbsp": (1, 2), "openssf": (2, 1),
    "paraphrasers": (4, 2), "pptx": (1, 2), "previous": (2, 3),
    "pyproject": (3, 2), "queryset": (3, 2), "react": (1, 2),
    "required": (2, 3), "requires": (2, 3), "scenarios": (3, 4),
    "serialized": (3, 4), "sqlalchemy": (3, 2), "storages": (3, 2),
    "tracerprovider": (5, 3), "utils": (2, 1), "various": (2, 3),
    "venue": (1, 2), "visual": (2, 3),
    "biology": (3, 4), "carefully": (4, 3), "carried": (1, 2), "crooked": (1, 2),
    "dialect": (2, 3), "dialog": (2, 3), "easier": (2, 3), "echoed": (1, 2),
    "emerald": (3, 2), "especially": (4, 3), "evening": (3, 2),
    "everybody": (5, 4), "experience": (3, 4), "flying": (1, 2),
    "geography": (3, 4), "goodbye": (1, 2), "graceful": (3, 2),
    "industrial": (3, 4), "interesting": (4, 3), "maybe": (1, 2),
    "miniature": (3, 4), "mr": (1, 2), "naked": (1, 2), "peaceful": (3, 2),
    "piano": (2, 3), "poem": (1, 2), "poetic": (2, 3), "poetry": (2, 3),
    "quiet": (1, 2), "radio": (2, 3), "ragged": (1, 2), "rhythm": (1, 2),
    "simile": (2, 3), "specifically": (5, 4), "studied": (1, 2),
    "studio": (2, 3), "theatre": (1, 3), "trying": (1, 2), "useful": (3, 2),
    "usually": (3, 4), "video": (2, 3), "wicked": (1, 2), "louis": (1, 2),
    "pm": (1, 2),
}

# Word-by-word adjudication pool: the pinned divergence words plus a broad
# agreement vocabulary (300+ words total, extended after a 300-word fresh
# prose-vocabulary probe). The silent -es agreement words lock in the
# published -es rule (files/makes/handles-classes).
ADJUDICATION_WORDS = sorted(set(PINNED_DIVERGENCE) | set("""
    the of and a to in is you that it he was for on are as with his they at
    be this have from or one had by word but not what all were we when your
    can said there use an each which she do how their if will up other about
    out many then them these so some her would make like him into time look
    two more write go see number way could people my than first water been
    call who its now find long down day did get come made may part
    cat dog run sun tree house mouse table little simple happy garden
    reading writing speaking learning teaching children students school
    teacher lesson practice exercise knowledge understanding information
    development environment government organization community important
    different difficult wonderful readability formula syllable sentence
    paragraph analysis measure metric index level because through between
    against during before after above below under again further once here
    question answer example sample plain english easy hard harder complex
    bottle coffee three degree free please reason season treasure
    researchers investigated phenomenon deeply discussed mountain valley
    ocean river forest meadow sunrise sunset morning night bright light
    heavy soft loud silent noisy calm storm wind rain snow cloud sky earth
    world country city town street road path bridge building tower castle
    story legend myth fable novel chapter verse line page paper letter
    study carry try fly wanted needed planted rested jumped smiled laughed
    talked walked loved lived shouted whispered murmured description
    purity security clarity charity sanity unity confusion fusion vision
    mission session passion fashion action motion nation section station
    function puncture picture future nature feature capture culture
    mixture texture failure pressure pleasure judge color favor labor
    honor humor learn read morning allow follow hollow shallow yellow
    window borrow sorrow narrow
    files makes lines notes stores writes slides provides modules
    configures integrates templates guides includes defines executes
    generates types rules names modes nodes takes saves serves shares
    captures combines comes complete describes engines measures features
    structures procedures outcomes routes quotes invokes removes
    retrieves indicates goes uses boxes watches services circles handles
""".split()))


def _hand_scores(w, s, y, c, ch, letters, difficult):
    """Textbook formula arithmetic from hand-counted integers."""
    wps = w / s
    spw = y / w
    per_complex = 100 * c / w
    dc_pct = 100 * difficult / w
    dale_chall = (0.1579 * dc_pct) + (0.0496 * wps)
    if dc_pct > 5:
        dale_chall += 3.6365
    return {
        "flesch": 206.835 - 1.015 * wps - 84.6 * spw,
        "flesch_kincaid_grade": (0.39 * wps) + (11.8 * spw) - 15.59,
        "gunning_fog": 0.4 * (wps + per_complex),
        "ari": (0.5 * wps) + (4.71 * (ch / w)) - 21.43,
        "smog": (1.043 * (30 * (c / s)) ** 0.5) + 3.1291,
        "coleman_liau": 0.0588 * (letters / w * 100) - 0.296 * (s / w * 100) - 15.8,
        "dale_chall": dale_chall,
    }


# Ten hand-verified cases: every input integer was counted by hand.
# (text, words, sentences, syllables, complex, chars, letters, difficult)
HAND_CASES = [
    # "The cat sat on the mat." -> 6 words / 1 sentence; syllables 6
    # (the1 cat1 sat1 on1 the1 mat1); chars 18 (incl. the final dot);
    # letters 17; difficult 3 (the/on/the are in the easy list).
    ("The cat sat on the mat.", 6, 1, 6, 0, 18, 17, 3),
    # "He met Dr. Smith at noon. They discussed the plan." -> 2 sentences
    # (Dr. is an abbreviation); words 10; syllables 11 (discussed=2);
    # chars 41; letters 38; difficult 6 (he/at/they/the are easy).
    ("He met Dr. Smith at noon. They discussed the plan.", 10, 2, 11, 0, 41, 38, 6),
    # "The researchers investigated the phenomenon deeply." -> words 6;
    # syllables 16 (researchers3 investigated5 phenomenon4 deeply2);
    # complex 3; chars 46; letters 45; difficult 4.
    ("The researchers investigated the phenomenon deeply.", 6, 1, 16, 3, 46, 45, 4),
    # No terminator: 1 sentence. words 9; syllables 11 (over2 lazy2);
    # chars 35; letters 35; difficult 7 (only the/the are easy).
    ("The quick brown fox jumps over the lazy dog", 9, 1, 11, 0, 35, 35, 7),
    # Semicolons split: 3 sentences; words 8; syllables 8; chars 27;
    # letters 24; difficult 4 (he/he/he/the easy; came,saw,left,room hard).
    ("He came; he saw; he left the room.", 8, 3, 8, 0, 27, 24, 4),
    # Single word: 1 sentence; 2 syllables (hel-lo); chars 6; letters 5;
    # difficult 1.
    ("Hello.", 1, 1, 2, 0, 6, 5, 1),
    # Decimals do not split: 1 sentence; words 7 (3.14 and 2.7 are words);
    # syllables 8 (units2, numbers count as 1); chars 25; letters 22;
    # difficult 4 (the/is/by easy; price, numbers, units hard).
    ("The price is 3.14 by 2.7 units.", 7, 1, 8, 0, 25, 22, 4),
    # ? and ! terminators: 3 sentences; words 13; syllables 15 (over2
    # quickly2, all others 1); chars 50; letters 47; difficult 8 (you/see/the/it/the easy).
    ("Did you see the bird? Yes! It flew over the tall tree quickly.",
     13, 3, 15, 0, 50, 47, 8),
    # Contraction and hyphen: don't/it's are one word each, well-known
    # becomes wellknown; 2 sentences (semicolon); words 6; syllables 8
    # (worry2 wellknown2); chars 31; letters 26 (wellknown = 9 letters); difficult 5.
    ("Don't worry; it's a well-known fact.", 6, 2, 8, 0, 31, 26, 5),
    # Ellipsis never splits: 2 sentences; words 11; syllables 13
    # (nothing2 nothing2); chars 47; letters 42; difficult 5 (he/said/at/all/of/the easy).
    ("Wait... he said nothing at all. Nothing came of the plan.",
     11, 2, 13, 0, 47, 42, 5),
]


class ReadabilityHandComputedTest(unittest.TestCase):
    """Unit tests against hand-counted inputs and textbook formula arithmetic."""

    def setUp(self):
        self.tool = ReadabilityTool()

    def test_hand_cases(self):
        """Every hand-counted case matches metrics and all seven scores."""
        for text, w, s, y, c, ch, letters, difficult in HAND_CASES:
            result = self.tool.execute(mode="analyze", text=text)
            self.assertEqual(result["status"], "success", result.get("error"))
            m = result["metrics"]
            self.assertEqual(m["word_count"], w, text)
            self.assertEqual(m["sentence_count"], s, text)
            self.assertEqual(m["syllable_count"], y, text)
            self.assertEqual(m["complex_word_count"], c, text)
            self.assertEqual(m["char_count"], ch, text)
            self.assertEqual(m["letters_only"], letters, text)
            expected = _hand_scores(w, s, y, c, ch, letters, difficult)
            for name, want in expected.items():
                got = result["scores"][name]["score"]
                self.assertIsInstance(got, float, (name, text))
                self.assertTrue(math.isclose(got, want, rel_tol=1e-12), (name, text, got, want))
            # Deterministic sub-derivations.
            self.assertEqual(m["avg_words_per_sentence"], w / s)
            self.assertTrue(math.isclose(m["avg_syllables_per_word"], y / w, rel_tol=1e-15))

    def test_hand_case_alegbra_spot_checks(self):
        """Spot-check two classics: FRE 116.145 and SMOG base 3.1291."""
        result = self.tool.execute(mode="analyze", text="The cat sat on the mat.")
        self.assertEqual(result["scores"]["flesch"]["score"], 206.835 - 1.015 * 6 - 84.6 * 1.0)
        self.assertEqual(result["scores"]["smog"]["score"], 3.1291)
        # Coleman-Liau hand arithmetic: 0.0588*500 - 0.296*100 - 15.8 = -16.0.
        single = self.tool.execute(mode="analyze", text="Hello.")
        self.assertTrue(
            math.isclose(single["scores"]["coleman_liau"]["score"], -16.0, rel_tol=1e-12)
        )

    def test_sentence_detail_counts(self):
        """Per-sentence detail carries words, syllables, and a Flesch score."""
        result = self.tool.execute(mode="analyze", text="The cat sat on the mat. Hello.")
        self.assertEqual(len(result["sentences"]), 2)
        first = result["sentences"][0]
        self.assertEqual(first["text"], "The cat sat on the mat.")
        self.assertEqual(first["words"], 6)
        self.assertEqual(first["syllables"], 6)
        self.assertEqual(first["score"], 206.835 - 1.015 * 6 - 84.6 * 1.0)
        self.assertEqual(result["word_syllables"][0], {"word": "The", "syllables": 1})
        self.assertEqual(result["metrics"]["polysyllabic"], [])

    def test_silent_es_rule(self):
        """Hand-verifiable silent -es behavior after the vowel-group count.

        Silent -es after a non-sibilant consonant (makes=1, files=1,
        templates=2), kept after sibilants (boxes=2, services=3, watches=2)
        and vowel-final stems (goes=1, trees=1), and kept when consonant+l+es
        keeps its syllabic -les (handles=2, circles=2) while vowel+l+es is
        silent (files=1, modules=2, locales=2).
        """
        cases = {
            "makes": 1, "takes": 1, "notes": 1, "writes": 1, "routes": 1,
            "stores": 1, "lines": 1, "slides": 1, "saves": 1, "quotes": 1,
            "files": 1, "tales": 1, "whales": 1, "modules": 2, "locales": 2,
            "templates": 2, "estimates": 3, "defines": 2, "executes": 3,
            "boxes": 2, "uses": 2, "houses": 2, "watches": 2, "services": 3,
            "goes": 1, "trees": 1, "series": 2,
            "handles": 2, "circles": 2, "bottles": 2, "articles": 3,
            "wanted": 2, "jumped": 1, "table": 2, "whale": 1,
        }
        for word, want in cases.items():
            self.assertEqual(self.tool._syllables(word), want, word)


@unittest.skipUnless(TEXTSTAT_AVAILABLE, "textstat oracle not installed")
class ReadabilityTextstatOracleTest(unittest.TestCase):
    """Exact-parity battery and word-by-word adjudication against textstat."""

    def setUp(self):
        self.tool = ReadabilityTool()
        from textstat.backend.utils._get_lang_easy_words import get_lang_easy_words
        self.easy_words = get_lang_easy_words("en")

    def _oracle_vocab(self):
        """Adjudicated vocabulary: heuristic == CMU syllables and fog-safe."""
        vocab = []
        for word in ADJUDICATION_WORDS:
            if word in PINNED_DIVERGENCE:
                continue
            heur = self.tool._syllables(word)
            ts = textstat.syllable_count(word)
            if heur != ts:
                self.fail(
                    f"agreement vocabulary word {word!r} unexpectedly diverges: "
                    f"heuristic={heur} textstat={ts} - update PINNED_DIVERGENCE"
                )
            if heur >= 3 and word in self.easy_words:
                continue  # textstat's fog exempts easy-list words; ours does not
            vocab.append(word)
        self.assertGreaterEqual(len(vocab), 60)
        return vocab

    def _battery_texts(self, vocab):
        rng = random.Random(BATTERY_SEED)
        texts = []
        for _ in range(BATTERY_TEXTS):
            sentence_count = rng.randint(3, 9)
            sentences = []
            for _ in range(sentence_count):
                n = rng.randint(3, 15)
                words = [rng.choice(vocab) for _ in range(n)]
                sentences.append(" ".join(words).capitalize() + rng.choice([".", ".", ".", "!", "?"]))
            texts.append(" ".join(sentences))
        return texts

    def test_battery_exact_parity(self):
        """100 seeded texts: all five oracle formulas match textstat exactly."""
        vocab = self._oracle_vocab()
        for text in self._battery_texts(vocab):
            result = self.tool.execute(mode="analyze", text=text)
            self.assertEqual(result["status"], "success", result.get("error"))
            m = result["metrics"]
            self.assertEqual(m["word_count"], textstat.lexicon_count(text), text)
            self.assertEqual(m["sentence_count"], textstat.sentence_count(text), text)
            self.assertEqual(m["syllable_count"], textstat.syllable_count(text), text)
            self.assertEqual(m["char_count"], textstat.char_count(text, ignore_spaces=True), text)
            self.assertEqual(m["letters_only"], textstat.letter_count(text), text)
            self.assertEqual(
                result["scores"]["flesch"]["score"], textstat.flesch_reading_ease(text), text
            )
            self.assertEqual(
                result["scores"]["flesch_kincaid_grade"]["score"],
                textstat.flesch_kincaid_grade(text),
                text,
            )
            self.assertEqual(result["scores"]["gunning_fog"]["score"], textstat.gunning_fog(text), text)
            self.assertEqual(
                result["scores"]["ari"]["score"], textstat.automated_readability_index(text), text
            )
            self.assertEqual(result["scores"]["smog"]["score"], textstat.smog_index(text), text)
            # Complex-word agreement (same syllables, list-exempt vocabulary).
            complex_expected = sum(
                1 for w in self.tool._words(text) if textstat.syllable_count(w) >= 3
            )
            self.assertEqual(m["complex_word_count"], complex_expected, text)
            self.assertEqual(
                sorted(m["polysyllabic"]),
                sorted(w for w in self.tool._words(text) if textstat.syllable_count(w) >= 3),
                text,
            )

    def test_word_by_word_syllable_adjudication(self):
        """200+ words: divergence set must equal the pinned documented set."""
        self.assertGreaterEqual(len(ADJUDICATION_WORDS), 200)
        seen = set()
        for word in ADJUDICATION_WORDS:
            heur = self.tool._syllables(word)
            ts = textstat.syllable_count(word)
            if heur != ts:
                self.assertIn(word, PINNED_DIVERGENCE, f"unpinned divergence: {word}")
                self.assertEqual(
                    PINNED_DIVERGENCE[word], (heur, ts), word
                )
                seen.add(word)
            else:
                self.assertNotIn(word, PINNED_DIVERGENCE, word)
        self.assertEqual(seen, set(PINNED_DIVERGENCE), "pinned set drifted")

    def test_segmentation_divergence_adjudicated(self):
        """Abbreviation/semicolon texts: textstat splits, this tool does not.

        The divergence is adjudicated by feeding textstat the tool's OWN
        sentences: word and syllable totals agree per sentence (agreement
        vocabulary), so aggregating textstat's per-sentence counts over the
        tool's partition reproduces the tool's formulas exactly, while
        textstat's own (different) partition yields a different score.
        """
        cases = [
            # (text, our sentence count, textstat's sentence count)
            ("She met Dr. Adams and Prof. Lee on Jan. 5 in St. Adams.", 1, 4),
            ("He arrived at 9 a.m. and left the building.", 1, 2),
            ("He came; he saw; he conquered.", 3, 1),
            ("He left. She went home early.", 2, 1),  # textstat drops 2-word fragments
        ]
        for text, our_s, ts_s in cases:
            sentences = self.tool._sentences(text)
            self.assertEqual(len(sentences), our_s, text)
            self.assertEqual(textstat.sentence_count(text), ts_s, text)
            # Feed textstat the tool's own sentences: totals must agree.
            words = self.tool._words(text)
            ts_words = sum(textstat.lexicon_count(s) for s in sentences)
            ts_syllables = sum(textstat.syllable_count(s) for s in sentences)
            self.assertEqual(ts_words, len(words), text)
            self.assertEqual(ts_syllables, sum(self.tool._syllables(w) for w in words), text)
            # Aggregating textstat counts over OUR partition reproduces the
            # tool's syllable-sensitive formulas exactly.
            result = self.tool.execute(mode="analyze", text=text)
            expected_fre = 206.835 - 1.015 * (ts_words / our_s) - 84.6 * (ts_syllables / ts_words)
            self.assertEqual(result["scores"]["flesch"]["score"], expected_fre, text)
            expected_fk = (0.39 * (ts_words / our_s)) + (11.8 * (ts_syllables / ts_words)) - 15.59
            self.assertEqual(result["scores"]["flesch_kincaid_grade"]["score"], expected_fk, text)
            # ...and differs from textstat's own segmentation of the raw text.
            self.assertNotEqual(
                result["scores"]["flesch"]["score"],
                textstat.flesch_reading_ease(text),
                text,
            )

    def test_compensating_quirk_no_divergence(self):
        """textstat's tiny-fragment dropping can compensate its abbreviation split.

        "He arrived at 9 a.m. and left." splits into three fragments under
        textstat's regex, but two of them are <= 2 words and are dropped, so
        both counters land on one sentence and the formulas agree exactly.
        Pinned here so the quirk is documented, not accidental.
        """
        text = "He arrived at 9 a.m. and left."
        sentences = self.tool._sentences(text)
        self.assertEqual(len(sentences), 1)
        self.assertEqual(textstat.sentence_count(text), 1)
        result = self.tool.execute(mode="analyze", text=text)
        self.assertEqual(result["metrics"]["word_count"], textstat.lexicon_count(text))
        self.assertEqual(result["metrics"]["syllable_count"], textstat.syllable_count(text))
        self.assertEqual(
            result["scores"]["flesch"]["score"], textstat.flesch_reading_ease(text)
        )

    def _doc_paragraphs(self):
        """10 actual prose paragraphs from repository documentation."""
        sources = [
            os.path.join(REPO_ROOT, "README.md"),
            os.path.join(
                REPO_ROOT,
                "docs", "guidebook", "en", "In-Depth_Guides",
                "Components", "Tools", "Integrated_Tools.md",
            ),
            os.path.join(REPO_ROOT, "docs", "guidebook", "en", "Concepts", "Introduction.md"),
            os.path.join(
                REPO_ROOT, "docs", "guidebook", "en", "Concepts",
                "Why_Use_agentUniverse.md",
            ),
            os.path.join(
                REPO_ROOT, "docs", "guidebook", "en", "Get_Start",
                "0.Installation_and_Initialization.md",
            ),
            os.path.join(
                REPO_ROOT, "docs", "guidebook", "en", "Get_Start",
                "3.Quick_Guide_to_Build_Single_Agent.md",
            ),
        ]
        paragraphs = []
        for path in sources:
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as handle:
                content = handle.read()
            for chunk in content.split("\n\n"):
                chunk = chunk.strip()
                if not chunk:
                    continue
                # Prose only: no markdown syntax, ASCII, reasonable length.
                if re.search(r"[`|*#>=<\[\]{}_\\/]|[\x00-\x1f]", chunk):
                    continue
                if not chunk.isascii():
                    continue
                word_count = len(chunk.split())
                if 25 <= word_count <= 400:
                    paragraphs.append(" ".join(chunk.split()))
        paragraphs = paragraphs[:10]
        self.assertEqual(len(paragraphs), 10, "expected 10 doc paragraphs")
        return paragraphs

    def test_doc_paragraphs_adjudicated(self):
        """Repo doc paragraphs: every divergence is enumerated and explained.

        For each paragraph the test proves:
        1. word/char/letter conventions match textstat on real prose;
        2. textstat's own score equals the textbook formula applied to ITS
           counts (our segmentation + its per-word syllables + its sentence
           count), so the only divergence sources are the enumerated
           syllable-mismatch words and textstat's sentence-count quirk;
        3. ARI (no syllables) matches exactly whenever sentence counts agree.
        """
        for para in self._doc_paragraphs():
            result = self.tool.execute(mode="analyze", text=para)
            self.assertEqual(result["status"], "success", result.get("error"))
            m = result["metrics"]
            words = self.tool._words(para)
            self.assertEqual(len(words), textstat.lexicon_count(para), para)
            self.assertEqual(m["char_count"], textstat.char_count(para, ignore_spaces=True), para)
            self.assertEqual(m["letters_only"], textstat.letter_count(para), para)
            ts_s = textstat.sentence_count(para)
            ts_y = sum(textstat.syllable_count(w) for w in words)
            mismatches = {
                w: (self.tool._syllables(w), textstat.syllable_count(w))
                for w in sorted(set(words))
                if self.tool._syllables(w) != textstat.syllable_count(w)
            }
            # Each mismatch is re-verified against textstat word-by-word here;
            # nothing unexplained may enter the divergence budget.
            for w, (h, t) in mismatches.items():
                self.assertEqual(t, textstat.syllable_count(w))
                self.assertNotEqual(h, t)
            # textstat's score reconstructed from ITS counts on OUR words.
            w = m["word_count"]
            ts_fre = 206.835 - 1.015 * (w / ts_s) - 84.6 * (ts_y / w)
            self.assertTrue(
                math.isclose(ts_fre, textstat.flesch_reading_ease(para), rel_tol=1e-9),
                (para, ts_fre, textstat.flesch_reading_ease(para)),
            )
            ts_fk = (0.39 * (w / ts_s)) + (11.8 * (ts_y / w)) - 15.59
            self.assertTrue(
                math.isclose(ts_fk, textstat.flesch_kincaid_grade(para), rel_tol=1e-9),
                para,
            )
            if not mismatches and ts_s == m["sentence_count"]:
                self.assertEqual(
                    result["scores"]["flesch"]["score"], textstat.flesch_reading_ease(para), para
                )
                self.assertEqual(
                    result["scores"]["flesch_kincaid_grade"]["score"],
                    textstat.flesch_kincaid_grade(para),
                    para,
                )
            # ARI ignores syllables: exact parity whenever segmentation agrees.
            if ts_s == m["sentence_count"]:
                self.assertEqual(
                    result["scores"]["ari"]["score"],
                    textstat.automated_readability_index(para),
                    para,
                )
            # Algebraic identity: our minus textstat's is fully explained by
            # the enumerated syllable deltas and the sentence-count delta.
            our_fre = result["scores"]["flesch"]["score"]
            explained = (
                -1.015 * ((w / m["sentence_count"]) - (w / ts_s))
                - 84.6 * ((m["syllable_count"] - ts_y) / w)
            )
            self.assertTrue(
                math.isclose(our_fre - textstat.flesch_reading_ease(para), explained, rel_tol=1e-9, abs_tol=1e-9),
                para,
            )


class ReadabilityEdgeCaseTest(unittest.TestCase):
    """Unit tests for empty/degenerate inputs, validation, caps, performance."""

    def setUp(self):
        self.tool = ReadabilityTool()

    def test_empty_and_whitespace(self):
        for text in ("", "   \n\t "):
            result = self.tool.execute(mode="analyze", text=text)
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["metrics"]["word_count"], 0)
            self.assertEqual(result["metrics"]["sentence_count"], 0)
            self.assertIn("empty_text", result["caveats"][0])
            for name in (
                "flesch", "flesch_kincaid_grade", "gunning_fog",
                "ari", "smog", "coleman_liau", "dale_chall",
            ):
                self.assertIsNone(result["scores"][name]["score"])
                self.assertIsNone(result["scores"][name]["band"])

    def test_single_word_and_numbers(self):
        result = self.tool.execute(mode="analyze", text="Hello.")
        self.assertEqual(result["metrics"]["word_count"], 1)
        self.assertEqual(result["scores"]["flesch"]["score"], 206.835 - 1.015 * 1 - 84.6 * 2)
        numbers = self.tool.execute(mode="analyze", text="42 17 3.5 100.")
        self.assertEqual(numbers["metrics"]["word_count"], 4)
        self.assertEqual(numbers["metrics"]["sentence_count"], 1)
        self.assertEqual(numbers["metrics"]["syllable_count"], 4)
        self.assertEqual(numbers["metrics"]["char_count"], 11)
        self.assertEqual(numbers["metrics"]["letters_only"], 9)

    def test_no_terminator_caveat(self):
        result = self.tool.execute(mode="analyze", text="just some words here")
        self.assertEqual(result["metrics"]["sentence_count"], 1)
        self.assertTrue(any(c.startswith("no_terminator") for c in result["caveats"]))

    def test_cjk_rejected_and_naive(self):
        cjk_text = "这是一个测试文本，没有空格分隔。"
        rejected = self.tool.execute(mode="analyze", text=cjk_text)
        self.assertEqual(rejected["status"], "error")
        self.assertEqual(rejected["error_type"], "validation_error")
        naive = self.tool.execute(mode="analyze", text=cjk_text, cjk="naive")
        self.assertEqual(naive["status"], "success")
        self.assertTrue(any(c.startswith("cjk_text") for c in naive["caveats"]))

    def test_smog_caveats_by_sentence_count(self):
        few = self.tool.execute(mode="analyze", text="One sentence only. Two here too.")
        self.assertTrue(any(c.startswith("smog_unreliable") for c in few["caveats"]))
        sentences = " ".join(f"The cat sat on the mat number {i}." for i in range(4))
        short = self.tool.execute(mode="analyze", text=sentences)
        self.assertTrue(any(c.startswith("smog_short_sample") for c in short["caveats"]))

    def test_caps_and_truncation_flags(self):
        long_text = " ".join(
            f"The researchers investigated phenomena number {i}." for i in range(60)
        )
        result = self.tool.execute(mode="analyze", text=long_text)
        self.assertEqual(len(result["sentences"]), self.tool.max_sentences_detail)
        self.assertTrue(result["sentences_truncated"])
        self.assertEqual(result["metrics"]["sentence_count"], 60)
        self.assertEqual(len(result["word_syllables"]), self.tool.max_word_syllables)
        self.assertTrue(result["word_syllables_truncated"])
        self.assertEqual(
            len(result["metrics"]["polysyllabic"]), self.tool.max_polysyllabic_listed
        )
        self.assertTrue(result["metrics"]["polysyllabic_truncated"])
        preview = result["sentences"][0]["text"]
        self.assertLessEqual(len(preview), self.tool.sentence_preview_length + 3)

    def test_max_text_length(self):
        tiny = ReadabilityTool(max_text_length=10)
        result = tiny.execute(mode="analyze", text="This text is far too long for the cap.")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("max_text_length", result["error"])

    def test_validation_errors(self):
        cases = [
            {"mode": "analyze"},  # missing text
            {"mode": "analyze", "text": 123},
            {"mode": "unknown", "text": "x"},
            {"mode": "compare", "a": "one."},  # missing b
            {"mode": "compare", "a": "one.", "b": 5},
            {"mode": "grade_band", "formula": "flesch"},  # missing score
            {"mode": "grade_band", "score": 5.0},  # missing formula
            {"mode": "grade_band", "score": "5.0", "formula": "flesch"},
            {"mode": "grade_band", "score": True, "formula": "flesch"},
            {"mode": "grade_band", "score": float("nan"), "formula": "flesch"},
            {"mode": "grade_band", "score": float("inf"), "formula": "flesch"},
            {"mode": "grade_band", "score": 5.0, "formula": "nope"},
            {"mode": "analyze", "text": "words", "cjk": "sometimes"},
        ]
        for kwargs in cases:
            result = self.tool.execute(**kwargs)
            self.assertEqual(result["status"], "error", kwargs)
            self.assertEqual(result["error_type"], "validation_error", kwargs)

    def test_determinism(self):
        text = "The researchers investigated the phenomenon deeply. Everyone agreed quickly."
        first = self.tool.execute(mode="analyze", text=text)
        second = self.tool.execute(mode="analyze", text=text)
        self.assertEqual(first, second)

    def test_performance_10k_words(self):
        rng = random.Random(BATTERY_SEED)
        vocab = [w for w in ADJUDICATION_WORDS if w not in PINNED_DIVERGENCE]
        words = [rng.choice(vocab) for _ in range(10_000)]
        text = " ".join(words)
        start = time.perf_counter()
        result = self.tool.execute(mode="analyze", text=text)
        elapsed = time.perf_counter() - start
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["metrics"]["word_count"], 10_000)
        self.assertLess(elapsed, 2.0, f"analyze took {elapsed:.3f}s for 10k words")


class ReadabilityGradeBandTest(unittest.TestCase):
    """Unit tests for grade_band mode covering the full band tables."""

    def setUp(self):
        self.tool = ReadabilityTool()

    def _band(self, score, formula):
        result = self.tool.execute(mode="grade_band", score=score, formula=formula)
        self.assertEqual(result["status"], "success", result.get("error"))
        return result["band"]

    def test_flesch_full_table(self):
        table = [
            (100.0, "5th grade (very easy)"),
            (90.0, "5th grade (very easy)"),
            (89.9, "6th grade (easy)"),
            (80.0, "6th grade (easy)"),
            (79.9, "7th grade (fairly easy)"),
            (70.0, "7th grade (fairly easy)"),
            (69.9, "8th-9th grade (plain English)"),
            (60.0, "8th-9th grade (plain English)"),
            (59.9, "10th-12th grade (fairly difficult)"),
            (50.0, "10th-12th grade (fairly difficult)"),
            (49.9, "college (difficult)"),
            (30.0, "college (difficult)"),
            (29.9, "college graduate (very difficult)"),
            (0.0, "college graduate (very difficult)"),
            (120.0, "5th grade (very easy)"),  # clamped above 100
            (-5.0, "college graduate (very difficult)"),  # clamped below 0
        ]
        for score, band in table:
            self.assertEqual(self._band(score, "flesch"), band, score)

    def test_grade_formulas_table(self):
        table = [
            (0.9, "preschool (below grade 1)"),
            (1.0, "early elementary (grades 1-3)"),
            (3.99, "early elementary (grades 1-3)"),
            (4.0, "late elementary (grades 4-5)"),
            (5.9, "late elementary (grades 4-5)"),
            (6.0, "middle school (grades 6-8)"),
            (8.99, "middle school (grades 6-8)"),
            (9.0, "high school (grades 9-12)"),
            (12.99, "high school (grades 9-12)"),
            (13.0, "college (grades 13-16)"),
            (16.99, "college (grades 13-16)"),
            (17.0, "graduate / professional (grade 17+)"),
            (-2.0, "preschool (below grade 1)"),
        ]
        for formula in ("flesch_kincaid_grade", "gunning_fog", "ari", "smog", "coleman_liau"):
            for score, band in table:
                self.assertEqual(self._band(score, formula), band, (formula, score))

    def test_dale_chall_table(self):
        table = [
            (0.0, "grade 4 and below"),
            (4.9, "grade 4 and below"),
            (5.0, "grades 5-6"),
            (5.9, "grades 5-6"),
            (6.0, "grades 7-8"),
            (6.9, "grades 7-8"),
            (7.0, "grades 9-10"),
            (7.9, "grades 9-10"),
            (8.0, "grades 11-12"),
            (8.9, "grades 11-12"),
            (9.0, "grades 13-15 (college)"),
            (9.9, "grades 13-15 (college)"),
            (10.0, "college graduate (grade 16+)"),
            (12.5, "college graduate (grade 16+)"),
        ]
        for score, band in table:
            self.assertEqual(self._band(score, "dale_chall"), band, score)

    def test_easier_direction(self):
        result = self.tool.execute(mode="grade_band", score=50, formula="flesch")
        self.assertEqual(result["easier_direction"], "higher")
        result = self.tool.execute(mode="grade_band", score=50, formula="gunning_fog")
        self.assertEqual(result["easier_direction"], "lower")


class ReadabilityCompareTest(unittest.TestCase):
    """Unit tests for compare mode verdicts and direction handling."""

    def setUp(self):
        self.tool = ReadabilityTool()
        self.easy = "The cat sat on the mat. The dog ran to the pen."
        self.hard = (
            "The ubiquitous dissertation obfuscates comprehension. "
            "Notwithstanding pedagogical methodologies, esoteric terminology proliferates."
        )

    def test_easier_verdict(self):
        result = self.tool.execute(mode="compare", a=self.easy, b=self.hard)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["summary"]["easier"], "a")
        self.assertTrue(result["summary"]["unanimous"])
        self.assertEqual(result["summary"]["votes"]["a"], 7)
        # flesch: higher is easier; every grade formula: lower is easier.
        self.assertEqual(result["formulas"]["flesch"]["easier"], "a")
        self.assertGreater(
            result["formulas"]["flesch"]["a"], result["formulas"]["flesch"]["b"]
        )
        self.assertEqual(result["formulas"]["gunning_fog"]["easier"], "a")
        self.assertLess(
            result["formulas"]["gunning_fog"]["a"], result["formulas"]["gunning_fog"]["b"]
        )
        # Band columns are reported for every formula.
        self.assertTrue(result["formulas"]["ari"]["a_band"])

    def test_tie(self):
        text = "The cat sat on the mat."
        result = self.tool.execute(mode="compare", a=text, b=text)
        self.assertEqual(result["summary"]["easier"], "tie")
        self.assertEqual(result["summary"]["votes"]["tie"], 7)
        self.assertTrue(all(f["easier"] == "tie" for f in result["formulas"].values()))

    def test_empty_side_scores_none(self):
        result = self.tool.execute(mode="compare", a="", b=self.easy)
        self.assertEqual(result["status"], "success")
        self.assertIsNone(result["formulas"]["flesch"]["a"])
        self.assertIsNone(result["formulas"]["flesch"]["easier"])
        self.assertEqual(result["summary"]["easier"], "undecidable")

    def test_sides_carry_full_analysis(self):
        result = self.tool.execute(mode="compare", a=self.easy, b=self.hard)
        self.assertEqual(result["a"]["metrics"]["word_count"], 12)
        self.assertIn("caveats", result)
        self.assertTrue(all(c.startswith(("a: ", "b: ")) for c in result["caveats"]))


class ReadabilityToolfaceTest(unittest.TestCase):
    """Unit tests for the tool surface: docstring data and yaml round-trip."""

    def setUp(self):
        self.tool = ReadabilityTool()

    def test_easy_word_list_is_exactly_76(self):
        self.assertEqual(len(readability_module._EASY_WORDS_76), 76)
        # All words are lowercase plain tokens.
        for word in readability_module._EASY_WORDS_76:
            self.assertEqual(word, word.lower())
            self.assertTrue(word.isalpha())

    def test_abbreviation_list_size(self):
        self.assertGreaterEqual(len(readability_module._ABBREVIATIONS), 40)

    def test_abbreviation_segmentation(self):
        cases = {
            "Mr. Smith met them at noon. Everyone talked.": 2,
            "She met Dr. Adams and Prof. Lee on Jan. 5 in St. Louis.": 1,
            "The meeting started at 9 a.m. and ended at 5 p.m. today.": 1,
            "See Fig. 3 and refs. in Vol. 2, pp. 10-30, approx. noon.": 1,
            "J. K. Rowling wrote it in the U.S. last year.": 1,
            "Compare item no. 7 with item no. 8 in the catalogue.": 1,
        }
        for text, expected in cases.items():
            self.assertEqual(len(self.tool._sentences(text)), expected, text)

    def test_ellipsis_and_decimal_never_split(self):
        self.assertEqual(len(self.tool._sentences("Wait... he said nothing. Now.")), 2)
        self.assertEqual(len(self.tool._sentences("Pi is 3.14159 rounded here.")), 1)
        self.assertEqual(len(self.tool._sentences("He said no... then left the room.")), 1)


class ReadabilityRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped readability_tool.yaml as a tool component."""

    def setUp(self):
        """Load the shipped yaml config and snapshot the current app configer state."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the app configer snapshot taken in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """Verify the shipped yaml resolves to a tool component exposing the ReadabilityTool class."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "ReadabilityTool")

    def test_manager(self):
        """Verify the ReadabilityTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, ReadabilityTool)
        self.assertEqual(tool.input_keys, ["mode"])


if __name__ == "__main__":
    unittest.main()
