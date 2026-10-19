#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_text_directionality_tool.py

"""Offline unit tests for TextDirectionalityTool.

The tool is built purely on the standard library (unicodedata) and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic: ground-truth sample strings in pure
Arabic / Hebrew / Latin were hand-counted for their strong bidi-class
characters, ratios are checked with independent arithmetic, paragraph
splits are checked against hand-numbered 1-based line ranges, and the
bidi control occurrences (including a right-to-left-override filename
spoof) are checked against hand-numbered string indices.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import TextDirectionalityTool
from agentuniverse.agent.action.tool.common_tool.text_directionality_tool import (
    TextDirectionalityTool as DirectTextDirectionalityTool,
)

# --------------------------------------------------------------------- #
# Ground-truth sample strings (hand-counted)
# --------------------------------------------------------------------- #
# 5 Arabic letters (bidi class AL each).
ARABIC_HELLO = "مرحبا"
# 4 Hebrew letters (bidi class R each).
HEBREW_PEACE = "שלום"
# "hello שלום" = 5 Latin letters + 1 space + 4 Hebrew letters.
MIXED_EN_HE = "hello שלום"
MULTI_PARAGRAPH = (
    "Intro line one\n"
    "second line\n"
    "\n"
    "مرحبا بالعالم\n"
    "\n"
    "mixed שלום world\n"
    "\n"
    "123 456"
)

# Explicit bidi control characters, built from codepoints so no
# invisible literal can be silently corrupted in the source.
LRM = chr(0x200E)
RLM = chr(0x200F)
LRE = chr(0x202A)
RLE = chr(0x202B)
PDF = chr(0x202C)
LRO = chr(0x202D)
RLO = chr(0x202E)
LRI = chr(0x2066)
RLI = chr(0x2067)
FSI = chr(0x2068)
PDI = chr(0x2069)
# Extension-spoof payload: renders as "photoexe.png" in a bidi-aware
# renderer while the logical string is "photo<RLO>gnp.exe".
RLO_SPOOF = "photo" + RLO + "gnp.exe"

ALL_CONTROLS = [
    (LRM, "U+200E", "LEFT-TO-RIGHT MARK", "mark"),
    (RLM, "U+200F", "RIGHT-TO-LEFT MARK", "mark"),
    (LRE, "U+202A", "LEFT-TO-RIGHT EMBEDDING", "embedding"),
    (RLE, "U+202B", "RIGHT-TO-LEFT EMBEDDING", "embedding"),
    (PDF, "U+202C", "POP DIRECTIONAL FORMATTING", "pop"),
    (LRO, "U+202D", "LEFT-TO-RIGHT OVERRIDE", "override"),
    (RLO, "U+202E", "RIGHT-TO-LEFT OVERRIDE", "override"),
    (LRI, "U+2066", "LEFT-TO-RIGHT ISOLATE", "isolate"),
    (RLI, "U+2067", "RIGHT-TO-LEFT ISOLATE", "isolate"),
    (FSI, "U+2068", "FIRST STRONG ISOLATE", "isolate"),
    (PDI, "U+2069", "POP DIRECTIONAL ISOLATE", "pop"),
]


class TextDirectionalityToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib directionality tool."""

    def setUp(self) -> None:
        self.tool = TextDirectionalityTool()

    # ------------------------------------------------------------------ #
    # detect mode
    # ------------------------------------------------------------------ #

    def test_detect_pure_arabic(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="detect", text=ARABIC_HELLO),
            {
                "mode": "detect",
                "dominant_direction": "rtl",
                "strong_counts": {"ltr": 0, "rtl": 5},
                "total_strong": 5,
                "rtl_ratio": 1.0,
                "bidi_class_counts": {"AL": 5},
                "neutral_char_count": 0,
                "bidi_control_count": 0,
                "total_chars": 5,
            },
        )

    def test_detect_pure_hebrew(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="detect", text=HEBREW_PEACE),
            {
                "mode": "detect",
                "dominant_direction": "rtl",
                "strong_counts": {"ltr": 0, "rtl": 4},
                "total_strong": 4,
                "rtl_ratio": 1.0,
                "bidi_class_counts": {"R": 4},
                "neutral_char_count": 0,
                "bidi_control_count": 0,
                "total_chars": 4,
            },
        )

    def test_detect_pure_latin(self) -> None:
        result = self.tool.execute(mode="detect", text="Hello, world!")
        self.assertEqual(result["dominant_direction"], "ltr")
        self.assertEqual(result["strong_counts"], {"ltr": 10, "rtl": 0})
        self.assertEqual(result["total_strong"], 10)
        self.assertEqual(result["rtl_ratio"], 0.0)
        # 13 chars total: 10 letters + comma (CS) + space (WS) + "!" (ON).
        self.assertEqual(result["neutral_char_count"], 3)
        self.assertEqual(
            result["bidi_class_counts"], {"L": 10, "CS": 1, "ON": 1, "WS": 1}
        )
        self.assertEqual(result["total_chars"], 13)

    def test_detect_mixed_with_ratio_arithmetic(self) -> None:
        result = self.tool.execute(mode="detect", text=MIXED_EN_HE)
        self.assertEqual(result["dominant_direction"], "mixed")
        self.assertEqual(result["strong_counts"], {"ltr": 5, "rtl": 4})
        self.assertEqual(result["total_strong"], 9)
        # 4 / 9 rounded to four decimals.
        self.assertEqual(result["rtl_ratio"], round(4 / 9, 4))
        self.assertEqual(result["rtl_ratio"], 0.4444)
        self.assertEqual(result["neutral_char_count"], 1)  # the space
        self.assertEqual(result["bidi_class_counts"], {"L": 5, "R": 4, "WS": 1})
        self.assertEqual(result["total_chars"], 10)

    def test_detect_mixed_equal_halves_ratio_half(self) -> None:
        result = self.tool.execute(mode="detect", text="abcאבג")
        self.assertEqual(result["dominant_direction"], "mixed")
        self.assertEqual(result["strong_counts"], {"ltr": 3, "rtl": 3})
        self.assertEqual(result["rtl_ratio"], 0.5)

    def test_detect_digits_and_punctuation_only_is_neutral(self) -> None:
        result = self.tool.execute(mode="detect", text="123 !!! ,,, 456.5;")
        self.assertEqual(result["dominant_direction"], "neutral")
        self.assertEqual(result["strong_counts"], {"ltr": 0, "rtl": 0})
        self.assertIsNone(result["rtl_ratio"])
        self.assertEqual(result["total_strong"], 0)
        # Everything is weak/neutral — the documented neutral verdict.
        self.assertEqual(
            result["neutral_char_count"], result["total_chars"]
        )

    def test_detect_arabic_indic_digits_are_not_strong(self) -> None:
        # Arabic-Indic digits carry the weak class AN, not AL.
        result = self.tool.execute(mode="detect", text="٣٤٥")
        self.assertEqual(result["dominant_direction"], "neutral")
        self.assertEqual(result["strong_counts"], {"ltr": 0, "rtl": 0})
        self.assertEqual(result["bidi_class_counts"], {"AN": 3})

    def test_detect_bidi_class_counts_hand_counted(self) -> None:
        result = self.tool.execute(mode="detect", text="aא 3!")
        self.assertEqual(
            result["bidi_class_counts"], {"EN": 1, "L": 1, "ON": 1, "R": 1, "WS": 1}
        )
        self.assertEqual(result["strong_counts"], {"ltr": 1, "rtl": 1})
        self.assertEqual(result["neutral_char_count"], 3)

    def test_detect_other_ltr_scripts(self) -> None:
        for text in ("Привет", "Γειά σου", "こんにちは", "你好世界"):
            with self.subTest(text=text):
                result = self.tool.execute(mode="detect", text=text)
                self.assertEqual(result["dominant_direction"], "ltr")
                self.assertEqual(result["strong_counts"]["rtl"], 0)

    def test_detect_emoji_is_neutral(self) -> None:
        result = self.tool.execute(mode="detect", text="hi😀")
        self.assertEqual(result["dominant_direction"], "ltr")
        self.assertEqual(result["strong_counts"], {"ltr": 2, "rtl": 0})
        self.assertEqual(result["neutral_char_count"], 1)

    def test_detect_control_chars_do_not_flip_the_verdict(self) -> None:
        # RLM is bidi class R but a formatting mark, not content.
        result = self.tool.execute(mode="detect", text="hello" + RLM)
        self.assertEqual(result["dominant_direction"], "ltr")
        self.assertEqual(result["strong_counts"], {"ltr": 5, "rtl": 0})
        self.assertEqual(result["bidi_control_count"], 1)
        self.assertEqual(result["neutral_char_count"], 0)
        self.assertEqual(result["total_chars"], 6)
        # Raw class counts still show the RLM's own class for transparency.
        self.assertEqual(result["bidi_class_counts"], {"L": 5, "R": 1})
        # And an LRM cannot make pure Arabic text look mixed either.
        rtl_result = self.tool.execute(mode="detect", text=LRM + ARABIC_HELLO)
        self.assertEqual(rtl_result["dominant_direction"], "rtl")
        self.assertEqual(rtl_result["strong_counts"], {"ltr": 0, "rtl": 5})
        self.assertEqual(rtl_result["bidi_control_count"], 1)

    def test_detect_arabic_with_digits_stays_rtl(self) -> None:
        # Neutral digits never join the dominance decision.
        result = self.tool.execute(mode="detect", text="سنة 2026 م")
        self.assertEqual(result["dominant_direction"], "rtl")
        self.assertEqual(result["strong_counts"]["ltr"], 0)
        self.assertGreater(result["strong_counts"]["rtl"], 0)

    def test_detect_at_the_100k_character_boundary(self) -> None:
        result = self.tool.execute(mode="detect", text=ARABIC_HELLO * 20_000)
        self.assertEqual(result["total_chars"], 100_000)
        self.assertEqual(result["dominant_direction"], "rtl")
        self.assertEqual(result["strong_counts"]["rtl"], 100_000)

    # ------------------------------------------------------------------ #
    # per_paragraph mode
    # ------------------------------------------------------------------ #

    def test_per_paragraph_full_fixture(self) -> None:
        result = self.tool.execute(mode="per_paragraph", text=MULTI_PARAGRAPH)
        self.assertEqual(result["mode"], "per_paragraph")
        self.assertEqual(result["paragraph_count"], 4)
        self.assertEqual(
            result["paragraphs"][0],
            {
                "index": 0,
                "direction": "ltr",
                "strong_counts": {"ltr": 22, "rtl": 0},
                "rtl_ratio": 0.0,
                "bidi_control_count": 0,
                "char_count": 26,
                "start_line": 1,
                "end_line": 2,
                "preview": "Intro line one\nsecond line",
            },
        )
        self.assertEqual(result["paragraphs"][1]["direction"], "rtl")
        self.assertEqual(
            result["paragraphs"][1]["strong_counts"], {"ltr": 0, "rtl": 12}
        )
        self.assertEqual(
            (result["paragraphs"][1]["start_line"], result["paragraphs"][1]["end_line"]),
            (4, 4),
        )
        self.assertEqual(result["paragraphs"][1]["preview"], "مرحبا بالعالم")
        self.assertEqual(result["paragraphs"][2]["direction"], "mixed")
        self.assertEqual(
            result["paragraphs"][2]["strong_counts"], {"ltr": 10, "rtl": 4}
        )
        self.assertEqual(result["paragraphs"][2]["rtl_ratio"], round(4 / 14, 4))
        self.assertEqual(result["paragraphs"][3]["direction"], "neutral")
        self.assertIsNone(result["paragraphs"][3]["rtl_ratio"])
        self.assertEqual(result["paragraphs"][3]["preview"], "123 456")
        self.assertEqual(
            result["summary"], {"ltr": 1, "rtl": 1, "mixed": 1, "neutral": 1}
        )
        self.assertEqual(result["mixed_paragraphs"], [2])

    def test_per_paragraph_whitespace_blank_lines_and_runs(self) -> None:
        # Blank separator lines may contain spaces/tabs; consecutive
        # blank lines collapse into one separator.
        result = self.tool.execute(mode="per_paragraph", text="a\n  \nb\nc\n\n\n\n\td")
        self.assertEqual(result["paragraph_count"], 3)
        self.assertEqual(result["paragraphs"][0]["start_line"], 1)
        self.assertEqual(result["paragraphs"][0]["end_line"], 1)
        self.assertEqual(result["paragraphs"][1]["start_line"], 3)
        self.assertEqual(result["paragraphs"][1]["end_line"], 4)
        self.assertEqual(result["paragraphs"][2]["start_line"], 8)
        self.assertEqual(result["paragraphs"][2]["end_line"], 8)
        self.assertEqual(result["mixed_paragraphs"], [])

    def test_per_paragraph_no_blank_lines_is_one_paragraph(self) -> None:
        result = self.tool.execute(mode="per_paragraph", text="one\ntwo\nthree")
        self.assertEqual(result["paragraph_count"], 1)
        self.assertEqual(result["paragraphs"][0]["char_count"], 13)
        self.assertEqual(
            (result["paragraphs"][0]["start_line"], result["paragraphs"][0]["end_line"]),
            (1, 3),
        )

    def test_per_paragraph_leading_and_trailing_blanks(self) -> None:
        result = self.tool.execute(mode="per_paragraph", text="\n\na\n")
        self.assertEqual(result["paragraph_count"], 1)
        self.assertEqual(result["paragraphs"][0]["start_line"], 3)
        self.assertEqual(result["paragraphs"][0]["end_line"], 3)

    def test_per_paragraph_whitespace_only_text_has_no_paragraphs(self) -> None:
        result = self.tool.execute(mode="per_paragraph", text=" \n\t \n  ")
        self.assertEqual(
            result,
            {
                "mode": "per_paragraph",
                "paragraph_count": 0,
                "paragraphs": [],
                "summary": {"ltr": 0, "rtl": 0, "mixed": 0, "neutral": 0},
                "mixed_paragraphs": [],
            },
        )

    def test_per_paragraph_long_preview_is_capped_at_40_chars(self) -> None:
        long_line = "word " * 20  # 100 chars
        result = self.tool.execute(mode="per_paragraph", text=long_line)
        self.assertEqual(len(result["paragraphs"][0]["preview"]), 40)
        self.assertEqual(result["paragraphs"][0]["char_count"], 100)

    def test_per_paragraph_flags_mixed_paragraph_indices(self) -> None:
        text = "hello שלום\n\nplain latin\n\nעולם world"
        result = self.tool.execute(mode="per_paragraph", text=text)
        self.assertEqual(result["paragraph_count"], 3)
        self.assertEqual(result["mixed_paragraphs"], [0, 2])
        self.assertEqual(result["summary"]["mixed"], 2)
        self.assertEqual(result["summary"]["ltr"], 1)

    # ------------------------------------------------------------------ #
    # bidi_chars mode
    # ------------------------------------------------------------------ #

    def test_bidi_chars_rlo_spoof_case(self) -> None:
        result = self.tool.execute(mode="bidi_chars", text=RLO_SPOOF)
        self.assertEqual(result["total_found"], 1)
        self.assertTrue(result["has_override"])
        self.assertEqual(result["counts_by_codepoint"], {"U+202E": 1})
        self.assertEqual(len(result["occurrences"]), 1)
        occurrence = result["occurrences"][0]
        self.assertEqual(occurrence["index"], 5)  # after "photo"
        self.assertEqual(occurrence["codepoint"], "U+202E")
        self.assertEqual(occurrence["name"], "RIGHT-TO-LEFT OVERRIDE")
        self.assertEqual(occurrence["kind"], "override")
        self.assertFalse(result["occurrence_list_truncated"])
        # The security note explains the display-spoofing risk.
        self.assertIn("spoof", result["security_note"])
        self.assertIn("U+202E", result["security_note"])

    def test_bidi_chars_all_eleven_controls(self) -> None:
        for char, codepoint, name, kind in ALL_CONTROLS:
            with self.subTest(codepoint=codepoint):
                result = self.tool.execute(mode="bidi_chars", text=f"a{char}b")
                self.assertEqual(result["total_found"], 1)
                self.assertEqual(result["counts_by_codepoint"], {codepoint: 1})
                self.assertEqual(result["occurrences"][0]["index"], 1)
                self.assertEqual(result["occurrences"][0]["codepoint"], codepoint)
                self.assertEqual(result["occurrences"][0]["name"], name)
                self.assertEqual(result["occurrences"][0]["kind"], kind)
                self.assertEqual(
                    result["has_override"], kind == "override"
                )

    def test_bidi_chars_positions_across_a_string(self) -> None:
        text = f"ab{LRM}cd{RLI} {RLO_SPOOF}"
        # a(0) b(1) LRM(2) c(3) d(4) RLI(5) space(6) then the spoof RLO.
        spoof_offset = 7 + len("photo")
        result = self.tool.execute(mode="bidi_chars", text=text)
        self.assertEqual(
            [o["index"] for o in result["occurrences"]],
            [2, 5, spoof_offset],
        )
        self.assertEqual(
            result["counts_by_codepoint"],
            {"U+200E": 1, "U+202E": 1, "U+2067": 1},
        )
        self.assertTrue(result["has_override"])

    def test_bidi_chars_clean_text(self) -> None:
        result = self.tool.execute(mode="bidi_chars", text="hello שלום")
        self.assertEqual(
            result,
            {
                "mode": "bidi_chars",
                "total_found": 0,
                "counts_by_codepoint": {},
                "occurrences": [],
                "occurrence_list_truncated": False,
                "has_override": False,
                "security_note": result["security_note"],
            },
        )
        self.assertTrue(result["security_note"])  # note is always present

    def test_bidi_chars_occurrence_capping(self) -> None:
        text = "x" + LRM * 150 + "y"
        result = self.tool.execute(mode="bidi_chars", text=text)
        self.assertEqual(result["total_found"], 150)
        self.assertEqual(len(result["occurrences"]), 100)
        self.assertTrue(result["occurrence_list_truncated"])
        self.assertEqual(result["occurrences"][0]["index"], 1)
        self.assertEqual(result["occurrences"][99]["index"], 100)
        # Exactly at the cap the list is not truncated.
        at_cap = self.tool.execute(mode="bidi_chars", text="x" + LRM * 100 + "y")
        self.assertEqual(len(at_cap["occurrences"]), 100)
        self.assertFalse(at_cap["occurrence_list_truncated"])

    # ------------------------------------------------------------------ #
    # strip_bidi mode
    # ------------------------------------------------------------------ #

    def test_strip_bidi_basic_removal(self) -> None:
        result = self.tool.execute(mode="strip_bidi", text=f"ab{LRM}cd{RLO}!")
        self.assertEqual(result["mode"], "strip_bidi")
        self.assertEqual(result["cleaned"], "abcd!")
        self.assertEqual(result["removed_count"], 2)
        self.assertEqual(
            result["removed_by_codepoint"], {"U+200E": 1, "U+202E": 1}
        )
        self.assertTrue(result["changed"])

    def test_strip_bidi_all_eleven_controls(self) -> None:
        joined = "".join(char for char, _, _, _ in ALL_CONTROLS)
        result = self.tool.execute(mode="strip_bidi", text=joined)
        self.assertEqual(result["cleaned"], "")
        self.assertEqual(result["removed_count"], 11)
        self.assertEqual(len(result["removed_by_codepoint"]), 11)

    def test_strip_bidi_no_controls_is_unchanged(self) -> None:
        text = "مرحبا hello 123 !!!"
        result = self.tool.execute(mode="strip_bidi", text=text)
        self.assertEqual(result["cleaned"], text)
        self.assertEqual(result["removed_count"], 0)
        self.assertEqual(result["removed_by_codepoint"], {})
        self.assertFalse(result["changed"])

    def test_strip_bidi_leaves_other_invisibles_alone(self) -> None:
        # Soft hyphen (Cf) and NBSP (Zs) are NOT bidi controls.
        text = "a" + chr(0x00AD) + chr(0x00A0) + "b"
        result = self.tool.execute(mode="strip_bidi", text=text)
        self.assertEqual(result["cleaned"], text)
        self.assertFalse(result["changed"])

    def test_strip_bidi_documents_lrm_rlm_safety(self) -> None:
        result = self.tool.execute(mode="strip_bidi", text=f"a{LRM}{RLM}b")
        self.assertEqual(result["cleaned"], "ab")
        self.assertIn("safe to remove in data contexts", result["note"])
        self.assertIn("LRM (U+200E)", result["note"])

    def test_strip_bidi_round_trips_with_bidi_chars(self) -> None:
        text = f"report{RLO}gnp.exe and note{LRM}"
        found = self.tool.execute(mode="bidi_chars", text=text)
        stripped = self.tool.execute(mode="strip_bidi", text=text)
        self.assertEqual(found["total_found"], stripped["removed_count"])
        self.assertEqual(found["counts_by_codepoint"], stripped["removed_by_codepoint"])
        self.assertEqual(stripped["cleaned"], "reportgnp.exe and note")

    # ------------------------------------------------------------------ #
    # error matrix (strict validation, before any computation)
    # ------------------------------------------------------------------ #

    def test_unknown_mode_raises(self) -> None:
        for mode in ("", "Direction", "DETECT", "detect ", None, 5, True):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode=mode, text="hello")

    def test_missing_text_raises(self) -> None:
        for mode in ("detect", "per_paragraph", "bidi_chars", "strip_bidi"):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode=mode)

    def test_non_string_text_raises(self) -> None:
        for bad in (None, 5, 1.5, True, False, ["ab"], {"a": 1}, b"ab"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="detect", text=bad)

    def test_empty_text_raises(self) -> None:
        for mode in ("detect", "per_paragraph", "bidi_chars", "strip_bidi"):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode=mode, text="")

    def test_oversized_text_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="detect", text="a" * 100_001)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="strip_bidi", text=ARABIC_HELLO * 20_001)

    # ------------------------------------------------------------------ #
    # determinism and registration
    # ------------------------------------------------------------------ #

    def test_repeated_calls_are_deterministic(self) -> None:
        text = f"{MIXED_EN_HE}\n\n{ARABIC_HELLO}{RLM} {RLO_SPOOF}"
        for mode in ("detect", "per_paragraph", "bidi_chars", "strip_bidi"):
            with self.subTest(mode=mode):
                first = self.tool.execute(mode=mode, text=text)
                for _ in range(3):
                    self.assertEqual(self.tool.execute(mode=mode, text=text), first)

    def test_default_attributes_and_registration(self) -> None:
        self.assertEqual(self.tool.name, "text_directionality_tool")
        self.assertIn("detect", self.tool.description)
        self.assertEqual(
            TextDirectionalityTool, DirectTextDirectionalityTool
        )

    def test_mode_echo_in_every_result(self) -> None:
        for mode in ("detect", "per_paragraph", "bidi_chars", "strip_bidi"):
            with self.subTest(mode=mode):
                result = self.tool.execute(mode=mode, text=MIXED_EN_HE)
                self.assertEqual(result["mode"], mode)


if __name__ == "__main__":
    unittest.main()
