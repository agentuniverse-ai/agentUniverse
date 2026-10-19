#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_phonetic_alphabet_tool.py

"""Offline unit tests for PhoneticAlphabetTool.

The tool is built purely on the standard library (it is a plain
mapping table) and never touches the network, so this suite runs
fully offline. Every assertion is deterministic: the spell results
are checked against literal NATO / ICAO ground truths written out in
full (independent of the tool's own table), the read results against
fixed case-insensitive mappings, and the round trips against the
contract that read(spell(text)) reproduces the text exactly except
that letters are canonicalised to uppercase.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import PhoneticAlphabetTool
from agentuniverse.agent.action.tool.common_tool.phonetic_alphabet_tool import (
    PhoneticAlphabetTool as DirectPhoneticAlphabetTool,
)

# --------------------------------------------------------------------- #
# NATO / ICAO ground truths (literal expected values, not derived from
# the tool's tables). Official ICAO spellings: Alfa, Juliett, X-ray,
# and the digit word Niner.
# --------------------------------------------------------------------- #
LETTER_WORDS = (
    "Alfa Bravo Charlie Delta Echo Foxtrot Golf Hotel India Juliett "
    "Kilo Lima Mike November Oscar Papa Quebec Romeo Sierra Tango "
    "Uniform Victor Whiskey X-ray Yankee Zulu"
)
LETTER_TABLE = {
    "A": "Alfa", "B": "Bravo", "C": "Charlie", "D": "Delta",
    "E": "Echo", "F": "Foxtrot", "G": "Golf", "H": "Hotel",
    "I": "India", "J": "Juliett", "K": "Kilo", "L": "Lima",
    "M": "Mike", "N": "November", "O": "Oscar", "P": "Papa",
    "Q": "Quebec", "R": "Romeo", "S": "Sierra", "T": "Tango",
    "U": "Uniform", "V": "Victor", "W": "Whiskey", "X": "X-ray",
    "Y": "Yankee", "Z": "Zulu",
}
DIGIT_WORDS = "Zero One Two Three Four Five Six Seven Eight Niner"
DIGIT_TABLE = {
    "0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four",
    "5": "Five", "6": "Six", "7": "Seven", "8": "Eight", "9": "Niner",
}


class PhoneticAlphabetToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib PhoneticAlphabetTool."""

    def setUp(self) -> None:
        self.tool = PhoneticAlphabetTool()

    # ------------------------------------------------------------------ #
    # spell mode — full A-Z / 0-9 ground truths
    # ------------------------------------------------------------------ #

    def test_spell_uppercase_alphabet_ground_truth(self) -> None:
        result = self.tool.execute(mode="spell", text="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.assertEqual(result["mode"], "spell")
        self.assertEqual(result["result"], LETTER_WORDS)
        self.assertEqual(result["space_marker"], "[space]")
        self.assertEqual(result["flagged"], [])

    def test_spell_lowercase_alphabet_ground_truth(self) -> None:
        result = self.tool.execute(mode="spell", text="abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(result["result"], LETTER_WORDS)

    def test_spell_each_letter_individually(self) -> None:
        for letter, word in LETTER_TABLE.items():
            with self.subTest(letter=letter):
                self.assertEqual(
                    self.tool.execute(mode="spell", text=letter)["result"], word
                )
                self.assertEqual(
                    self.tool.execute(mode="spell", text=letter.lower())["result"],
                    word,
                )

    def test_spell_official_icao_spellings(self) -> None:
        # Alfa with f, Juliett with double t, X-ray hyphenated.
        self.assertEqual(LETTER_TABLE["A"], "Alfa")
        self.assertNotEqual(LETTER_TABLE["A"], "Alpha")
        self.assertEqual(LETTER_TABLE["J"], "Juliett")
        self.assertNotEqual(LETTER_TABLE["J"], "Juliet")
        self.assertEqual(LETTER_TABLE["X"], "X-ray")
        # Niner, not Nine.
        self.assertEqual(DIGIT_TABLE["9"], "Niner")

    def test_spell_digits_ground_truth(self) -> None:
        result = self.tool.execute(mode="spell", text="0123456789")
        self.assertEqual(result["result"], DIGIT_WORDS)

    def test_spell_each_digit_individually(self) -> None:
        for digit, word in DIGIT_TABLE.items():
            with self.subTest(digit=digit):
                self.assertEqual(
                    self.tool.execute(mode="spell", text=digit)["result"], word
                )

    def test_spell_hello_world_ground_truth(self) -> None:
        result = self.tool.execute(mode="spell", text="Hello World")
        self.assertEqual(
            result["result"],
            "Hotel Echo Lima Lima Oscar [space] "
            "Whiskey Oscar Romeo Lima Delta",
        )

    # ------------------------------------------------------------------ #
    # spell mode — case preservation in entries
    # ------------------------------------------------------------------ #

    def test_spell_entries_preserve_original_case(self) -> None:
        result = self.tool.execute(mode="spell", text="aBc")
        self.assertEqual(
            result["entries"],
            [
                {"char": "a", "word": "Alfa"},
                {"char": "B", "word": "Bravo"},
                {"char": "c", "word": "Charlie"},
            ],
        )

    def test_spell_entries_digit_and_space(self) -> None:
        result = self.tool.execute(mode="spell", text="A 7")
        self.assertEqual(
            result["entries"],
            [
                {"char": "A", "word": "Alfa"},
                {"char": " ", "word": "[space]"},
                {"char": "7", "word": "Seven"},
            ],
        )

    # ------------------------------------------------------------------ #
    # spell mode — space marker option
    # ------------------------------------------------------------------ #

    def test_spell_default_space_marker(self) -> None:
        result = self.tool.execute(mode="spell", text="A B")
        self.assertEqual(result["result"], "Alfa [space] Bravo")
        self.assertEqual(result["space_marker"], "[space]")

    def test_spell_custom_space_marker(self) -> None:
        for marker in ("·", "-", "...", "[pause]"):
            with self.subTest(marker=marker):
                result = self.tool.execute(
                    mode="spell", text="A B", space_marker=marker
                )
                self.assertEqual(result["result"], f"Alfa {marker} Bravo")
                self.assertEqual(result["space_marker"], marker)

    def test_spell_leading_trailing_and_repeated_spaces(self) -> None:
        result = self.tool.execute(mode="spell", text=" A  B ")
        self.assertEqual(
            result["result"], "[space] Alfa [space] [space] Bravo [space]"
        )

    # ------------------------------------------------------------------ #
    # spell mode — punctuation and unknown characters flagged
    # ------------------------------------------------------------------ #

    def test_spell_punctuation_passed_through_flagged(self) -> None:
        result = self.tool.execute(mode="spell", text="S.O.S!")
        self.assertEqual(result["result"], "Sierra . Oscar . Sierra !")
        self.assertEqual(
            result["flagged"],
            [
                {"char": ".", "index": 1},
                {"char": ".", "index": 3},
                {"char": "!", "index": 5},
            ],
        )

    def test_spell_unknown_non_ascii_passed_through_flagged(self) -> None:
        result = self.tool.execute(mode="spell", text="AéB")
        self.assertEqual(result["result"], "Alfa é Bravo")
        self.assertEqual(result["flagged"], [{"char": "é", "index": 1}])

    def test_spell_non_ascii_digit_word_not_used(self) -> None:
        # Arabic-Indic digit ٣ is a digit but not an ASCII 0-9 digit,
        # so it must be flagged, not mapped.
        result = self.tool.execute(mode="spell", text="٣")
        self.assertEqual(result["result"], "٣")
        self.assertEqual(result["flagged"], [{"char": "٣", "index": 0}])

    def test_spell_flagged_entry_pairs_still_listed(self) -> None:
        result = self.tool.execute(mode="spell", text="A-B")
        self.assertEqual(
            result["entries"],
            [
                {"char": "A", "word": "Alfa"},
                {"char": "-", "word": "-"},
                {"char": "B", "word": "Bravo"},
            ],
        )
        self.assertEqual(result["flagged"], [{"char": "-", "index": 1}])

    # ------------------------------------------------------------------ #
    # read mode
    # ------------------------------------------------------------------ #

    def test_read_known_vector(self) -> None:
        result = self.tool.execute(
            mode="read", text="Hotel Echo Lima Lima Oscar"
        )
        self.assertEqual(result["mode"], "read")
        self.assertEqual(result["result"], "HELLO")

    def test_read_case_insensitive(self) -> None:
        result = self.tool.execute(mode="read", text="hotel ECHO JuliETT x-ray")
        self.assertEqual(result["result"], "HEJX")

    def test_read_all_caps_and_mixed_words(self) -> None:
        result = self.tool.execute(mode="read", text="ALFA BRAVO charlie DELTA")
        self.assertEqual(result["result"], "ABCD")

    def test_read_digits_ground_truth(self) -> None:
        result = self.tool.execute(mode="read", text=DIGIT_WORDS)
        self.assertEqual(result["result"], "0123456789")

    def test_read_letters_ground_truth(self) -> None:
        result = self.tool.execute(mode="read", text=LETTER_WORDS)
        self.assertEqual(result["result"], "ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def test_read_each_word_case_insensitive(self) -> None:
        for letter, word in LETTER_TABLE.items():
            with self.subTest(word=word):
                self.assertEqual(
                    self.tool.execute(mode="read", text=word.lower())["result"],
                    letter,
                )
        for digit, word in DIGIT_TABLE.items():
            with self.subTest(word=word):
                self.assertEqual(
                    self.tool.execute(mode="read", text=word.upper())["result"],
                    digit,
                )

    def test_read_default_space_marker(self) -> None:
        result = self.tool.execute(mode="read", text="Alfa [space] Bravo")
        self.assertEqual(result["result"], "A B")
        self.assertEqual(result["space_marker"], "[space]")

    def test_read_custom_space_marker(self) -> None:
        result = self.tool.execute(
            mode="read", text="Alfa · Bravo", space_marker="·"
        )
        self.assertEqual(result["result"], "A B")

    def test_read_marker_matched_case_insensitively(self) -> None:
        result = self.tool.execute(
            mode="read", text="Alfa [SPACE] Bravo"
        )
        self.assertEqual(result["result"], "A B")

    def test_read_punctuation_pass_through(self) -> None:
        result = self.tool.execute(mode="read", text="Hotel . Echo - Oscar")
        self.assertEqual(result["result"], "H.E-O")

    def test_read_unknown_word_rejected_with_word_and_position(self) -> None:
        result = self.tool.execute(mode="read", text="Hotel blah Echo")
        self.assertEqual(result["mode"], "read")
        self.assertEqual(result["error"]["type"], "unknown_word")
        self.assertIn("blah", result["error"]["message"])
        self.assertIn("position 1", result["error"]["message"])
        self.assertIn("word 2 of 3", result["error"]["message"])

    def test_read_unknown_word_at_start(self) -> None:
        result = self.tool.execute(mode="read", text="nope Alfa")
        self.assertEqual(result["error"]["type"], "unknown_word")
        self.assertIn("nope", result["error"]["message"])
        self.assertIn("position 0", result["error"]["message"])

    def test_read_rejects_single_letter_token(self) -> None:
        # A single letter is not a phonetic word; passing one through
        # would be ambiguous with flagged punctuation.
        result = self.tool.execute(mode="read", text="A Hotel")
        self.assertEqual(result["error"]["type"], "unknown_word")
        self.assertIn("'A'", result["error"]["message"])

    def test_read_rejects_single_digit_token(self) -> None:
        result = self.tool.execute(mode="read", text="Hotel 5")
        self.assertEqual(result["error"]["type"], "unknown_word")
        self.assertIn("'5'", result["error"]["message"])

    def test_read_rejects_multi_word_garbage(self) -> None:
        result = self.tool.execute(mode="read", text="Alpha Bravo")
        # "Alpha" is the wrong spelling of "Alfa" and must be rejected.
        self.assertEqual(result["error"]["type"], "unknown_word")
        self.assertIn("Alpha", result["error"]["message"])

    def test_read_rejects_plain_digits_word_string(self) -> None:
        result = self.tool.execute(mode="read", text="Nine Niner")
        # "Nine" is not the ICAO digit word; only "Niner" is.
        self.assertEqual(result["error"]["type"], "unknown_word")
        self.assertIn("Nine", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # Round trips (letters canonicalised to uppercase)
    # ------------------------------------------------------------------ #

    def test_mixed_case_round_trip_spell_read(self) -> None:
        for text in (
            "Hello World",
            "MiXeD CaSe 42",
            "AB CD 07",
            "agentUniverse",
            "Zulu 9 Niner 0",
        ):
            with self.subTest(text=text):
                spelled = self.tool.execute(mode="spell", text=text)
                read_back = self.tool.execute(mode="read", text=spelled["result"])
                self.assertEqual(read_back["result"], text.upper())

    def test_round_trip_with_punctuation(self) -> None:
        spelled = self.tool.execute(mode="spell", text="H.i 42!")
        read_back = self.tool.execute(mode="read", text=spelled["result"])
        self.assertEqual(read_back["result"], "H.I 42!")

    def test_round_trip_custom_space_marker(self) -> None:
        for marker in ("·", "-", "[pause]"):
            with self.subTest(marker=marker):
                spelled = self.tool.execute(
                    mode="spell", text="A B C", space_marker=marker
                )
                read_back = self.tool.execute(
                    mode="read", text=spelled["result"], space_marker=marker
                )
                self.assertEqual(read_back["result"], "A B C")

    def test_spell_is_deterministic(self) -> None:
        first = self.tool.execute(mode="spell", text="Round Trip 7")
        second = self.tool.execute(mode="spell", text="Round Trip 7")
        self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # list mode
    # ------------------------------------------------------------------ #

    def test_list_returns_full_tables(self) -> None:
        result = self.tool.execute(mode="list")
        self.assertEqual(
            result,
            {
                "mode": "list",
                "alphabet": "nato",
                "letters": LETTER_TABLE,
                "digits": DIGIT_TABLE,
                "default_space_marker": "[space]",
            },
        )

    def test_list_table_sizes_and_order(self) -> None:
        result = self.tool.execute(mode="list")
        self.assertEqual(len(result["letters"]), 26)
        self.assertEqual(len(result["digits"]), 10)
        self.assertEqual(list(result["letters"]), list(LETTER_TABLE))
        self.assertEqual(list(result["digits"]), list(DIGIT_TABLE))

    def test_list_ignores_text(self) -> None:
        result = self.tool.execute(mode="list", text="ignored")
        self.assertEqual(result["mode"], "list")
        self.assertEqual(result["letters"], LETTER_TABLE)

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="spellit", text="A")
        self.assert_invalid(mode=None, text="A")
        self.assert_invalid(mode=123, text="A")
        self.assert_invalid(mode="SPELLED", text="A")

    def test_missing_or_invalid_text(self) -> None:
        self.assert_invalid(mode="spell")
        self.assert_invalid(mode="read")
        self.assert_invalid(mode="spell", text="")
        self.assert_invalid(mode="read", text="")
        for bad in (None, 123, True, b"AB", ["AB"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="spell", text=bad)
                self.assert_invalid(mode="read", text=bad)

    def test_rejects_control_and_non_space_whitespace(self) -> None:
        for bad in ("A\tB", "A\nB", "A\rB", "A\x00B", "A\x7fB", "A\xa0B", "A\u2009B"):
            with self.subTest(bad=repr(bad)):
                self.assert_invalid(mode="spell", text=bad)
                self.assert_invalid(mode="read", text=bad)

    def test_text_length_limit(self) -> None:
        oversized = "A" * 10_001
        self.assert_invalid(mode="spell", text=oversized)
        self.assert_invalid(mode="read", text=oversized)
        ok = self.tool.execute(mode="spell", text="A" * 10_000)
        self.assertEqual(len(ok["entries"]), 10_000)

    def test_invalid_space_marker(self) -> None:
        for bad in ("", 123, True, "a b", " ", "zulu", "ZULU", "Niner", "x-ray", "x", "9", "· ·"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="spell", text="A B", space_marker=bad)
        # A marker longer than 16 characters is rejected.
        self.assert_invalid(mode="spell", text="A B", space_marker="m" * 17)
        # A marker that collides with a word is also rejected in read mode.
        self.assert_invalid(mode="read", text="Alfa Bravo", space_marker="alfa")

    def test_valid_space_markers_accepted(self) -> None:
        for good in (None, "[space]", "·", "-", "...", "[pause]", "m" * 16, "[SPACE]"):
            with self.subTest(good=good):
                result = self.tool.execute(
                    mode="spell", text="A B", space_marker=good
                )
                marker = "[space]" if good is None else good
                self.assertEqual(result["space_marker"], marker)
                self.assertEqual(result["result"], f"Alfa {marker} Bravo")

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectPhoneticAlphabetTool, PhoneticAlphabetTool)
        self.assertEqual(self.tool.name, "phonetic_alphabet_tool")
        self.assertIn("spell", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("PhoneticAlphabetTool", __all__)


if __name__ == "__main__":
    unittest.main()
