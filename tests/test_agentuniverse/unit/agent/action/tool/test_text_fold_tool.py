#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_text_fold_tool.py

"""Offline unit tests for TextFoldTool.

The tool is built purely on the standard library ``unicodedata``
module and never touches the network, so this suite runs fully
offline. Every assertion is deterministic: the folding ground truths
are hand-verified literals (café == cafe, ﬁ == fi, ＡＢＣ == abc,
the symbol map, ß -> ss, Greek final sigma, CJK / Hangul / kana
behavior), the pipeline invariants (idempotence over every single
code point of the BMP plus 300 seeded random texts, and the
per-character fragment sum that ``reverse_map`` evidence rests on)
are recomputed independently inside the tests with plain stdlib
calls, and the error matrix pins every validation branch.
"""

import random
import unittest
import unicodedata

from agentuniverse.agent.action.tool.common_tool import TextFoldTool
from agentuniverse.agent.action.tool.common_tool.text_fold_tool import (
    TextFoldTool as DirectTextFoldTool,
)

# --------------------------------------------------------------------- #
# Hand-verified ground truths (independent literals)
# --------------------------------------------------------------------- #

# é as one precomposed code point and as e + combining acute.
E_PRECOMPOSED = "café"
E_DECOMPOSED = "café"  # e + U+0301
FOLDED_CAFE = "cafe"

# Compatibility forms folded by NFKD.
LIGATURE_FILE = "ﬁle"  # U+FB01 ligature fi
FULLWIDTH_ABC = "ＡＢＣ"
SUPERSCRIPT_X2 = "x²"
HALFWIDTH_KANA = "ｶﾌｪ"
KANA = "カフェ"

# CJK: Han ideographs have no decomposition — untouched by NFKD.
HAN = "汉字测试"
TRADITIONAL_HAN = "漢字"  # a DIFFERENT character, must stay different

# Hangul: a precomposed syllable and its explicit Jamo sequence
# NFKD-decompose to the SAME Jamo — search equality is the point.
HANGUL_PRECOMPOSED = "가"  # U+AC00
HANGUL_JAMO = "가"  # U+1100 U+1161

# Turkish dotless/dotted i: İ folds to i (mark stripped before the
# case fold), ı stays ı (case folding is locale-independent).
TURKISH_DOTTED = "İ"  # U+0130

# Greek: Σ / ς / σ all case-fold to σ (final-sigma rule erased).
GREEK_UPPER = "ΟΔΟΣ"
GREEK_ACCENTED = "οδός"
GREEK_SIGMA_VARIANTS = ["σ", "ς", "Σ"]


def _independent_fold(text: str) -> str:
    """The documented pipeline, rebuilt from the stdlib alone."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(
        ch
        for ch in decomposed
        if unicodedata.category(ch) not in ("Mn", "Me")
    )
    symbol_map = {
        "×": "x", "÷": "/", "’": "'", "“": '"', "”": '"',
        "–": "-", "—": "-", "…": "...",
    }
    mapped = "".join(symbol_map.get(ch, ch) for ch in stripped)
    return " ".join(mapped.casefold().split())


def _independent_rules(text: str) -> dict:
    """The first transforming pipeline rule per character, rebuilt."""
    rules = {}
    for index, ch in enumerate(text):
        if unicodedata.normalize("NFKD", ch) != ch:
            rules[index] = "nfkd_decomposition"
        elif unicodedata.category(ch) in ("Mn", "Me"):
            rules[index] = "mark_stripped"
        elif ch in TextFoldTool.SYMBOL_MAP:
            rules[index] = "symbol_mapped"
        elif ch.casefold() != ch:
            rules[index] = "case_folded"
        elif ch.isspace() and ch != " ":
            rules[index] = "whitespace_collapsed"
    return rules


class TextFoldToolFoldTest(unittest.TestCase):
    """The fold mode — ground truths of the five-stage pipeline."""

    def setUp(self) -> None:
        self.tool = TextFoldTool()

    def test_metadata(self) -> None:
        self.assertEqual(self.tool.name, "text_fold_tool")
        self.assertIn("fold", self.tool.description)
        self.assertTrue(DirectTextFoldTool is TextFoldTool)

    def test_fold_echoes_documented_pipeline(self) -> None:
        result = self.tool.execute(mode="fold", text="Anything")
        self.assertEqual(
            result["pipeline"],
            [
                "nfkd_decomposition",
                "combining_mark_strip",
                "symbol_map",
                "case_fold",
                "whitespace_collapse",
            ],
        )

    def test_fold_accent_insensitive(self) -> None:
        for variant in (E_PRECOMPOSED, E_DECOMPOSED, "CAFE", "Café"):
            result = self.tool.execute(mode="fold", text=variant)
            self.assertEqual(result["folded"], FOLDED_CAFE)
            self.assertFalse(result["is_empty_after_fold"])

    def test_fold_compatibility_forms(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="fold", text=LIGATURE_FILE)["folded"],
            "file",
        )
        self.assertEqual(
            self.tool.execute(mode="fold", text=FULLWIDTH_ABC)["folded"],
            "abc",
        )
        self.assertEqual(
            self.tool.execute(mode="fold", text=SUPERSCRIPT_X2)["folded"],
            "x2",
        )
        self.assertEqual(
            self.tool.execute(mode="fold", text=HALFWIDTH_KANA)["folded"],
            KANA,
        )

    def test_fold_symbol_map_ground_truths(self) -> None:
        cases = {
            "×": "x",
            "÷": "/",
            "2×3": "2x3",
            "x÷y": "x/y",
            "don’t": "don't",
            "“a”": '"a"',
            "a–b": "a-b",
            "a—b": "a-b",
            "…": "...",
            "1…5": "1...5",
        }
        for text, expected in cases.items():
            self.assertEqual(
                self.tool.execute(mode="fold", text=text)["folded"],
                expected,
                msg=repr(text),
            )

    def test_fold_symbol_map_is_the_documented_table(self) -> None:
        self.assertEqual(
            dict(TextFoldTool.SYMBOL_MAP),
            {
                "×": "x", "÷": "/", "’": "'", "“": '"', "”": '"',
                "–": "-", "—": "-", "…": "...",
            },
        )
        # Every map target EXCEPT … survives NFKD unchanged — the map
        # is applied to the post-NFKD canonical alphabet. … is the one
        # documented exception: NFKD itself expands it to "...", and
        # the map entry is kept so the behavior does not depend on
        # that side effect of the decomposition tables.
        for symbol in TextFoldTool.SYMBOL_MAP:
            if symbol == "…":
                self.assertEqual(
                    unicodedata.normalize("NFKD", symbol), "..."
                )
            else:
                self.assertEqual(
                    unicodedata.normalize("NFKD", symbol), symbol
                )

    def test_fold_casefold_specials(self) -> None:
        # ß -> ss via full case folding (documented).
        self.assertEqual(
            self.tool.execute(mode="fold", text="Straße")["folded"],
            "strasse",
        )
        self.assertEqual(
            self.tool.execute(mode="fold", text="STRASSE")["folded"],
            "strasse",
        )
        # Greek final sigma: all three sigma forms fold to σ.
        for variant in GREEK_SIGMA_VARIANTS:
            self.assertEqual(
                self.tool.execute(mode="fold", text=variant)["folded"],
                "σ",
            )
        self.assertEqual(
            self.tool.execute(mode="fold", text=GREEK_UPPER)["folded"],
            "οδοσ",
        )
        self.assertEqual(
            self.tool.execute(mode="fold", text=GREEK_ACCENTED)["folded"],
            "οδοσ",
        )
        # Turkish İ -> i (combining dot stripped before casefold);
        # dotless ı stays ı (locale-independent folding).
        self.assertEqual(
            self.tool.execute(mode="fold", text=TURKISH_DOTTED)["folded"],
            "i",
        )
        self.assertEqual(
            self.tool.execute(mode="fold", text="ı")["folded"],
            "ı",
        )

    def test_fold_cjk_safety(self) -> None:
        # Han ideographs: no decomposition of any kind — untouched.
        self.assertEqual(
            self.tool.execute(mode="fold", text=HAN)["folded"],
            HAN,
        )
        # Simplified and traditional forms are DIFFERENT characters
        # and must stay different keys (folding is not translation).
        self.assertNotEqual(
            self.tool.execute(mode="fold", text="汉")["folded"],
            self.tool.execute(mode="fold", text=TRADITIONAL_HAN)["folded"],
        )
        # Hangul: precomposed syllable == explicit Jamo sequence.
        self.assertEqual(
            self.tool.execute(mode="fold", text=HANGUL_PRECOMPOSED)["folded"],
            self.tool.execute(mode="fold", text=HANGUL_JAMO)["folded"],
        )
        # Kana is preserved (only halfwidth <-> fullwidth merges).
        self.assertEqual(
            self.tool.execute(mode="fold", text=KANA)["folded"],
            KANA,
        )

    def test_fold_whitespace_collapse(self) -> None:
        cases = {
            "a   b": "a b",
            "a\t\nb": "a b",
            "a b": "a b",       # NBSP -> space via NFKD, then collapse
            "　x　": "x",       # U+3000 ideographic space
            "   ": "",
        }
        for text, expected in cases.items():
            result = self.tool.execute(mode="fold", text=text)
            self.assertEqual(result["folded"], expected, msg=repr(text))
        self.assertTrue(
            self.tool.execute(mode="fold", text="   ")["is_empty_after_fold"]
        )

    def test_fold_combined_pipeline(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="fold", text="Ｃafé ﬁle… don’t  “ Panic ”"
            )["folded"],
            'cafe file... don\'t " panic "',
        )

    def test_fold_matches_independent_rebuild(self) -> None:
        for text in (
            E_PRECOMPOSED, E_DECOMPOSED, LIGATURE_FILE, FULLWIDTH_ABC,
            SUPERSCRIPT_X2, HALFWIDTH_KANA, HAN, HANGUL_PRECOMPOSED,
            GREEK_UPPER, "×÷’“”–—…", "MiXeD   Whitespace", TURKISH_DOTTED,
        ):
            self.assertEqual(
                self.tool.execute(mode="fold", text=text)["folded"],
                _independent_fold(text),
                msg=repr(text),
            )


class TextFoldToolSearchKeyTest(unittest.TestCase):
    """The search_key mode — non-alphanumeric runs squashed to '-'."""

    def setUp(self) -> None:
        self.tool = TextFoldTool()

    def test_search_key_punctuation_squashing(self) -> None:
        cases = {
            "Hello, World!": "hello-world",
            "café  --  bar": "cafe-bar",
            "ﬁlename.txt": "filename-txt",
            "a...b---c": "a-b-c",
            "!!!": "",
            " leading and trailing!! ": "leading-and-trailing",
        }
        for text, expected in cases.items():
            result = self.tool.execute(mode="search_key", text=text)
            self.assertEqual(result["search_key"], expected, msg=repr(text))
            self.assertEqual(result["separator"], "-")

    def test_search_key_accent_and_case_equality(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="search_key", text="Çafé")["search_key"],
            self.tool.execute(mode="search_key", text="CAFE")["search_key"],
        )
        self.assertEqual(
            self.tool.execute(mode="search_key", text=HALFWIDTH_KANA)["search_key"],
            self.tool.execute(mode="search_key", text=KANA)["search_key"],
        )

    def test_search_key_cjk_word_characters(self) -> None:
        # Han / kana are Unicode word characters: NOT squashed, only
        # the separating punctuation becomes the separator.
        self.assertEqual(
            self.tool.execute(mode="search_key", text="你好，世界！")["search_key"],
            "你好-世界",
        )
        self.assertEqual(
            self.tool.execute(mode="search_key", text="汉字 测试")["search_key"],
            "汉字-测试",
        )
        # Fullwidth punctuation is NFKD-folded to ASCII punctuation
        # first, then squashed — ，！ never reach the key verbatim.

    def test_search_key_reports_underlying_fold(self) -> None:
        result = self.tool.execute(mode="search_key", text="Hello, World!")
        self.assertEqual(result["folded"], "hello, world!")


class TextFoldToolCompareTest(unittest.TestCase):
    """The compare mode — key equality and differing positions."""

    def setUp(self) -> None:
        self.tool = TextFoldTool()

    def test_compare_equal_after_fold(self) -> None:
        result = self.tool.execute(
            mode="compare", text_1="café", text_2="CAFE"
        )
        self.assertTrue(result["equal_after_fold"])
        self.assertEqual(result["key1"], FOLDED_CAFE)
        self.assertEqual(result["key2"], FOLDED_CAFE)
        self.assertEqual(result["differing_count"], 0)
        self.assertEqual(result["differing_positions"], [])
        self.assertFalse(result["truncated"])

    def test_compare_width_and_ligature_equality(self) -> None:
        result = self.tool.execute(
            mode="compare", text_1="ＡＢＣ ﬁle", text_2="ABC file"
        )
        self.assertTrue(result["equal_after_fold"])
        self.assertEqual(result["key1"], "abc file")

    def test_compare_single_differing_position(self) -> None:
        result = self.tool.execute(mode="compare", text_1="abc", text_2="abd")
        self.assertFalse(result["equal_after_fold"])
        self.assertEqual(result["differing_count"], 1)
        self.assertEqual(
            result["differing_positions"],
            [{"position": 2, "key1_char": "c", "key2_char": "d"}],
        )

    def test_compare_length_difference(self) -> None:
        result = self.tool.execute(mode="compare", text_1="ab", text_2="abc")
        self.assertFalse(result["equal_after_fold"])
        self.assertEqual(
            result["differing_positions"],
            [{"position": 2, "key1_char": None, "key2_char": "c"}],
        )
        result = self.tool.execute(mode="compare", text_1="abcd", text_2="ab")
        self.assertEqual(
            result["differing_positions"],
            [{"position": 2, "key1_char": "c", "key2_char": None},
             {"position": 3, "key1_char": "d", "key2_char": None}],
        )

    def test_compare_positions_capped_at_20(self) -> None:
        # 30 common positions all differing -> capped listing.
        first = "a" * 30
        second = "b" * 30
        result = self.tool.execute(
            mode="compare", text_1=first, text_2=second
        )
        self.assertEqual(result["differing_count"], 30)
        self.assertEqual(len(result["differing_positions"]), 20)
        self.assertTrue(result["truncated"])
        self.assertEqual(
            result["differing_positions"][0]["position"], 0
        )
        self.assertEqual(
            result["differing_positions"][-1]["position"], 19
        )

    def test_compare_fold_equality_but_search_key_difference(self) -> None:
        # Fold keys differ only by punctuation; search keys equal.
        result = self.tool.execute(
            mode="compare", text_1="café-bar", text_2="cafe bar"
        )
        self.assertFalse(result["equal_after_fold"])
        self.assertTrue(result["equal_after_search_key"])
        self.assertEqual(result["len_key1"], 8)
        self.assertEqual(result["len_key2"], 8)

    def test_compare_matches_fold_mode_keys(self) -> None:
        result = self.tool.execute(
            mode="compare", text_1="Straße", text_2="STRASSE"
        )
        self.assertEqual(
            result["key1"],
            self.tool.execute(mode="fold", text="Straße")["folded"],
        )
        self.assertEqual(result["key1"], "strasse")


    def test_compare_nbsp_equals_plain_space(self) -> None:
        result = self.tool.execute(
            mode="compare", text_1="a\u00A0b", text_2="a b"
        )
        self.assertTrue(result["equal_after_fold"])
        self.assertTrue(result["equal_after_search_key"])


class TextFoldToolReverseMapTest(unittest.TestCase):
    """The reverse_map mode — the per-character mapping evidence."""

    def setUp(self) -> None:
        self.tool = TextFoldTool()

    def test_reverse_map_evidence_for_accented_word(self) -> None:
        result = self.tool.execute(
            mode="reverse_map", text="Café", folded_key="cafe"
        )
        self.assertTrue(result["matches"])
        self.assertEqual(result["evidence_count"], 2)
        self.assertEqual(result["unchanged_count"], 2)
        rules = {entry["index"]: entry for entry in result["evidence"]}
        self.assertEqual(rules[0]["original"], "C")
        self.assertEqual(rules[0]["rule"], "case_folded")
        self.assertEqual(rules[0]["folded_to"], "c")
        self.assertEqual(rules[0]["codepoint"], "U+0043")
        self.assertEqual(rules[3]["original"], "é")
        self.assertEqual(rules[3]["rule"], "nfkd_decomposition")
        self.assertEqual(rules[3]["folded_to"], "e")
        self.assertEqual(rules[3]["codepoint"], "U+00E9")
        self.assertEqual(
            result["rule_counts"], {"case_folded": 1, "nfkd_decomposition": 1}
        )

    def test_reverse_map_every_rule_fires(self) -> None:
        # mark, whitespace(tab), symbol, casefold, ligature — a plain
        # space maps to itself and stays unchanged by design; ASCII
        # whitespace that changes (tab) fires whitespace_collapsed,
        # while NBSP / the ideographic space transform at stage 1 and
        # fire nfkd_decomposition instead.
        text = "é́\t× ß ﬁ  x"  # also a standalone combining acute
        key = self.tool.execute(mode="fold", text=text)["folded"]
        self.assertEqual(key, "e x ss fi x")
        result = self.tool.execute(
            mode="reverse_map", text=text, folded_key=key
        )
        self.assertTrue(result["matches"])
        fired = set(result["rule_counts"])
        self.assertIn("mark_stripped", fired)
        self.assertIn("symbol_mapped", fired)
        self.assertIn("case_folded", fired)
        self.assertIn("nfkd_decomposition", fired)
        self.assertIn("whitespace_collapsed", fired)
        for entry in result["evidence"]:
            self.assertIsInstance(entry["codepoint"], str)
            self.assertTrue(entry["codepoint"].startswith("U+"))

    def test_reverse_map_standalone_mark_and_symbol(self) -> None:
        result = self.tool.execute(
            mode="reverse_map", text="é", folded_key="e"
        )
        entry = result["evidence"][0]
        self.assertEqual(entry["codepoint"], "U+0301")
        self.assertEqual(entry["rule"], "mark_stripped")
        self.assertEqual(entry["folded_to"], "")
        result = self.tool.execute(
            mode="reverse_map", text="×", folded_key="x"
        )
        self.assertEqual(
            result["evidence"],
            [{
                "index": 0,
                "original": "×",
                "codepoint": "U+00D7",
                "rule": "symbol_mapped",
                "folded_to": "x",
            }],
        )

    def test_reverse_map_mismatch_returns_error_payload(self) -> None:
        result = self.tool.execute(
            mode="reverse_map", text="file", folded_key="cafe"
        )
        self.assertEqual(result["error"], "key_mismatch")
        self.assertFalse(result.get("matches", False))
        self.assertEqual(result["provided_key"], "cafe")
        self.assertEqual(result["expected_key"], "file")

    def test_reverse_map_evidence_capped(self) -> None:
        text = "A" * 250
        key = self.tool.execute(mode="fold", text=text)["folded"]
        result = self.tool.execute(
            mode="reverse_map", text=text, folded_key=key
        )
        self.assertEqual(result["evidence_count"], 250)
        self.assertEqual(len(result["evidence"]), 200)
        self.assertTrue(result["truncated"])

    def test_reverse_map_rule_follows_pipeline_order(self) -> None:
        for ch in ("\u00A0", "\u2000", "\u2003", "\u202F", "\u3000"):
            result = self.tool.execute(
                mode="reverse_map",
                text=ch,
                folded_key=TextFoldTool.fold_text(ch),
            )
            self.assertEqual(result["folded_key"], "")
            self.assertTrue(result["matches"], msg=repr(ch))
            entry = result["evidence"][0]
            self.assertEqual(entry["rule"], "nfkd_decomposition")
            self.assertEqual(entry["folded_to"], " ")
        for ch in ("\t", "\n", "\x0b", "\u0085", "\u1680"):
            result = self.tool.execute(
                mode="reverse_map",
                text=ch,
                folded_key=TextFoldTool.fold_text(ch),
            )
            self.assertEqual(
                result["evidence"][0]["rule"], "whitespace_collapsed"
            )
        result = self.tool.execute(mode="reverse_map", text=" ", folded_key="")
        self.assertEqual(result["evidence"], [])
        self.assertEqual(result["evidence_count"], 0)

    def test_reverse_map_format_characters_kept_by_fold(self) -> None:
        for ch in ("\u200D", "\u200C", "\u200E", "\u200F", "\u00AD", "\u2060"):
            self.assertEqual(TextFoldTool.fold_text(ch), ch)
            self.assertEqual(
                self.tool.execute(
                    mode="search_key", text="a" + ch + "b"
                )["search_key"],
                "a-b",
            )
        family = "\U0001F469\u200D\U0001F4BB"
        self.assertEqual(TextFoldTool.fold_text(family), family)
        result = self.tool.execute(
            mode="reverse_map", text=family, folded_key=family
        )
        self.assertTrue(result["matches"])
        self.assertEqual(result["unchanged_count"], 3)

    def test_reverse_map_marks_only_text_folds_to_empty_key(self) -> None:
        text = "̧́̈"
        folded = self.tool.execute(mode="fold", text=text)
        self.assertEqual(folded["folded"], "")
        self.assertTrue(folded["is_empty_after_fold"])
        result = self.tool.execute(
            mode="reverse_map", text=text, folded_key=""
        )
        self.assertTrue(result["matches"])
        self.assertEqual(result["rule_counts"], {"mark_stripped": 3})
        self.assertEqual(result["unchanged_count"], 0)

    def test_reverse_map_compatibility_clones_reach_symbol_map(self) -> None:
        for ch in ("\uFE31", "\uFE32", "\uFE58"):
            result = self.tool.execute(
                mode="reverse_map",
                text=ch,
                folded_key=TextFoldTool.fold_text(ch),
            )
            entry = result["evidence"][0]
            self.assertEqual(entry["rule"], "nfkd_decomposition")
            self.assertEqual(entry["folded_to"], "-")

    def test_reverse_map_fragments_sum_to_the_key(self) -> None:
        # The transparency invariant: concatenating the per-character
        # folded fragments and collapsing whitespace reproduces the
        # full fold exactly.
        for text in (
            "Café", "ＡＢＣ ﬁle…", "don’t  panic", E_DECOMPOSED,
            "你好，世界！", HANGUL_JAMO + " " + HANGUL_PRECOMPOSED,
        ):
            key = self.tool.execute(mode="fold", text=text)["folded"]
            result = self.tool.execute(
                mode="reverse_map", text=text, folded_key=key
            )
            changed = {
                entry["index"]: entry["folded_to"]
                for entry in result["evidence"]
            }
            fragments = [
                changed.get(i, TextFoldTool._fragment(ch))
                if i not in changed
                else changed[i]
                for i, ch in enumerate(text)
            ]
            joined = " ".join("".join(fragments).split())
            self.assertEqual(joined, key, msg=repr(text))


class TextFoldToolIdempotenceTest(unittest.TestCase):
    """Pipeline invariants — idempotence and the fragment-sum rule."""

    def setUp(self) -> None:
        self.tool = TextFoldTool()

    def test_fold_idempotent_over_seeded_texts(self) -> None:
        rng = random.Random(252)
        alphabet = list(
            "abcABCéÉèeﬁﬀＡＢ１２×÷’“”–—…ßςσΙİı"
            "汉字测试カフェｶﾌｪ가 \t\n-.,!哈"
        ) + ["́", "　"]
        for _ in range(300):
            text = "".join(
                rng.choice(alphabet) for _ in range(rng.randint(1, 25))
            )
            folded = self.tool.execute(mode="fold", text=text)["folded"]
            # The second pass goes through the pure classmethods —
            # execute() would rightly reject the empty key that an
            # all-punctuation text legitimately folds to.
            refolded = TextFoldTool.fold_text(folded)
            self.assertEqual(refolded, folded, msg=repr(text))
            key = self.tool.execute(mode="search_key", text=text)["search_key"]
            rekey = TextFoldTool.key_text(key)
            self.assertEqual(rekey, key, msg=repr(text))
            # The fold also matches the independent pipeline rebuild.
            self.assertEqual(folded, _independent_fold(text), msg=repr(text))

    def test_fold_idempotent_over_every_single_code_point(self) -> None:
        # Exhaustive single-code-point sweep of the whole Unicode
        # range (surrogates aside — they cannot appear in a str) —
        # the structural guarantee behind "stable key".
        for codepoint in range(0x110000):
            if 0xD800 <= codepoint <= 0xDFFF:
                continue
            char = chr(codepoint)
            folded = TextFoldTool.fold_text(char)
            self.assertEqual(
                TextFoldTool.fold_text(folded),
                folded,
                msg=f"U+{codepoint:04X}",
            )
            for out_char in folded:
                self.assertNotIn(
                    unicodedata.category(out_char), ("Mn", "Me")
                )

    def test_invariants_over_adversarial_alphabet(self) -> None:
        rng = random.Random(3993)
        alphabet = list(
            "abcABCéèﬁﬀＡ×÷’“”–—…ßςσΙİı汉カ가 \t\n-.,!"
        ) + [
            "\u0301", "\u0308", "\u035C", "\u00A0", "\u2000", "\u3000",
            "\u200D", "\u200C", "\u00AD", "\uFE31", "\uFE32",
            "\U0001F4BB",
        ]
        for _ in range(500):
            text = "".join(
                rng.choice(alphabet) for _ in range(rng.randint(1, 30))
            )
            folded = TextFoldTool.fold_text(text)
            self.assertEqual(TextFoldTool.fold_text(folded), folded)
            self.assertEqual(folded, _independent_fold(text))
            fragments = [TextFoldTool._fragment(ch) for ch in text]
            self.assertEqual(
                " ".join("".join(fragments).split()), folded
            )
            expected = _independent_rules(text)
            result = self.tool.execute(
                mode="reverse_map", text=text, folded_key=folded
            )
            listed = {
                entry["index"]: entry["rule"]
                for entry in result["evidence"]
            }
            self.assertEqual(listed, expected, msg=repr(text))


class TextFoldToolValidationTest(unittest.TestCase):
    """The error matrix — strict validation before any computation."""

    def setUp(self) -> None:
        self.tool = TextFoldTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_unknown_mode_rejected(self) -> None:
        self.assert_invalid(mode="unfold", text="x")
        self.assert_invalid(mode=None, text="x")
        self.assert_invalid(mode=123, text="x")

    def test_wrong_types_rejected(self) -> None:
        for bad in (None, True, False, 42, ["x"], {"a": 1}, b"bytes"):
            self.assert_invalid(mode="fold", text=bad)
            self.assert_invalid(mode="compare", text_1=bad, text_2="b")
            self.assert_invalid(mode="compare", text_1="a", text_2=bad)
            self.assert_invalid(mode="reverse_map", text="a", folded_key=bad)

    def test_empty_text_rejected(self) -> None:
        self.assert_invalid(mode="fold", text="")
        self.assert_invalid(mode="search_key", text="")
        self.assert_invalid(mode="compare", text_1="", text_2="b")
        self.assert_invalid(mode="compare", text_1="a", text_2="")

    def test_missing_required_parameters_rejected(self) -> None:
        self.assert_invalid(mode="fold")
        self.assert_invalid(mode="fold", text_1="not-the-right-parameter")
        self.assert_invalid(mode="search_key")
        self.assert_invalid(mode="compare", text_1="only-one")
        self.assert_invalid(mode="compare", text_2="only-one")
        self.assert_invalid(mode="compare")
        self.assert_invalid(mode="reverse_map", text="a")
        self.assert_invalid(mode="reverse_map", folded_key="a")

    def test_oversized_text_rejected(self) -> None:
        limit = self.tool.max_text_chars
        self.assert_invalid(mode="fold", text="x" * (limit + 1))
        self.assert_invalid(
            mode="reverse_map", text="x", folded_key="x" * (limit + 1)
        )
        # Exactly at the limit is accepted.
        result = self.tool.execute(mode="fold", text="x" * limit)
        self.assertEqual(len(result["folded"]), limit)

    def test_empty_folded_key_is_legitimate(self) -> None:
        # A whitespace-only text folds to the empty key, so the empty
        # folded_key must be accepted (and verified) — not rejected.
        # Tabs / newlines fire whitespace_collapsed; a plain space is
        # its own folded fragment and stays "unchanged" per character
        # (the collapse of the RUN is what produces the empty key).
        result = self.tool.execute(
            mode="reverse_map", text="\t\n ", folded_key=""
        )
        self.assertTrue(result["matches"])
        self.assertEqual(result["evidence_count"], 2)
        self.assertEqual(
            result["rule_counts"], {"whitespace_collapsed": 2}
        )

    def test_error_messages_are_prefixed(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="bogus", text="x")
        self.assertTrue(str(ctx.exception).startswith("text_fold_tool:"))


if __name__ == "__main__":
    unittest.main()
