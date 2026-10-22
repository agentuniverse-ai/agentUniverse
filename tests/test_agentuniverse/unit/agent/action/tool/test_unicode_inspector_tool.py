#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_unicode_inspector_tool.py

"""Offline unit tests for UnicodeInspectorTool.

The tool is built purely on the standard library (``unicodedata`` plus
``difflib``) and never touches the network, so this suite runs fully
offline. Every assertion is deterministic: per-character records are
checked against hand-verified Unicode properties, the three length
metrics against hand-computed values, script-mix counts against
hand-counted buckets, and normalization results against the canonical
NFC/NFD/NFKC/NFKD definitions. No value in this file is derived by
calling ``unicodedata`` on the expected side first (except where the
assertion is explicitly about consistency, e.g. idempotence).
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import UnicodeInspectorTool
from agentuniverse.agent.action.tool.common_tool.unicode_inspector_tool import (
    UnicodeInspectorTool as DirectUnicodeInspectorTool,
)

E_ACUTE = "é"                      # U+00E9, NFD: e + U+0301
E_COMPOSED = "e\u0301"             # NFC-normalizes back to é
CJK_ZHONG = "中"                   # U+4E2D
GRINNING = "\U0001F600"            # 😀 U+1F600
MIXED_LENGTHS = "a中😀"            # 3 code points, 8 UTF-8 bytes, 4 UTF-16 units
MIXED_SENTENCE = "Hello, 世界! 123 안녕"


class UnicodeInspectorToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib UnicodeInspectorTool."""

    def setUp(self) -> None:
        self.tool = UnicodeInspectorTool()

    # ------------------------------------------------------------------ #
    # inspect mode — per-character ground truths
    # ------------------------------------------------------------------ #

    def test_inspect_single_char_e_acute(self) -> None:
        result = self.tool.execute(mode="inspect", text=E_ACUTE)
        self.assertEqual(
            result,
            {
                "mode": "inspect",
                "total_chars": 1,
                "returned_chars": 1,
                "truncated": False,
                "characters": [
                    {
                        "index": 0,
                        "char": "é",
                        "codepoint": "U+00E9",
                        "hex": "e9",
                        "name": "LATIN SMALL LETTER E WITH ACUTE",
                        "category": "Ll (Lowercase Letter)",
                        "bidi_class": "L",
                        "east_asian_width": (
                            "A (ambiguous — one or two columns depending on context)"
                        ),
                        "decomposition": "0065 0301",
                        "is_emoji_ish": False,
                    }
                ],
            },
        )

    def test_inspect_single_char_cjk_zhong(self) -> None:
        record = self.tool.execute(mode="inspect", text=CJK_ZHONG)["characters"][0]
        self.assertEqual(record["char"], "中")
        self.assertEqual(record["codepoint"], "U+4E2D")
        self.assertEqual(record["hex"], "4e2d")
        self.assertEqual(record["name"], "CJK UNIFIED IDEOGRAPH-4E2D")
        self.assertEqual(record["category"], "Lo (Other Letter)")
        self.assertEqual(record["bidi_class"], "L")
        self.assertTrue(record["east_asian_width"].startswith("W ("))
        self.assertIn("two columns", record["east_asian_width"])
        self.assertIsNone(record["decomposition"])
        self.assertFalse(record["is_emoji_ish"])

    def test_inspect_emoji_is_symbol_other(self) -> None:
        record = self.tool.execute(mode="inspect", text=GRINNING)["characters"][0]
        self.assertEqual(record["char"], GRINNING)
        self.assertEqual(record["codepoint"], "U+1F600")
        self.assertEqual(record["hex"], "1f600")
        self.assertEqual(record["name"], "GRINNING FACE")
        self.assertEqual(record["category"], "So (Other Symbol)")
        self.assertEqual(record["bidi_class"], "ON")
        self.assertTrue(record["east_asian_width"].startswith("W ("))
        self.assertIsNone(record["decomposition"])
        # The is-emoji-ish flag is defined as category == So.
        self.assertTrue(record["is_emoji_ish"])

    def test_inspect_ascii_letter(self) -> None:
        record = self.tool.execute(mode="inspect", text="a")["characters"][0]
        self.assertEqual(record["codepoint"], "U+0061")
        self.assertEqual(record["hex"], "61")
        self.assertEqual(record["name"], "LATIN SMALL LETTER A")
        self.assertEqual(record["category"], "Ll (Lowercase Letter)")
        self.assertEqual(record["bidi_class"], "L")
        self.assertTrue(record["east_asian_width"].startswith("Na ("))
        self.assertIsNone(record["decomposition"])

    def test_inspect_unassigned_codepoint_is_unnamed(self) -> None:
        # U+0378 is famously unassigned in the Unicode database.
        record = self.tool.execute(mode="inspect", text="\u0378")["characters"][0]
        self.assertEqual(record["name"], "<unnamed>")
        self.assertTrue(record["category"].startswith("Cn ("))
        self.assertIsNone(record["decomposition"])
        self.assertFalse(record["is_emoji_ish"])

    def test_inspect_multi_char_order_and_indices(self) -> None:
        result = self.tool.execute(mode="inspect", text="a" + E_ACUTE + GRINNING)
        self.assertEqual(result["total_chars"], 3)
        self.assertEqual([r["char"] for r in result["characters"]], ["a", "é", GRINNING])
        self.assertEqual([r["index"] for r in result["characters"]], [0, 1, 2])
        self.assertEqual([r["codepoint"] for r in result["characters"]],
                         ["U+0061", "U+00E9", "U+1F600"])

    def test_inspect_cap_at_100_chars_with_count(self) -> None:
        result = self.tool.execute(mode="inspect", text="x" * 150)
        self.assertEqual(result["total_chars"], 150)
        self.assertEqual(result["returned_chars"], 100)
        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["characters"]), 100)
        self.assertEqual(result["characters"][0]["char"], "x")
        self.assertEqual(result["characters"][99]["index"], 99)

    def test_inspect_exactly_100_chars_not_truncated(self) -> None:
        result = self.tool.execute(mode="inspect", text="y" * 100)
        self.assertEqual(result["total_chars"], 100)
        self.assertEqual(result["returned_chars"], 100)
        self.assertFalse(result["truncated"])

    # ------------------------------------------------------------------ #
    # string_stats mode — hand-computed ground truths
    # ------------------------------------------------------------------ #

    def test_string_stats_three_length_metrics(self) -> None:
        # "a中😀": 3 code points; UTF-8 = 1 + 3 + 4 = 8 bytes;
        # UTF-16 = 1 + 1 + 2 = 4 code units (the emoji is astral).
        result = self.tool.execute(mode="string_stats", text=MIXED_LENGTHS)
        self.assertEqual(result["lengths"], {
            "code_points": 3,
            "utf8_bytes": 8,
            "utf16_units": 4,
        })
        self.assertEqual(result["total_chars"], 3)

    def test_string_stats_bmp_only_lengths(self) -> None:
        # "Привет": 6 code points, each 2 UTF-8 bytes, all BMP.
        result = self.tool.execute(mode="string_stats", text="Привет")
        self.assertEqual(result["lengths"], {
            "code_points": 6,
            "utf8_bytes": 12,
            "utf16_units": 6,
        })

    def test_string_stats_script_mix_hand_counted(self) -> None:
        # "Hello, 世界! 123 안녕" hand count:
        # latin H e l l o = 5; punct , ! = 2; whitespace = 3;
        # cjk 世界 = 2; digits 1 2 3 = 3; hangul 안녕 = 2. Total 17.
        result = self.tool.execute(mode="string_stats", text=MIXED_SENTENCE)
        self.assertEqual(result["total_chars"], 17)
        self.assertEqual(result["script_counts"], {
            "latin": 5, "cjk": 2, "hangul": 2, "kana": 0,
            "cyrillic": 0, "greek": 0, "arabic": 0, "hebrew": 0,
            "digits": 3, "punctuation": 2, "symbols": 0,
            "whitespace": 3, "other": 0,
        })
        self.assertEqual(result["lengths"], {
            "code_points": 17,
            "utf8_bytes": 25,   # 9 ASCII + 2*3 CJK + 2*3 Hangul
            "utf16_units": 17,
        })

    def test_string_stats_individual_scripts(self) -> None:
        cases = [
            ("abc", "latin", 3),
            (" Привет", "cyrillic", 6),
            ("γεια σας", "greek", 7),
            ("مرحبا", "arabic", 5),
            ("שלום", "hebrew", 4),
            ("こんにちは", "kana", 5),
            ("カタカナ", "kana", 4),
            ("안녕", "hangul", 2),
            ("中文", "cjk", 2),
        ]
        for text, bucket, expected in cases:
            with self.subTest(text=text):
                counts = self.tool.execute(mode="string_stats", text=text)[
                    "script_counts"
                ]
                self.assertEqual(counts[bucket], expected)

    def test_string_stats_digit_punct_symbol_whitespace(self) -> None:
        # "Hi! 42?" — latin H i = 2, punct ! ? = 2, whitespace = 1,
        # digits 4 2 = 2.
        counts = self.tool.execute(mode="string_stats", text="Hi! 42?")[
            "script_counts"
        ]
        self.assertEqual(counts["latin"], 2)
        self.assertEqual(counts["digits"], 2)
        self.assertEqual(counts["punctuation"], 2)
        self.assertEqual(counts["whitespace"], 1)

    def test_string_stats_counts_always_sum_to_total(self) -> None:
        for text in (MIXED_SENTENCE, MIXED_LENGTHS, "e\u0301", "\u00A0\t~^"):
            with self.subTest(text=repr(text)):
                result = self.tool.execute(mode="string_stats", text=text)
                self.assertEqual(
                    sum(result["script_counts"].values()), result["total_chars"]
                )

    def test_string_stats_combining_mark_goes_to_other(self) -> None:
        # The decomposed acute accent is a nonspacing mark (Mn) — not in
        # any script bucket, not a digit/punct/symbol — so it lands in
        # the documented catch-all "other" bucket.
        counts = self.tool.execute(mode="string_stats", text=E_COMPOSED)[
            "script_counts"
        ]
        self.assertEqual(counts["latin"], 1)
        self.assertEqual(counts["other"], 1)

    def test_string_stats_nfkc_form(self) -> None:
        # NFKC folds the circled digit to an ASCII digit and the
        # fullwidth letters to plain ASCII, and leaves CJK alone.
        result = self.tool.execute(mode="string_stats", text="①ﬁ")
        self.assertEqual(result["nfkc"], "1fi")
        result = self.tool.execute(mode="string_stats", text=MIXED_SENTENCE)
        self.assertEqual(result["nfkc"], MIXED_SENTENCE)

    # ------------------------------------------------------------------ #
    # normalize mode — canonical form ground truths
    # ------------------------------------------------------------------ #

    def test_normalize_nfd_of_e_acute(self) -> None:
        result = self.tool.execute(mode="normalize", text=E_ACUTE, form="NFD")
        self.assertEqual(
            result,
            {
                "mode": "normalize",
                "form": "NFD",
                "result": E_COMPOSED,
                "changed": True,
                "changed_count": 1,
                "changed_positions": [0],
                "changed_positions_truncated": False,
            },
        )

    def test_normalize_nfc_of_decomposed_e_acute(self) -> None:
        result = self.tool.execute(mode="normalize", text=E_COMPOSED, form="NFC")
        self.assertEqual(result["result"], E_ACUTE)
        self.assertTrue(result["changed"])
        self.assertEqual(result["changed_count"], 2)
        self.assertEqual(result["changed_positions"], [0, 1])

    def test_normalize_idempotent_form_reports_unchanged(self) -> None:
        result = self.tool.execute(mode="normalize", text=E_ACUTE, form="NFC")
        self.assertEqual(result["result"], E_ACUTE)
        self.assertFalse(result["changed"])
        self.assertEqual(result["changed_count"], 0)
        self.assertEqual(result["changed_positions"], [])

    def test_normalize_nfkc_known_folds(self) -> None:
        cases = [
            ("①", "1"),
            ("ﬁ", "fi"),
            ("ｆｕｌｌ", "full"),
            ("Ⅻ", "XII"),
            ("½", "1⁄2"),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                result = self.tool.execute(
                    mode="normalize", text=source, form="NFKC"
                )
                self.assertEqual(result["result"], expected)
                self.assertTrue(result["changed"])

    def test_normalize_nfkd_known_folds(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="normalize", text="①", form="NFKD")["result"],
            "1",
        )
        self.assertEqual(
            self.tool.execute(mode="normalize", text=E_ACUTE, form="NFKD")["result"],
            E_COMPOSED,
        )

    def test_normalize_changed_positions_partial_string(self) -> None:
        # Only the é at the end changes; "caf" is untouched.
        result = self.tool.execute(mode="normalize", text="café", form="NFD")
        self.assertEqual(result["result"], "cafe\u0301")
        self.assertEqual(result["changed_positions"], [3])

    def test_normalize_changed_positions_capped(self) -> None:
        result = self.tool.execute(mode="normalize", text=E_ACUTE * 150, form="NFD")
        self.assertTrue(result["changed"])
        self.assertEqual(result["changed_count"], 150)
        self.assertEqual(result["changed_positions"], list(range(100)))
        self.assertTrue(result["changed_positions_truncated"])

    def test_normalize_canonical_round_trip(self) -> None:
        # NFC(NFD(x)) recomposes the canonically equivalent string.
        decomposed = self.tool.execute(
            mode="normalize", text="café 日本 😀", form="NFD"
        )["result"]
        recomposed = self.tool.execute(
            mode="normalize", text=decomposed, form="NFC"
        )["result"]
        self.assertEqual(recomposed, "café 日本 😀")

    def test_normalize_all_forms_idempotent(self) -> None:
        text = "①é中ﬁ ａ"
        for form in ("NFC", "NFD", "NFKC", "NFKD"):
            with self.subTest(form=form):
                once = self.tool.execute(mode="normalize", text=text, form=form)
                twice = self.tool.execute(mode="normalize", text=once["result"], form=form)
                self.assertEqual(twice["result"], once["result"])
                self.assertFalse(twice["changed"])

    # ------------------------------------------------------------------ #
    # Determinism
    # ------------------------------------------------------------------ #

    def test_repeated_calls_are_deterministic(self) -> None:
        for mode, form in (("inspect", None), ("string_stats", None), ("normalize", "NFC")):
            with self.subTest(mode=mode):
                kwargs = {"mode": mode, "text": MIXED_SENTENCE}
                if form:
                    kwargs["form"] = form
                self.assertEqual(self.tool.execute(**kwargs), self.tool.execute(**kwargs))

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="unicode", text="a")
        self.assert_invalid(mode=None, text="a")
        self.assert_invalid(mode=123, text="a")
        self.assert_invalid(mode="INSPECT", text="a")

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"hello", ["hello"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="inspect", text=bad)
                self.assert_invalid(mode="string_stats", text=bad)
                self.assert_invalid(mode="normalize", text=bad, form="NFC")

    def test_empty_text_rejected(self) -> None:
        self.assert_invalid(mode="inspect", text="")
        self.assert_invalid(mode="string_stats", text="")
        self.assert_invalid(mode="normalize", text="", form="NFD")

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        self.assert_invalid(mode="inspect", text=oversized)
        self.assert_invalid(mode="string_stats", text=oversized)
        self.assert_invalid(mode="normalize", text=oversized, form="NFC")
        # Exactly at the limit the inspect mode still caps its records.
        ok = self.tool.execute(mode="inspect", text="a" * 100_000)
        self.assertEqual(ok["total_chars"], 100_000)
        self.assertEqual(ok["returned_chars"], 100)

    def test_invalid_form(self) -> None:
        for bad in ("NFK", "nfc", "nfkc", None, 123, True, ""):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="normalize", text="a", form=bad)

    def test_form_ignored_by_other_modes(self) -> None:
        # Mirrors the other common tools: irrelevant parameters are
        # accepted and ignored.
        result = self.tool.execute(mode="inspect", text="a", form="NFK")
        self.assertEqual(result["characters"][0]["char"], "a")
        result = self.tool.execute(mode="string_stats", text="a", form="bogus")
        self.assertEqual(result["script_counts"]["latin"], 1)

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectUnicodeInspectorTool, UnicodeInspectorTool)
        self.assertEqual(self.tool.name, "unicode_inspector_tool")
        self.assertIn("inspect", self.tool.description)
        self.assertIn("string_stats", self.tool.description)
        self.assertIn("normalize", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("UnicodeInspectorTool", __all__)


if __name__ == "__main__":
    unittest.main()
