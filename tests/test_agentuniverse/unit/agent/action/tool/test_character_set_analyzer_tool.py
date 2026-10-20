#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_character_set_analyzer_tool.py

"""Offline unit tests for CharacterSetAnalyzerTool.

The tool is built purely on the standard library (``unicodedata`` and
a documented block-range table) and never touches the network, so
this suite runs fully offline. Every assertion is deterministic:

* the block-range table is checked structurally (sorted, inclusive,
  non-overlapping) and every block boundary character is cross-checked
  against its known identity via ``unicodedata.name`` plus the block
  lookup — a typo in either the code point or the block name breaks
  the test;
* the ``blocks`` / ``categories`` ground truths are hand-counted
  tallies of a multilingual sample (with combining marks, two astral
  characters and a lone surrogate), including exact sort order and
  percentage arithmetic;
* ``summary`` flags, distinct counts and top-5 frequencies are
  hand-counted as well;
* the error matrix covers the strict validation rules (unknown or
  non-lowercase mode, missing / empty / non-string text, oversized
  text).
"""

import unittest
import unicodedata

from agentuniverse.agent.action.tool.common_tool import CharacterSetAnalyzerTool
from agentuniverse.agent.action.tool.common_tool.character_set_analyzer_tool import (
    _BLOCK_RANGES,
    CharacterSetAnalyzerTool as DirectCharacterSetAnalyzerTool,
    lookup_block,
)

# --------------------------------------------------------------------- #
# Hand-counted multilingual sample
#
# "AéĀĠ Ωλ Бж שָׁלוֹם سلام नमस्ते สวัสดี あいう アイウ 漢字 한글 🌍"
#
# 12 tokens joined by 11 ASCII spaces (Basic Latin), 53 chars total.
#   Basic Latin          12  (A + 11 spaces)
#   Latin-1 Supplement    1  (é)
#   Latin Extended-A      2  (Ā, Ġ)
#   Greek and Coptic      2  (Ω, λ)
#   Cyrillic              2  (Б, ж)
#   Hebrew                7  (4 letters + qamats + shin dot + holam)
#   Arabic                4  (س ل ا م)
#   Devanagari            6  (4 letters + virama + vowel sign े)
#   Thai                  6  (5 letters incl. ส twice + 2 marks)
#   Hiragana              3  (あ い う)
#   Katakana              3  (ア イ ウ)
#   CJK Unified Ideog.    2  (漢 字)
#   Hangul Syllables      2  (한 글)
#   Other                 1  (🌍, astral)
#
# General categories: Lu 5 (A Ā Ġ Ω Б), Ll 3 (é λ ж),
# Lo 26, Mn 7 (3 Hebrew + 2 Devanagari + 2 Thai marks), Zs 11
# (spaces), So 1 (🌍).
# --------------------------------------------------------------------- #
SAMPLE = "AéĀĠ Ωλ Бж שָׁלוֹם سلام नमस्ते สวัสดี あいう アイウ 漢字 한글 🌍"
SAMPLE_TOTAL = 53

EXPECTED_BLOCKS = [
    ("Basic Latin", 12, 22.64),
    ("Hebrew", 7, 13.21),
    ("Devanagari", 6, 11.32),
    ("Thai", 6, 11.32),
    ("Arabic", 4, 7.55),
    ("Hiragana", 3, 5.66),
    ("Katakana", 3, 5.66),
    ("CJK Unified Ideographs", 2, 3.77),
    ("Cyrillic", 2, 3.77),
    ("Greek and Coptic", 2, 3.77),
    ("Hangul Syllables", 2, 3.77),
    ("Latin Extended-A", 2, 3.77),
    ("Latin-1 Supplement", 1, 1.89),
    ("Other", 1, 1.89),
]

EXPECTED_CATEGORIES = [
    ("Lo", "Other Letter", 26, 49.06),
    ("Zs", "Space Separator", 11, 20.75),
    ("Mn", "Nonspacing Mark", 7, 13.21),
    ("Lu", "Uppercase Letter", 5, 9.43),
    ("Ll", "Lowercase Letter", 3, 5.66),
    ("So", "Other Symbol", 1, 1.89),
]

EXPECTED_GROUPS = [
    ("L", "Letter", 34, 64.15),
    ("Z", "Separator", 11, 20.75),
    ("M", "Mark", 7, 13.21),
    ("S", "Symbol", 1, 1.89),
]

# Known character identities: each entry cross-checks the code
# point's official Unicode name (independent of our table) against
# the block the tool attributes it to. ``None`` marks private-use
# characters, which have no Unicode name by definition.
ANCHORS = [
    (0x0041, "Basic Latin", "LATIN CAPITAL LETTER A"),
    (0x00FF, "Latin-1 Supplement", "LATIN SMALL LETTER Y WITH DIAERESIS"),
    (0x0100, "Latin Extended-A", "LATIN CAPITAL LETTER A WITH MACRON"),
    (0x0180, "Latin Extended-B", "LATIN SMALL LETTER B WITH STROKE"),
    (0x0250, "IPA Extensions", "LATIN SMALL LETTER TURNED A"),
    (0x02C6, "Spacing Modifier Letters", "MODIFIER LETTER CIRCUMFLEX ACCENT"),
    (0x0300, "Combining Diacritical Marks", "COMBINING GRAVE ACCENT"),
    (0x03A9, "Greek and Coptic", "GREEK CAPITAL LETTER OMEGA"),
    (0x0410, "Cyrillic", "CYRILLIC CAPITAL LETTER A"),
    (0x0531, "Armenian", "ARMENIAN CAPITAL LETTER AYB"),
    (0x05D0, "Hebrew", "HEBREW LETTER ALEF"),
    (0x0627, "Arabic", "ARABIC LETTER ALEF"),
    (0x0905, "Devanagari", "DEVANAGARI LETTER A"),
    (0x0E01, "Thai", "THAI CHARACTER KO KAI"),
    (0x2013, "General Punctuation", "EN DASH"),
    (0x20AC, "Currency Symbols", "EURO SIGN"),
    (0x2122, "Letterlike Symbols", "TRADE MARK SIGN"),
    (0x2153, "Number Forms", "VULGAR FRACTION ONE THIRD"),
    (0x2192, "Arrows", "RIGHTWARDS ARROW"),
    (0x2211, "Mathematical Operators", "N-ARY SUMMATION"),
    (0x231A, "Miscellaneous Technical", "WATCH"),
    (0x2500, "Box Drawing", "BOX DRAWINGS LIGHT HORIZONTAL"),
    (0x2584, "Block Elements", "LOWER HALF BLOCK"),
    (0x25A0, "Geometric Shapes", "BLACK SQUARE"),
    (0x2600, "Miscellaneous Symbols", "BLACK SUN WITH RAYS"),
    (0x2705, "Dingbats", "WHITE HEAVY CHECK MARK"),
    (0x3001, "CJK Symbols and Punctuation", "IDEOGRAPHIC COMMA"),
    (0x3042, "Hiragana", "HIRAGANA LETTER A"),
    (0x30A2, "Katakana", "KATAKANA LETTER A"),
    (0x3400, "CJK Unified Ideographs Extension A", "CJK UNIFIED IDEOGRAPH-3400"),
    (0x4E00, "CJK Unified Ideographs", "CJK UNIFIED IDEOGRAPH-4E00"),
    (0xAC00, "Hangul Syllables", "HANGUL SYLLABLE GA"),
    (0xE000, "Private Use Area", None),
    (0xFF01, "Halfwidth and Fullwidth Forms", "FULLWIDTH EXCLAMATION MARK"),
]


class BlockTableTest(unittest.TestCase):
    """Structural and identity checks of the compact block table."""

    # Official Unicode block ranges (per the UCD Blocks.txt) for the 34
    # blocks the compact table covers. Held independently here so the
    # boundary tests below cannot silently follow a table typo: if a
    # range in _BLOCK_RANGES drifts from the official values, this
    # equality fails even though lookup_block stays self-consistent.
    OFFICIAL_RANGES = [
        (0x0000, 0x007F, "Basic Latin"),
        (0x0080, 0x00FF, "Latin-1 Supplement"),
        (0x0100, 0x017F, "Latin Extended-A"),
        (0x0180, 0x024F, "Latin Extended-B"),
        (0x0250, 0x02AF, "IPA Extensions"),
        (0x02B0, 0x02FF, "Spacing Modifier Letters"),
        (0x0300, 0x036F, "Combining Diacritical Marks"),
        (0x0370, 0x03FF, "Greek and Coptic"),
        (0x0400, 0x04FF, "Cyrillic"),
        (0x0530, 0x058F, "Armenian"),
        (0x0590, 0x05FF, "Hebrew"),
        (0x0600, 0x06FF, "Arabic"),
        (0x0900, 0x097F, "Devanagari"),
        (0x0E00, 0x0E7F, "Thai"),
        (0x2000, 0x206F, "General Punctuation"),
        (0x20A0, 0x20CF, "Currency Symbols"),
        (0x2100, 0x214F, "Letterlike Symbols"),
        (0x2150, 0x218F, "Number Forms"),
        (0x2190, 0x21FF, "Arrows"),
        (0x2200, 0x22FF, "Mathematical Operators"),
        (0x2300, 0x23FF, "Miscellaneous Technical"),
        (0x2500, 0x257F, "Box Drawing"),
        (0x2580, 0x259F, "Block Elements"),
        (0x25A0, 0x25FF, "Geometric Shapes"),
        (0x2600, 0x26FF, "Miscellaneous Symbols"),
        (0x2700, 0x27BF, "Dingbats"),
        (0x3000, 0x303F, "CJK Symbols and Punctuation"),
        (0x3040, 0x309F, "Hiragana"),
        (0x30A0, 0x30FF, "Katakana"),
        (0x3400, 0x4DBF, "CJK Unified Ideographs Extension A"),
        (0x4E00, 0x9FFF, "CJK Unified Ideographs"),
        (0xAC00, 0xD7AF, "Hangul Syllables"),
        (0xE000, 0xF8FF, "Private Use Area"),
        (0xFF00, 0xFFEF, "Halfwidth and Fullwidth Forms"),
    ]

    def test_ranges_match_official_unicode_values(self) -> None:
        self.assertEqual(
            [(first, last, name) for first, last, name in _BLOCK_RANGES],
            self.OFFICIAL_RANGES,
        )

    def test_table_is_sorted_and_non_overlapping(self) -> None:
        self.assertEqual(len(_BLOCK_RANGES), 34)
        for (prev_first, prev_last, _), (first, last, _) in zip(
            _BLOCK_RANGES, _BLOCK_RANGES[1:]
        ):
            self.assertLessEqual(prev_first, first)
            self.assertLess(prev_last, first)
            self.assertLessEqual(first, last)

    def test_first_and_last_code_point_of_every_block(self) -> None:
        for first, last, name in _BLOCK_RANGES:
            self.assertEqual(lookup_block(first), name, hex(first))
            self.assertEqual(lookup_block(last), name, hex(last))

    def test_boundaries_do_not_bleed_into_neighbour(self) -> None:
        for first, last, name in _BLOCK_RANGES:
            if first > 0:
                self.assertNotEqual(lookup_block(first - 1), name, hex(first))
            self.assertNotEqual(lookup_block(last + 1), name, hex(last))

    def test_anchor_identities_match_official_names(self) -> None:
        # One anchor per block: 34 anchors == 34 table names.
        self.assertEqual(
            {name for _cp, name, _uname in ANCHORS},
            {name for _f, _l, name in _BLOCK_RANGES},
        )
        for code_point, block, official_name in ANCHORS:
            self.assertEqual(lookup_block(code_point), block, hex(code_point))
            if official_name is None:
                # Private use characters have no Unicode name.
                with self.assertRaises(ValueError):
                    unicodedata.name(chr(code_point))
            else:
                self.assertEqual(
                    unicodedata.name(chr(code_point)),
                    official_name,
                    hex(code_point),
                )

    def test_gap_code_points_fall_into_other(self) -> None:
        # U+0500 is Cyrillic Supplement (not in the compact table).
        self.assertEqual(lookup_block(0x0500), "Other")
        # U+A000 is Yi Syllables (not in the compact table).
        self.assertEqual(lookup_block(0xA000), "Other")
        # U+D7B0 is Hangul Jamo Extended-B (outside Hangul Syllables).
        self.assertEqual(lookup_block(0xD7B0), "Other")
        # U+FFF0 is unassigned, beyond Halfwidth and Fullwidth Forms.
        self.assertEqual(lookup_block(0xFFF0), "Other")
        # Astral characters: emoji and mathematical alphanumerics.
        self.assertEqual(lookup_block(0x1F30D), "Other")
        self.assertEqual(lookup_block(0x1D400), "Other")
        # Lone surrogate (never valid in encoded text, valid in str).
        self.assertEqual(lookup_block(0xD800), "Other")


class BlocksModeTest(unittest.TestCase):
    """Ground-truth tests of the blocks census."""

    def setUp(self) -> None:
        self.tool = CharacterSetAnalyzerTool()

    def test_multilingual_sample_ground_truth(self) -> None:
        result = self.tool.execute(mode="blocks", text=SAMPLE)
        self.assertEqual(
            result,
            {
                "mode": "blocks",
                "total_chars": SAMPLE_TOTAL,
                "distinct_blocks": len(EXPECTED_BLOCKS),
                "blocks": [
                    {"block": name, "count": count, "percent": percent}
                    for name, count, percent in EXPECTED_BLOCKS
                ],
            },
        )

    def test_percent_arithmetic_and_count_sum(self) -> None:
        result = self.tool.execute(mode="blocks", text=SAMPLE)
        rows = result["blocks"]
        self.assertEqual(sum(row["count"] for row in rows), SAMPLE_TOTAL)
        for row in rows:
            self.assertEqual(
                row["percent"], round(row["count"] * 100.0 / SAMPLE_TOTAL, 2)
            )

    def test_other_bucket_for_astral_chars(self) -> None:
        result = self.tool.execute(mode="blocks", text="🌍 x \U0001D400")
        tally = {row["block"]: row["count"] for row in result["blocks"]}
        # 🌍 and 𝐀 are astral → Other; space, x, space → Basic Latin.
        self.assertEqual(tally, {"Other": 2, "Basic Latin": 3})
        self.assertEqual(result["total_chars"], 5)

    def test_symbol_and_punctuation_blocks(self) -> None:
        # One character per block, no separators: the all-count-1
        # output must come back sorted by block name.
        text = "".join(
            ["–", "€", "™", "→", "∑", "─", "■", "☀"]
        )
        result = self.tool.execute(mode="blocks", text=text)
        self.assertEqual(
            [row["block"] for row in result["blocks"]],
            [
                "Arrows",
                "Box Drawing",
                "Currency Symbols",
                "General Punctuation",
                "Geometric Shapes",
                "Letterlike Symbols",
                "Mathematical Operators",
                "Miscellaneous Symbols",
            ],
        )
        self.assertTrue(all(row["count"] == 1 for row in result["blocks"]))
        self.assertTrue(all(row["percent"] == 12.5 for row in result["blocks"]))

    def test_cjk_punctuation_fullwidth_private_use(self) -> None:
        tally = self.tool.execute(mode="blocks", text="、。々")["blocks"]
        self.assertEqual(
            [(row["block"], row["count"]) for row in tally],
            [("CJK Symbols and Punctuation", 3)],
        )
        tally = self.tool.execute(mode="blocks", text="！")["blocks"]
        self.assertEqual(
            [(row["block"], row["count"]) for row in tally],
            [("Halfwidth and Fullwidth Forms", 1)],
        )
        tally = self.tool.execute(mode="blocks", text=chr(0xE000))["blocks"]
        self.assertEqual(
            [(row["block"], row["count"]) for row in tally],
            [("Private Use Area", 1)],
        )

    def test_combining_mark_and_modifier_blocks(self) -> None:
        result = self.tool.execute(mode="blocks", text="e\u0301")
        self.assertEqual(
            [(row["block"], row["count"]) for row in result["blocks"]],
            [("Basic Latin", 1), ("Combining Diacritical Marks", 1)],
        )
        result = self.tool.execute(mode="blocks", text="ˆ")
        self.assertEqual(result["blocks"][0]["block"], "Spacing Modifier Letters")

    def test_less_common_script_blocks(self) -> None:
        cases = [
            ("ɐʃ", "IPA Extensions"),  # turned a + esh
            ("ƀ", "Latin Extended-B"),
            ("Ա", "Armenian"),
            ("⅓", "Number Forms"),
            ("⌚", "Miscellaneous Technical"),
            ("▄", "Block Elements"),
            ("✅", "Dingbats"),
            ("㐀", "CJK Unified Ideographs Extension A"),
        ]
        for text, expected_block in cases:
            result = self.tool.execute(mode="blocks", text=text)
            self.assertEqual(
                [row["block"] for row in result["blocks"]],
                [expected_block],
                text,
            )


class CategoriesModeTest(unittest.TestCase):
    """Ground-truth tests of the general-category census."""

    def setUp(self) -> None:
        self.tool = CharacterSetAnalyzerTool()

    def test_multilingual_sample_ground_truth(self) -> None:
        result = self.tool.execute(mode="categories", text=SAMPLE)
        self.assertEqual(result["mode"], "categories")
        self.assertEqual(result["total_chars"], SAMPLE_TOTAL)
        self.assertEqual(
            result["categories"],
            [
                {
                    "category": category,
                    "label": label,
                    "count": count,
                    "percent": percent,
                }
                for category, label, count, percent in EXPECTED_CATEGORIES
            ],
        )
        self.assertEqual(
            result["groups"],
            [
                {"group": group, "label": label, "count": count, "percent": percent}
                for group, label, count, percent in EXPECTED_GROUPS
            ],
        )

    def test_group_totals_add_up(self) -> None:
        result = self.tool.execute(mode="categories", text=SAMPLE)
        self.assertEqual(
            sum(row["count"] for row in result["groups"]), SAMPLE_TOTAL
        )
        self.assertEqual(
            sum(row["count"] for row in result["categories"]), SAMPLE_TOTAL
        )

    def test_punctuation_digit_and_control_categories(self) -> None:
        # ( pd ps pe po nd zs cc ) — letters: a, b, d
        text = "a-b(d), 42\t"
        tally = {
            row["category"]: row["count"]
            for row in self.tool.execute(mode="categories", text=text)["categories"]
        }
        self.assertEqual(
            tally,
            {"Ll": 3, "Pd": 1, "Ps": 1, "Pe": 1, "Po": 1, "Nd": 2, "Zs": 1, "Cc": 1},
        )

    def test_surrogate_and_private_use_categories(self) -> None:
        tally = {
            row["category"]: row["count"]
            for row in self.tool.execute(
                mode="categories", text="\ud800" + chr(0xE000)
            )["categories"]
        }
        self.assertEqual(tally, {"Cs": 1, "Co": 1})

    def test_percent_arithmetic(self) -> None:
        result = self.tool.execute(mode="categories", text=SAMPLE)
        for row in result["categories"] + result["groups"]:
            self.assertEqual(
                row["percent"], round(row["count"] * 100.0 / SAMPLE_TOTAL, 2)
            )


class SummaryModeTest(unittest.TestCase):
    """Ground-truth tests of the summary fingerprint."""

    def setUp(self) -> None:
        self.tool = CharacterSetAnalyzerTool()

    def test_multilingual_sample_summary(self) -> None:
        result = self.tool.execute(mode="summary", text=SAMPLE)
        # Distinct: 53 chars minus 10 repeat spaces minus 1 repeat ส.
        self.assertEqual(
            result,
            {
                "mode": "summary",
                "total_chars": SAMPLE_TOTAL,
                "ascii_only": False,
                "latin1_only": False,
                "distinct_chars": 42,
                "top_chars": [
                    {"char": " ", "codepoint": 0x20, "count": 11},
                    {"char": "ส", "codepoint": 0x0E2A, "count": 2},
                    # Remaining singletons ordered by code point.
                    {"char": "A", "codepoint": 0x41, "count": 1},
                    {"char": "é", "codepoint": 0xE9, "count": 1},
                    {"char": "Ā", "codepoint": 0x100, "count": 1},
                ],
                "has_emoji": True,
                "control_char_count": 0,
            },
        )

    def test_ascii_text_summary(self) -> None:
        result = self.tool.execute(mode="summary", text="Hello, World!")
        self.assertEqual(
            result,
            {
                "mode": "summary",
                "total_chars": 13,
                "ascii_only": True,
                "latin1_only": True,
                "distinct_chars": 10,
                "top_chars": [
                    {"char": "l", "codepoint": 0x6C, "count": 3},
                    {"char": "o", "codepoint": 0x6F, "count": 2},
                    {"char": " ", "codepoint": 0x20, "count": 1},
                    {"char": "!", "codepoint": 0x21, "count": 1},
                    {"char": ",", "codepoint": 0x2C, "count": 1},
                ],
                "has_emoji": False,
                "control_char_count": 0,
            },
        )

    def test_latin1_only_flag(self) -> None:
        result = self.tool.execute(mode="summary", text="café")
        self.assertFalse(result["ascii_only"])
        self.assertTrue(result["latin1_only"])
        self.assertEqual(result["distinct_chars"], 4)
        result = self.tool.execute(mode="summary", text="naïve 世界")
        self.assertFalse(result["latin1_only"])

    def test_control_char_count(self) -> None:
        result = self.tool.execute(mode="summary", text="a\tb\nc\r d")
        self.assertEqual(result["control_char_count"], 3)
        self.assertTrue(result["ascii_only"])

    def test_has_emoji_so_heuristic(self) -> None:
        # 🌍 (U+1F30D) and ⚠ (U+26A0) are both category So.
        self.assertTrue(self.tool.execute(mode="summary", text="hi 🌍")["has_emoji"])
        self.assertTrue(self.tool.execute(mode="summary", text="⚠ caution")["has_emoji"])
        # Currency symbols are Sc, not So: no emoji by this heuristic.
        self.assertFalse(self.tool.execute(mode="summary", text="€5 ₨")["has_emoji"])

    def test_top_chars_capped_at_five(self) -> None:
        result = self.tool.execute(mode="summary", text="abcdef")
        self.assertEqual(len(result["top_chars"]), 5)
        self.assertEqual(
            [(row["char"], row["count"]) for row in result["top_chars"]],
            [("a", 1), ("b", 1), ("c", 1), ("d", 1), ("e", 1)],
        )


class ValidationAndDeterminismTest(unittest.TestCase):
    """Strict validation matrix and determinism checks."""

    def setUp(self) -> None:
        self.tool = CharacterSetAnalyzerTool()

    def test_error_matrix(self) -> None:
        bad_modes = [None, "BLOCKS", "Blocks", "blockz", "", 123, ["blocks"]]
        for bad_mode in bad_modes:
            with self.assertRaises(ValueError, msg=repr(bad_mode)):
                self.tool.execute(mode=bad_mode, text="hello")
        bad_texts = [None, "", 123, True, False, ["a"], {"a": 1}, b"bytes"]
        for bad_text in bad_texts:
            with self.assertRaises(ValueError, msg=repr(bad_text)):
                self.tool.execute(mode="blocks", text=bad_text)
        # Every mode rejects bad text, not just blocks.
        for mode in ("categories", "summary"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode=mode, text=None)

    def test_error_message_lists_valid_modes(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="BLOCKS", text="hello")
        self.assertIn("blocks, categories, summary", str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="blocks", text="")
        self.assertIn("non-empty string", str(ctx.exception))

    def test_text_length_cap(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="blocks", text="a" * 100_001)
        self.assertIn("100,000", str(ctx.exception))
        # Exactly at the cap is accepted.
        result = self.tool.execute(mode="summary", text="a" * 100_000)
        self.assertEqual(result["total_chars"], 100_000)

    def test_max_text_chars_attribute_is_honored(self) -> None:
        # The documented max_text_chars bound is enforced, not a
        # hardcoded 100_000: a tighter configuration must reject text
        # that the default would accept, and accept at its own cap.
        configured = CharacterSetAnalyzerTool()
        configured.max_text_chars = 10
        with self.assertRaises(ValueError) as ctx:
            configured.execute(mode="blocks", text="a" * 11)
        self.assertIn("10-character limit", str(ctx.exception))
        result = configured.execute(mode="summary", text="a" * 10)
        self.assertEqual(result["total_chars"], 10)
        # The default tool still accepts an 11-character string.
        self.assertEqual(
            self.tool.execute(mode="summary", text="a" * 11)["total_chars"], 11
        )

    def test_deterministic_results(self) -> None:
        for mode in ("blocks", "categories", "summary"):
            first = self.tool.execute(mode=mode, text=SAMPLE)
            second = self.tool.execute(mode=mode, text=SAMPLE)
            self.assertEqual(first, second, mode)

    def test_direct_module_import_matches_package_export(self) -> None:
        self.assertIs(CharacterSetAnalyzerTool, DirectCharacterSetAnalyzerTool)
        tool = DirectCharacterSetAnalyzerTool()
        self.assertEqual(tool.name, "character_set_analyzer_tool")
        self.assertIsNotNone(tool.description)


if __name__ == "__main__":
    unittest.main()
