#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_morse_code_tool.py

"""Offline unit tests for MorseCodeTool.

The tool is built purely on the standard library (no imports beyond
pydantic for the Tool model) and never touches the network, so this
suite runs fully offline. Every assertion is deterministic: encode and
decode results are checked against literal ITU-R M.1677-1 ground
truths, the table mode against the full 54-entry mapping, and error
paths against fixed ValueError / structured-error conditions.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import MorseCodeTool
from agentuniverse.agent.action.tool.common_tool.morse_code_tool import (
    MorseCodeTool as DirectMorseCodeTool,
)

# --------------------------------------------------------------------- #
# Ground truths — ITU-R M.1677-1 International Morse code
# --------------------------------------------------------------------- #
LETTERS = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".",
    "F": "..-.", "G": "--.", "H": "....", "I": "..", "J": ".---",
    "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---",
    "P": ".--.", "Q": "--.-", "R": ".-.", "S": "...", "T": "-",
    "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--",
    "Z": "--..",
}
DIGITS = {
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
}
PUNCTUATION = {
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "'": ".----.",
    "!": "-.-.--", "/": "-..-.", "(": "-.--.", ")": "-.--.-",
    "&": ".-...", ":": "---...", ";": "-.-.-.", "=": "-...-",
    "+": ".-.-.", "-": "-....-", "_": "..--.-", '"': ".-..-.",
    "$": "...-..-", "@": ".--.-.",
}
FULL_TABLE = {**LETTERS, **DIGITS, **PUNCTUATION}

SOS_MORSE = "... --- ..."
HELLO_WORLD_MORSE = ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."


class MorseCodeToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib MorseCodeTool."""

    def setUp(self) -> None:
        self.tool = MorseCodeTool()

    # ------------------------------------------------------------------ #
    # encode mode — full alphabet and digit ground truths
    # ------------------------------------------------------------------ #

    def test_encode_full_alphabet_ground_truth(self) -> None:
        for char, code in LETTERS.items():
            with self.subTest(char=char):
                result = self.tool.execute(mode="encode", text=char)
                self.assertEqual(
                    result,
                    {
                        "mode": "encode",
                        "result": code,
                        "unknown_chars": [],
                        "skipped_count": 0,
                    },
                )

    def test_encode_full_digits_ground_truth(self) -> None:
        for char, code in DIGITS.items():
            with self.subTest(char=char):
                self.assertEqual(
                    self.tool.execute(mode="encode", text=char)["result"],
                    code,
                )

    def test_encode_punctuation_set_ground_truth(self) -> None:
        for char, code in PUNCTUATION.items():
            with self.subTest(char=char):
                self.assertEqual(
                    self.tool.execute(mode="encode", text=char)["result"],
                    code,
                )

    def test_encode_sos_known_vector(self) -> None:
        result = self.tool.execute(mode="encode", text="SOS")
        self.assertEqual(result["result"], SOS_MORSE)
        self.assertEqual(result["skipped_count"], 0)

    def test_encode_hello_world_with_word_separator(self) -> None:
        result = self.tool.execute(mode="encode", text="HELLO WORLD")
        self.assertEqual(result["result"], HELLO_WORLD_MORSE)
        self.assertIn(" / ", result["result"])

    def test_encode_multiple_words(self) -> None:
        result = self.tool.execute(mode="encode", text="MORSE CODE TOOL")
        self.assertEqual(
            result["result"],
            "-- --- .-. ... . / -.-. --- -.. . / - --- --- .-..",
        )

    def test_encode_letters_single_space_separation(self) -> None:
        result = self.tool.execute(mode="encode", text="AB")
        self.assertEqual(result["result"], ".- -...")

    # ------------------------------------------------------------------ #
    # encode mode — case-insensitivity and whitespace handling
    # ------------------------------------------------------------------ #

    def test_encode_mixed_case_insensitive(self) -> None:
        expected = self.tool.execute(mode="encode", text="HELLO")["result"]
        for text in ("hello", "HeLLo", "hELLO"):
            with self.subTest(text=text):
                self.assertEqual(
                    self.tool.execute(mode="encode", text=text)["result"],
                    expected,
                )

    def test_encode_whitespace_runs_collapse_to_word_separator(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="encode", text="  HELLO   WORLD  ")["result"],
            self.tool.execute(mode="encode", text="HELLO WORLD")["result"],
        )

    # ------------------------------------------------------------------ #
    # encode mode — unknown characters are flagged per char and skipped
    # ------------------------------------------------------------------ #

    def test_encode_unknown_chars_flagged_with_cjk(self) -> None:
        result = self.tool.execute(mode="encode", text="HI 世界")
        self.assertEqual(result["mode"], "encode")
        self.assertEqual(result["result"], ".... ..")
        self.assertEqual(result["unknown_chars"], ["世", "界"])
        self.assertEqual(result["skipped_count"], 2)

    def test_encode_unknown_chars_counted_per_occurrence(self) -> None:
        result = self.tool.execute(mode="encode", text="AéAé")
        self.assertEqual(result["result"], ".- .-")
        # Unknown characters are flagged after case folding.
        self.assertEqual(result["unknown_chars"], ["É", "É"])
        self.assertEqual(result["skipped_count"], 2)

    def test_encode_all_unknown_chars(self) -> None:
        result = self.tool.execute(mode="encode", text="日本語")
        self.assertEqual(result["result"], "")
        self.assertEqual(result["unknown_chars"], ["日", "本", "語"])
        self.assertEqual(result["skipped_count"], 3)

    def test_encode_unknown_chars_list_capped_at_100(self) -> None:
        result = self.tool.execute(mode="encode", text="A" + "世" * 150)
        self.assertEqual(result["skipped_count"], 150)
        self.assertEqual(len(result["unknown_chars"]), 100)
        self.assertTrue(all(char == "世" for char in result["unknown_chars"]))

    # ------------------------------------------------------------------ #
    # decode mode
    # ------------------------------------------------------------------ #

    def test_decode_sos_known_vector(self) -> None:
        result = self.tool.execute(mode="decode", text=SOS_MORSE)
        self.assertEqual(result, {"mode": "decode", "result": "SOS"})

    def test_decode_hello_world_with_word_separator(self) -> None:
        result = self.tool.execute(
            mode="decode", text=HELLO_WORLD_MORSE
        )
        self.assertEqual(result["result"], "HELLO WORLD")

    def test_decode_slash_separator_variants(self) -> None:
        # Canonical form: single spaces between letters, " / " between
        # words; any whitespace run around the "/" token works.
        self.assertEqual(
            self.tool.execute(mode="decode", text="... --- ...")["result"],
            "SOS",
        )
        self.assertEqual(
            self.tool.execute(mode="decode", text=".- / -...")["result"],
            "A B",
        )
        self.assertEqual(
            self.tool.execute(mode="decode", text=".-  /  -...")["result"],
            "A B",
        )

    def test_decode_every_slash_starts_a_new_word(self) -> None:
        # Each "/" token is a word break, so "... / --- / ..." is three
        # one-letter words, not the single word "SOS".
        self.assertEqual(
            self.tool.execute(mode="decode", text="... / --- / ...")["result"],
            "S O S",
        )

    def test_decode_glued_separator_is_one_invalid_token(self) -> None:
        # Tokens split on space: without spaces around the '/', the
        # whole string is a single (invalid) token.
        result = self.tool.execute(mode="decode", text=".../---/...")
        self.assertEqual(result["error"]["type"], "invalid_morse_token")
        self.assertIn("'.../---/...'", result["error"]["message"])

    def test_decode_slash_character_code_is_not_a_separator(self) -> None:
        # "-..-." is the Morse code for the '/' character itself.
        result = self.tool.execute(mode="decode", text="-..-.")
        self.assertEqual(result["result"], "/")

    def test_decode_prosign_handled_as_normal_letters(self) -> None:
        # SOS as three normal letters decodes fine; the concatenated
        # prosign form is not a table entry and is rejected below.
        self.assertEqual(
            self.tool.execute(mode="decode", text="... --- ...")["result"],
            "SOS",
        )

    def test_decode_leading_trailing_and_double_separators(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="decode", text="/ ... --- ... /")["result"],
            "SOS",
        )
        self.assertEqual(
            self.tool.execute(
                mode="decode", text="... --- ... / / .... .."
            )["result"],
            "SOS HI",
        )

    def test_decode_punctuation_round_trip(self) -> None:
        text = "HELLO, WORLD!"
        encoded = self.tool.execute(mode="encode", text=text)["result"]
        self.assertEqual(
            self.tool.execute(mode="decode", text=encoded)["result"], text
        )

    def test_decode_full_alphabet_ground_truth(self) -> None:
        for char, code in FULL_TABLE.items():
            with self.subTest(char=char):
                self.assertEqual(
                    self.tool.execute(mode="decode", text=code)["result"],
                    char,
                )

    def test_round_trip_uppercases_and_normalizes_spacing(self) -> None:
        text = "the quick brown fox 1234!?&"
        encoded = self.tool.execute(mode="encode", text=text)["result"]
        self.assertEqual(
            self.tool.execute(mode="decode", text=encoded)["result"],
            "THE QUICK BROWN FOX 1234!?&",
        )

    # ------------------------------------------------------------------ #
    # decode mode — invalid tokens rejected with the token listed
    # ------------------------------------------------------------------ #

    def test_decode_invalid_token_error_lists_token(self) -> None:
        result = self.tool.execute(
            mode="decode", text=".... .-.. ..zz."
        )
        self.assertEqual(result["mode"], "decode")
        self.assertEqual(result["error"]["type"], "invalid_morse_token")
        self.assertIn("'..zz.'", result["error"]["message"])

    def test_decode_concatenated_prosign_rejected(self) -> None:
        result = self.tool.execute(mode="decode", text="...---...")
        self.assertEqual(result["error"]["type"], "invalid_morse_token")
        self.assertIn("'...---...'", result["error"]["message"])
        self.assertIn("... --- ...", result["error"]["message"])

    def test_decode_non_morse_token_rejected(self) -> None:
        result = self.tool.execute(mode="decode", text="SOS")
        self.assertEqual(result["error"]["type"], "invalid_morse_token")
        self.assertIn("'SOS'", result["error"]["message"])

    def test_decode_multiple_invalid_tokens_listed_and_capped(self) -> None:
        result = self.tool.execute(
            mode="decode", text="z1 z2 z3 z4 z5 z6 z7"
        )
        self.assertEqual(result["error"]["type"], "invalid_morse_token")
        for token in ("z1", "z2", "z3", "z4", "z5"):
            self.assertIn(repr(token), result["error"]["message"])
        self.assertIn("+2 more", result["error"]["message"])
        self.assertNotIn("z7", result["error"]["message"].replace("+2 more", ""))

    def test_decode_invalid_dashes_and_dots_sequence(self) -> None:
        for bad in ("------", "....... .......", "-..-.-", ".----..-"):
            with self.subTest(bad=bad):
                result = self.tool.execute(mode="decode", text=bad)
                self.assertEqual(result["error"]["type"], "invalid_morse_token")

    # ------------------------------------------------------------------ #
    # table mode
    # ------------------------------------------------------------------ #

    def test_table_returns_full_mapping(self) -> None:
        result = self.tool.execute(mode="table")
        self.assertEqual(result["mode"], "table")
        self.assertEqual(result["result"], FULL_TABLE)
        self.assertEqual(len(result["result"]), 54)

    def test_table_is_a_copy(self) -> None:
        first = self.tool.execute(mode="table")["result"]
        first["A"] = "mutated"
        second = self.tool.execute(mode="table")["result"]
        self.assertEqual(second["A"], ".-")

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        for bad in ("morse", "encode/decode", None, 123, "ENCODE"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode=bad, text="SOS")

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"SOS", ["SOS"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="encode", text=bad)
                self.assert_invalid(mode="decode", text=bad)

    def test_empty_text_rejected(self) -> None:
        self.assert_invalid(mode="encode", text="")
        self.assert_invalid(mode="decode", text="")

    def test_whitespace_only_text_rejected(self) -> None:
        for bad in (" ", "   ", "\t", " \n "):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="encode", text=bad)
                self.assert_invalid(mode="decode", text=bad)

    def test_text_length_limit(self) -> None:
        oversized = "A" * 100_001
        self.assert_invalid(mode="encode", text=oversized)
        self.assert_invalid(mode="decode", text=oversized)
        ok = self.tool.execute(mode="encode", text="A" * 100_000)
        self.assertEqual(ok["skipped_count"], 0)
        self.assertTrue(ok["result"].startswith(".- "))

    def test_table_mode_ignores_text(self) -> None:
        result = self.tool.execute(mode="table", text="anything")
        self.assertEqual(len(result["result"]), 54)

    # ------------------------------------------------------------------ #
    # Determinism and packaging / registration
    # ------------------------------------------------------------------ #

    def test_encode_deterministic_across_calls(self) -> None:
        first = self.tool.execute(mode="encode", text="HELLO WORLD")
        second = self.tool.execute(mode="encode", text="HELLO WORLD")
        self.assertEqual(first, second)

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectMorseCodeTool, MorseCodeTool)
        self.assertEqual(self.tool.name, "morse_code_tool")
        self.assertIn("encode", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("MorseCodeTool", __all__)


if __name__ == "__main__":
    unittest.main()
