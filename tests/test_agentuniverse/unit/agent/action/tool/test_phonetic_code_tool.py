#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_phonetic_code_tool.py

"""Offline unit tests for PhoneticCodeTool.

The tool is built purely on the standard library (re, typing) and never
touches the network, so this suite runs fully offline. Every assertion
is deterministic: the Soundex implementation is checked against the
classic published NARA test vectors (Robert, Rupert, Ashcraft,
Tymczak, Pfister, Honeyman, Washington, Lee, Gutierrez, VanDeusen),
the simplified NYSIIS implementation against vectors hand-derived from
the ruleset documented in the module docstring, the compare mode
against arithmetic computed from those codes, and the batch_group mode
against exact grouping output. Homophone pairs must share codes while
genuinely different names must not collide, and a full error matrix
covers every rejected input shape.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import PhoneticCodeTool
from agentuniverse.agent.action.tool.common_tool.phonetic_code_tool import (
    PhoneticCodeTool as DirectPhoneticCodeTool,
)

# --------------------------------------------------------------------- #
# Classic published American Soundex vectors (NARA / Wikipedia table).
# --------------------------------------------------------------------- #
CLASSIC_SOUNDEX = {
    "Robert": "R163",
    "Rupert": "R163",
    "Ashcraft": "A261",   # H-bridge: S and C share code 2 across H.
    "Ashcroft": "A261",   # Same H-bridge family as Ashcraft.
    "Tymczak": "T522",    # Vowel split: C-Z collapse, A splits, K re-coded.
    "Pfister": "P236",    # First/second letter share code 1 -> one digit.
    "Honeyman": "H555",
    "Washington": "W252",
    "Lee": "L000",        # No coded consonants after the first letter.
    "Gutierrez": "G362",  # Adjacent R-R collapses.
    "VanDeusen": "V532",
    # Extra canonical vectors exercising the same rules.
    "Schmidt": "S530",    # S-C adjacent same code at the word start.
    "Smith": "S530",      # Classic Schmidt/Smith homophone pair.
    "Smyth": "S530",
    "Allan": "A450",
    "Allen": "A450",
    "Johnson": "J525",
    "Jonson": "J525",
    "Albert": "A416",
    "Thompson": "T512",
    "Timczak": "T522",
    "Lea": "L000",
    "Kings": "K520",      # G-S adjacent same code collapse.
}

# --------------------------------------------------------------------- #
# Simplified NYSIIS vectors, hand-derived from the documented ruleset
# (prefix rules, character pass, suffix rules, collapsing) pinned in
# the PhoneticCodeTool module docstring.
# --------------------------------------------------------------------- #
DOCUMENTED_NYSIIS = {
    "Tymczak": "TYNCSAC",   # Y kept; M->N; Z->S; K->C.
    "Smith": "SNAT",        # M->N; I->A; trailing H dropped.
    "Smyth": "SNYT",        # Y kept as a consonant.
    "Ashcraft": "ASCRAFT",  # H dropped mid-word.
    "Ashcroft": "ASCRAFT",  # O->A makes both spellings identical.
    "Pfister": "FASTAR",    # PF->FF then collapse.
    "Robert": "RABART",     # O/E->A.
    "Rupert": "RAPART",     # U/E->A; B vs P differ from Robert.
    "Gutierrez": "GATARA",  # Vowels->A, RR collapse, trailing S dropped.
    "Johnson": "JANSAN",    # O->A, H dropped, O->A.
    "Jonson": "JANSAN",     # Same key as Johnson (homophone).
    "Washington": "WASANGTAN",
    "Honeyman": "HANAYNAN",
    "Lee": "LA",            # E->A.
    "Lea": "LA",
    "Allan": "ALAN",        # LL collapse, A, N.
    "Allen": "ALAN",        # E->A gives the same key as Allan.
    "Schmidt": "SNADT",     # SCH->SS, M->N, I->A, collapse SS->S.
    "Thompson": "TANPSAN",  # H dropped, O->A, M->N, O->A.
    "Albert": "ALBART",
    # Prefix rule coverage.
    "Mack": "MC",           # MAC->MCC, K->C, collapse.
    "McCarthy": "MCARTY",   # MAC->MCC, H dropped, collapse.
    "Knight": "NAGT",       # KN->NN, I->A, H dropped, collapse.
    "King": "NANG",         # K->N, I->A.
    # Suffix rule coverage.
    "Kay": "NY",            # Prefix K->N, then trailing AY -> Y.
    "Jonas": "JANA",        # Trailing AS -> A.
    "Lewis": "LAWA",        # Trailing S dropped.
}

# Homophones: same Soundex code, and (where the sounds align) the same
# simplified NYSIIS key too.
SOUNDEX_HOMOPHONES = [
    ("Robert", "Rupert"),
    ("Ashcraft", "Ashcroft"),
    ("Tymczak", "Timczak"),
    ("Smith", "Smyth"),
    ("Smith", "Schmidt"),
    ("Allan", "Allen"),
    ("Johnson", "Jonson"),
    ("Lee", "Lea"),
]
NYSIIS_HOMOPHONES = [
    ("Ashcraft", "Ashcroft"),
    ("Allan", "Allen"),
    ("Johnson", "Jonson"),
    ("Lee", "Lea"),
]
# Genuinely different names: neither code may collide.
DISTINCT_NAMES = [
    ("Robert", "Albert"),
    ("Smith", "Thompson"),
    ("Johnson", "Thompson"),
    ("Washington", "Honeyman"),
]


class PhoneticCodeToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib PhoneticCodeTool."""

    def setUp(self) -> None:
        self.tool = PhoneticCodeTool()

    # ------------------------------------------------------------------ #
    # soundex mode
    # ------------------------------------------------------------------ #

    def test_soundex_classic_vectors(self) -> None:
        for word, expected in CLASSIC_SOUNDEX.items():
            result = self.tool.execute(mode="soundex", text=word)
            self.assertEqual(
                result,
                {"mode": "soundex", "result": expected, "codes": [expected]},
                msg=f"soundex({word!r}) should be {expected}",
            )

    def test_soundex_is_case_insensitive(self) -> None:
        for spelling in ("robert", "ROBERT", "rObErT"):
            self.assertEqual(
                self.tool.execute(mode="soundex", text=spelling)["result"],
                "R163",
            )

    def test_soundex_multiple_words(self) -> None:
        result = self.tool.execute(mode="soundex", text="robert rupert smith")
        self.assertEqual(
            result,
            {
                "mode": "soundex",
                "result": ["R163", "R163", "S530"],
                "codes": ["R163", "R163", "S530"],
            },
        )

    def test_soundex_collapses_whitespace(self) -> None:
        result = self.tool.execute(mode="soundex", text="  robert \t rupert\n")
        self.assertEqual(result["codes"], ["R163", "R163"])

    # ------------------------------------------------------------------ #
    # nysiis mode
    # ------------------------------------------------------------------ #

    def test_nysiis_documented_vectors(self) -> None:
        for word, expected in DOCUMENTED_NYSIIS.items():
            result = self.tool.execute(mode="nysiis", text=word)
            self.assertEqual(
                result,
                {"mode": "nysiis", "result": expected, "codes": [expected]},
                msg=f"nysiis({word!r}) should be {expected} per the documented ruleset",
            )

    def test_nysiis_multiple_words(self) -> None:
        result = self.tool.execute(mode="nysiis", text="Smith Schmidt")
        self.assertEqual(result["result"], ["SNAT", "SNADT"])
        self.assertEqual(result["codes"], ["SNAT", "SNADT"])

    # ------------------------------------------------------------------ #
    # Homophones versus distinct names
    # ------------------------------------------------------------------ #

    def test_homophones_share_soundex(self) -> None:
        for left, right in SOUNDEX_HOMOPHONES:
            codes = self.tool.execute(
                mode="soundex", text=f"{left} {right}"
            )["codes"]
            self.assertEqual(
                codes[0], codes[1], msg=f"{left}/{right} should share a Soundex code"
            )

    def test_homophones_share_nysiis(self) -> None:
        for left, right in NYSIIS_HOMOPHONES:
            keys = self.tool.execute(mode="nysiis", text=f"{left} {right}")["codes"]
            self.assertEqual(
                keys[0], keys[1], msg=f"{left}/{right} should share a NYSIIS key"
            )

    def test_distinct_names_do_not_collide(self) -> None:
        for left, right in DISTINCT_NAMES:
            both = self.tool.execute(mode="soundex", text=f"{left} {right}")["codes"]
            self.assertNotEqual(both[0], both[1])
            keys = self.tool.execute(mode="nysiis", text=f"{left} {right}")["codes"]
            self.assertNotEqual(
                keys[0], keys[1], msg=f"{left}/{right} NYSIIS keys must differ"
            )

    # ------------------------------------------------------------------ #
    # compare mode
    # ------------------------------------------------------------------ #

    def test_compare_homophone_pair(self) -> None:
        result = self.tool.execute(mode="compare", word1="Robert", word2="Rupert")
        self.assertEqual(
            result,
            {
                "mode": "compare",
                "word1": "Robert",
                "word2": "Rupert",
                "soundex1": "R163",
                "soundex2": "R163",
                "nysiis1": "RABART",
                "nysiis2": "RAPART",
                "same_soundex": True,
                "same_nysiis": False,
                "soundex_distance": 0,
                "edit_distance": 0,
                "nysiis_edit_distance": 1,
            },
        )

    def test_compare_fully_different_pair(self) -> None:
        result = self.tool.execute(mode="compare", word1="Robert", word2="Albert")
        self.assertFalse(result["same_soundex"])
        self.assertFalse(result["same_nysiis"])
        self.assertEqual(result["soundex_distance"], 4)  # R163 vs A416: all differ
        # Levenshtein: sub R->A, insert '4', delete '3' beats 4 substitutions.
        self.assertEqual(result["edit_distance"], 3)
        # RABART vs ALBART: delete R, insert A/L head shift = 2.
        self.assertEqual(result["nysiis_edit_distance"], 2)

    def test_compare_identical_words(self) -> None:
        result = self.tool.execute(mode="compare", word1="Ashcraft", word2="Ashcroft")
        self.assertTrue(result["same_soundex"])
        self.assertTrue(result["same_nysiis"])
        self.assertEqual(result["soundex_distance"], 0)
        self.assertEqual(result["edit_distance"], 0)
        self.assertEqual(result["nysiis_edit_distance"], 0)

    def test_compare_edit_distance_arithmetic(self) -> None:
        # Smith/Schmidt: identical Soundex, NYSIIS keys SNAT vs SNADT.
        result = self.tool.execute(mode="compare", word1="Smith", word2="Schmidt")
        self.assertTrue(result["same_soundex"])
        self.assertEqual(result["soundex_distance"], 0)
        self.assertEqual(result["nysiis_edit_distance"], 1)
        # Levenshtein helper sanity checks.
        self.assertEqual(PhoneticCodeTool._levenshtein("ABC", "ABC"), 0)
        self.assertEqual(PhoneticCodeTool._levenshtein("", "ABC"), 3)
        self.assertEqual(PhoneticCodeTool._levenshtein("kitten", "sitting"), 3)

    # ------------------------------------------------------------------ #
    # batch_group mode
    # ------------------------------------------------------------------ #

    def test_batch_group_groups_by_soundex(self) -> None:
        result = self.tool.execute(
            mode="batch_group",
            words=["Robert", "Rupert", "Albert", "Smith", "Smyth", "Schmidt"],
        )
        self.assertEqual(
            result,
            {
                "mode": "batch_group",
                "groups": {
                    "R163": ["Robert", "Rupert"],
                    "A416": ["Albert"],
                    "S530": ["Smith", "Smyth", "Schmidt"],
                },
                "word_count": 6,
                "group_count": 3,
            },
        )

    def test_batch_group_preserves_input_order(self) -> None:
        result = self.tool.execute(
            mode="batch_group", words=["smyth", "Smith", "schmidt"]
        )
        self.assertEqual(result["groups"], {"S530": ["smyth", "Smith", "schmidt"]})
        self.assertEqual(result["word_count"], 3)
        self.assertEqual(result["group_count"], 1)

    def test_batch_group_single_word(self) -> None:
        result = self.tool.execute(mode="batch_group", words=["Lee"])
        self.assertEqual(
            result,
            {
                "mode": "batch_group",
                "groups": {"L000": ["Lee"]},
                "word_count": 1,
                "group_count": 1,
            },
        )

    # ------------------------------------------------------------------ #
    # Determinism and exports
    # ------------------------------------------------------------------ #

    def test_results_are_deterministic(self) -> None:
        for mode_args in (
            {"mode": "soundex", "text": "Washington Honeyman"},
            {"mode": "nysiis", "text": "Washington Honeyman"},
            {"mode": "compare", "word1": "Allan", "word2": "Allen"},
            {"mode": "batch_group", "words": ["Johnson", "Jonson", "Kings"]},
        ):
            first = self.tool.execute(**mode_args)
            for _ in range(3):
                self.assertEqual(self.tool.execute(**mode_args), first)

    def test_package_and_direct_exports_are_the_same_class(self) -> None:
        self.assertIs(PhoneticCodeTool, DirectPhoneticCodeTool)

    def test_default_tool_metadata(self) -> None:
        self.assertEqual(self.tool.name, "phonetic_code_tool")
        self.assertIn("Soundex", self.tool.description)
        self.assertIn("NYSIIS", self.tool.description)

    def test_yaml_configuration_is_consistent(self) -> None:
        from pathlib import Path

        import yaml

        # tests/test_agentuniverse/unit/agent/action/tool/ -> repo root.
        yaml_path = (
            Path(__file__).resolve().parents[6]
            / "agentuniverse"
            / "agent"
            / "action"
            / "tool"
            / "common_tool"
            / "phonetic_code_tool.yaml"
        )
        with open(yaml_path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        self.assertEqual(config["name"], "phonetic_code_tool")
        self.assertEqual(config["metadata"]["class"], "PhoneticCodeTool")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool.phonetic_code_tool",
        )
        self.assertEqual(
            sorted(config["args_model_schema"]["properties"]),
            ["mode", "text", "word1", "word2", "words"],
        )
        self.assertEqual(config["args_model_schema"]["required"], ["mode"])

    # ------------------------------------------------------------------ #
    # Error matrix — every malformed input raises ValueError
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_unknown_mode_raises(self) -> None:
        self.assert_invalid(mode="metaphone", text="Robert")
        self.assert_invalid(mode=None, text="Robert")

    def test_soundex_rejects_non_alphabetic_text(self) -> None:
        self.assert_invalid(mode="soundex")                       # missing text
        self.assert_invalid(mode="soundex", text=None)
        self.assert_invalid(mode="soundex", text="")
        self.assert_invalid(mode="soundex", text="   ")
        self.assert_invalid(mode="soundex", text=123)
        self.assert_invalid(mode="soundex", text=True)
        self.assert_invalid(mode="soundex", text=["Robert"])
        self.assert_invalid(mode="soundex", text="Robert 3rd")     # digit token
        self.assert_invalid(mode="soundex", text="O'Brien")        # apostrophe
        self.assert_invalid(mode="soundex", text="Smith-Jones")    # hyphen
        self.assert_invalid(mode="soundex", text="héllo")          # non-ASCII
        self.assert_invalid(mode="soundex", text="Robert, Rupert") # punctuation
        self.assert_invalid(mode="soundex", text="a" * 101)        # word too long
        self.assert_invalid(mode="soundex", text=" ".join(["a"] * 101))

    def test_nysiis_rejects_non_alphabetic_text(self) -> None:
        self.assert_invalid(mode="nysiis", text="Tymczak7")
        self.assert_invalid(mode="nysiis", text="")
        self.assert_invalid(mode="nysiis", text=None)
        self.assert_invalid(mode="nysiis", text=3.14)

    def test_compare_rejects_malformed_words(self) -> None:
        self.assert_invalid(mode="compare", word1="Robert")             # missing word2
        self.assert_invalid(mode="compare", word2="Robert")             # missing word1
        self.assert_invalid(mode="compare", word1="John Smith", word2="Jonson")
        self.assert_invalid(mode="compare", word1="", word2="Jonson")
        self.assert_invalid(mode="compare", word1="J0hn", word2="Jonson")
        self.assert_invalid(mode="compare", word1=True, word2="Jonson")
        self.assert_invalid(mode="compare", word1=["Robert"], word2="Rupert")

    def test_batch_group_rejects_malformed_lists(self) -> None:
        self.assert_invalid(mode="batch_group")                        # missing words
        self.assert_invalid(mode="batch_group", words=None)
        self.assert_invalid(mode="batch_group", words="Robert")        # not a list
        self.assert_invalid(mode="batch_group", words=[])
        self.assert_invalid(mode="batch_group", words=[123])
        self.assert_invalid(mode="batch_group", words=["Robert", None])
        self.assert_invalid(mode="batch_group", words=["Robert", "O'Brien"])
        self.assert_invalid(mode="batch_group", words=["héllo"])
        self.assert_invalid(mode="batch_group", words=["a" * 101])
        self.assert_invalid(mode="batch_group", words=["a"] * 1001)

    def test_error_messages_name_the_tool(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="soundex", text="O'Brien")
        self.assertIn("phonetic_code_tool", str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="nysiis")
        self.assertIn("phonetic_code_tool", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
