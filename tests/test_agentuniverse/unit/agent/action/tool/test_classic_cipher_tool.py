#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_classic_cipher_tool.py

"""Offline unit tests for ClassicCipherTool.

The tool is built purely on the standard library (re, string) and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic: each mode is checked against classical
published vectors (ROT13 of "Hello", the Caesar shift-3 classic, the
Atbash "wizard" example and the Vigenère ATTACKATDAWN/LEMON vector
from the standard references), exact round trips over mixed case,
punctuation and CJK, and a chi-squared crack whose winner is verified
against the known plaintext of a 60+ character English sample. The
error matrix covers malformed modes, operations, shifts, keys and
texts, plus the structured no-letters error payload of the crack mode.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import ClassicCipherTool
from agentuniverse.agent.action.tool.common_tool.classic_cipher_tool import (
    ClassicCipherTool as DirectClassicCipherTool,
)

# --------------------------------------------------------------------- #
# Known vectors (independent of the implementation — published classics)
# --------------------------------------------------------------------- #
ROT13_HELLO = "Uryyb"                     # rot13("Hello")
CAESAR3_HELLO_WORLD = "Khoor, Zruog!"     # caesar("Hello, World!", +3)
ATBASH_HELLO = "Svool"                    # atbash("Hello")
ATBASH_WIZARD = "draziw"                  # classic atbash example
VIGENERE_CLASSIC_PLAIN = "ATTACKATDAWN"   # classic Vigenère vector
VIGENERE_CLASSIC_KEY = "LEMON"
VIGENERE_CLASSIC_CIPHER = "LXFOPVEFRNHR"
VIGENERE_MIXED_PLAIN = "Attack at dawn!"
VIGENERE_MIXED_KEY = "Lemon"
VIGENERE_MIXED_CIPHER = "Lxfopv ef rnhr!"

CJK_TEXT = "你好, 世界! Say 終了."
NON_ALPHA_TEXT = "12345 !?-_@#$%"

# 81 characters of ordinary English without rare letters; used for the
# chi-squared crack assertions (>= 60 characters as recommended).
CRACK_PLAIN = (
    "the plan is simple we meet at the bridge at dawn and leave "
    "before the sun is high"
)
CRACK_CAESAR_SHIFT = 7


class ClassicCipherToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib ClassicCipherTool."""

    def setUp(self) -> None:
        self.tool = ClassicCipherTool()

    # ------------------------------------------------------------------ #
    # rot13 mode
    # ------------------------------------------------------------------ #

    def test_rot13_known_vector(self) -> None:
        result = self.tool.execute(mode="rot13", text="Hello")
        self.assertEqual(result, {"mode": "rot13", "result": ROT13_HELLO})

    def test_rot13_self_inverse(self) -> None:
        for text in ("Hello", CJK_TEXT, "The Quick Brown Fox!", "a" * 5000):
            once = self.tool.execute(mode="rot13", text=text)["result"]
            twice = self.tool.execute(mode="rot13", text=once)["result"]
            self.assertEqual(twice, text)

    def test_rot13_case_preserved(self) -> None:
        result = self.tool.execute(mode="rot13", text="AbZz")["result"]
        self.assertEqual(result, "NoMm")

    # ------------------------------------------------------------------ #
    # caesar mode
    # ------------------------------------------------------------------ #

    def test_caesar_encode_classic_vector(self) -> None:
        result = self.tool.execute(
            mode="caesar", operation="encode", text="Hello, World!", shift=3
        )
        self.assertEqual(
            result,
            {
                "mode": "caesar",
                "operation": "encode",
                "shift": 3,
                "result": CAESAR3_HELLO_WORLD,
            },
        )

    def test_caesar_decode_classic_vector(self) -> None:
        result = self.tool.execute(
            mode="caesar",
            operation="decode",
            text=CAESAR3_HELLO_WORLD,
            shift=3,
        )
        self.assertEqual(result["result"], "Hello, World!")

    def test_caesar_wraps_alphabet(self) -> None:
        result = self.tool.execute(
            mode="caesar", operation="encode", text="abcxyz ABCXYZ", shift=3
        )["result"]
        self.assertEqual(result, "defabc DEFABC")

    def test_caesar_round_trip_all_shifts(self) -> None:
        for shift in range(1, 26):
            with self.subTest(shift=shift):
                encoded = self.tool.execute(
                    mode="caesar", operation="encode", text=CJK_TEXT, shift=shift
                )["result"]
                decoded = self.tool.execute(
                    mode="caesar", operation="decode", text=encoded, shift=shift
                )["result"]
                self.assertEqual(decoded, CJK_TEXT)

    def test_caesar_string_shift_accepted(self) -> None:
        result = self.tool.execute(
            mode="caesar", operation="encode", text="abc", shift="3"
        )
        self.assertEqual(result["shift"], 3)
        self.assertEqual(result["result"], "def")

    # ------------------------------------------------------------------ #
    # atbash mode
    # ------------------------------------------------------------------ #

    def test_atbash_known_vectors(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="atbash", text="Hello")["result"],
            ATBASH_HELLO,
        )
        self.assertEqual(
            self.tool.execute(mode="atbash", text="wizard")["result"],
            ATBASH_WIZARD,
        )

    def test_atbash_mirrors_alphabet(self) -> None:
        result = self.tool.execute(mode="atbash", text="AZaz")["result"]
        self.assertEqual(result, "ZAza")

    def test_atbash_self_inverse(self) -> None:
        for text in ("Hello", CJK_TEXT, "Mxvlli sb wvvk!"):
            once = self.tool.execute(mode="atbash", text=text)["result"]
            twice = self.tool.execute(mode="atbash", text=once)["result"]
            self.assertEqual(twice, text)

    # ------------------------------------------------------------------ #
    # vigenere mode
    # ------------------------------------------------------------------ #

    def test_vigenere_classic_known_vector(self) -> None:
        result = self.tool.execute(
            mode="vigenere",
            operation="encode",
            text=VIGENERE_CLASSIC_PLAIN,
            key=VIGENERE_CLASSIC_KEY,
        )
        self.assertEqual(
            result,
            {
                "mode": "vigenere",
                "operation": "encode",
                "key": VIGENERE_CLASSIC_KEY,
                "result": VIGENERE_CLASSIC_CIPHER,
            },
        )

    def test_vigenere_decode_classic_vector(self) -> None:
        result = self.tool.execute(
            mode="vigenere",
            operation="decode",
            text=VIGENERE_CLASSIC_CIPHER,
            key=VIGENERE_CLASSIC_KEY,
        )["result"]
        self.assertEqual(result, VIGENERE_CLASSIC_PLAIN)

    def test_vigenere_mixed_case_and_punctuation(self) -> None:
        # Key is case-insensitive; case of each text letter is kept and
        # non-letters pass through without consuming key material.
        result = self.tool.execute(
            mode="vigenere",
            operation="encode",
            text=VIGENERE_MIXED_PLAIN,
            key=VIGENERE_MIXED_KEY,
        )["result"]
        self.assertEqual(result, VIGENERE_MIXED_CIPHER)
        decoded = self.tool.execute(
            mode="vigenere",
            operation="decode",
            text=result,
            key="LeMoN",
        )["result"]
        self.assertEqual(decoded, VIGENERE_MIXED_PLAIN)

    def test_vigenere_cjk_passthrough_round_trip(self) -> None:
        encoded = self.tool.execute(
            mode="vigenere", operation="encode", text=CJK_TEXT, key="key"
        )["result"]
        # Only ASCII letters move; CJK and punctuation are untouched.
        self.assertTrue(encoded.startswith("你好, 世界! "))
        decoded = self.tool.execute(
            mode="vigenere", operation="decode", text=encoded, key="KEY"
        )["result"]
        self.assertEqual(decoded, CJK_TEXT)

    def test_vigenere_round_trip_long_text(self) -> None:
        text = (CRACK_PLAIN + " ") * 3
        encoded = self.tool.execute(
            mode="vigenere", operation="encode", text=text, key="CipherKey"
        )["result"]
        decoded = self.tool.execute(
            mode="vigenere", operation="decode", text=encoded, key="cipherkey"
        )["result"]
        self.assertEqual(decoded, text)

    # ------------------------------------------------------------------ #
    # Non-alphabetic and CJK pass-through (all modes)
    # ------------------------------------------------------------------ #

    def test_non_alpha_text_unchanged_in_every_mode(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="rot13", text=NON_ALPHA_TEXT)["result"],
            NON_ALPHA_TEXT,
        )
        self.assertEqual(
            self.tool.execute(mode="atbash", text=NON_ALPHA_TEXT)["result"],
            NON_ALPHA_TEXT,
        )
        for operation in ("encode", "decode"):
            self.assertEqual(
                self.tool.execute(
                    mode="caesar",
                    operation=operation,
                    text=NON_ALPHA_TEXT,
                    shift=13,
                )["result"],
                NON_ALPHA_TEXT,
            )
            self.assertEqual(
                self.tool.execute(
                    mode="vigenere",
                    operation=operation,
                    text=NON_ALPHA_TEXT,
                    key="lemon",
                )["result"],
                NON_ALPHA_TEXT,
            )

    def test_cjk_and_accented_letters_pass_through(self) -> None:
        # Only the 26 ASCII letters are transformed: CJK stays as-is and
        # the accented Latin letter is not an ASCII letter either.
        text = " café 你好 Ærø "
        self.assertEqual(
            self.tool.execute(mode="rot13", text=text)["result"],
            " pnsé 你好 Æeø ",
        )
        self.assertEqual(
            self.tool.execute(mode="atbash", text="你好é")["result"],
            "你好é",
        )

    # ------------------------------------------------------------------ #
    # crack mode
    # ------------------------------------------------------------------ #

    def test_crack_recovers_caesar_shift_first(self) -> None:
        cipher = self.tool.execute(
            mode="caesar",
            operation="encode",
            text=CRACK_PLAIN,
            shift=CRACK_CAESAR_SHIFT,
        )["result"]
        result = self.tool.execute(mode="crack", text=cipher)
        candidates = result["candidates"]
        self.assertEqual(len(candidates), 3)
        self.assertEqual(result["mode"], "crack")
        self.assertEqual(candidates[0]["result"], CRACK_PLAIN)
        self.assertEqual(candidates[0]["shift"], CRACK_CAESAR_SHIFT)
        self.assertIsInstance(candidates[0]["score"], float)

    def test_crack_recovers_rot13_first(self) -> None:
        cipher = self.tool.execute(mode="rot13", text=CRACK_PLAIN)["result"]
        candidates = self.tool.execute(mode="crack", text=cipher)["candidates"]
        self.assertEqual(candidates[0]["result"], CRACK_PLAIN)
        self.assertEqual(candidates[0]["shift"], 13)

    def test_crack_candidates_ranked_by_score(self) -> None:
        cipher = self.tool.execute(
            mode="caesar", operation="encode", text=CRACK_PLAIN, shift=19
        )["result"]
        candidates = self.tool.execute(mode="crack", text=cipher)["candidates"]
        scores = [candidate["score"] for candidate in candidates]
        self.assertEqual(scores, sorted(scores))
        self.assertLess(scores[0], scores[1])
        shifts = [candidate["shift"] for candidate in candidates]
        self.assertEqual(len(set(shifts)), 3)

    def test_crack_plaintext_scores_best_of_all_26(self) -> None:
        cipher = self.tool.execute(
            mode="caesar", operation="encode", text=CRACK_PLAIN, shift=1
        )["result"]
        result = self.tool.execute(mode="crack", text=cipher)
        # The winning candidate must beat every other shift, including
        # shift 0 (the untouched ciphertext) which is never the answer
        # of a real encoding.
        winner = result["candidates"][0]
        self.assertEqual(winner["result"], CRACK_PLAIN)
        self.assertNotEqual(winner["shift"], 0)

    def test_crack_deterministic(self) -> None:
        cipher = self.tool.execute(
            mode="rot13", text=CRACK_PLAIN.upper()
        )["result"]
        first = self.tool.execute(mode="crack", text=cipher)
        second = self.tool.execute(mode="crack", text=cipher)
        self.assertEqual(first, second)

    def test_crack_without_letters_returns_error_payload(self) -> None:
        for text in (NON_ALPHA_TEXT, "你好，世界", "0123 456"):
            with self.subTest(text=text):
                result = self.tool.execute(mode="crack", text=text)
                self.assertEqual(result["mode"], "crack")
                self.assertEqual(
                    result["error"]["type"], "no_alphabetic_characters"
                )
                self.assertNotIn("candidates", result)

    def test_crack_keeps_case_and_non_letters_in_candidates(self) -> None:
        text = CRACK_PLAIN + ", 你好 World!"
        cipher = self.tool.execute(mode="rot13", text=text)["result"]
        candidates = self.tool.execute(mode="crack", text=cipher)["candidates"]
        winner = candidates[0]
        self.assertEqual(winner["shift"], 13)
        self.assertEqual(winner["result"], text)

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="enigma", text="hello")
        self.assert_invalid(mode=None, text="hello")
        self.assert_invalid(mode=123, text="hello")
        self.assert_invalid(mode="ROT13", text="hello")

    def test_invalid_operation(self) -> None:
        self.assert_invalid(
            mode="caesar", operation="encrypt", text="hello", shift=3
        )
        self.assert_invalid(mode="caesar", operation=None, text="hello", shift=3)
        self.assert_invalid(
            mode="caesar", operation="ENCODE", text="hello", shift=3
        )
        self.assert_invalid(
            mode="vigenere", operation="decode", text="hello", key=None
        )

    def test_invalid_shift(self) -> None:
        for bad in (0, 26, -3, 100, None, True, 3.5, "abc", "1-3", ""):
            with self.subTest(shift=bad):
                self.assert_invalid(
                    mode="caesar", operation="encode", text="hello", shift=bad
                )

    def test_shift_boundaries_accepted(self) -> None:
        for good in (1, 25):
            result = self.tool.execute(
                mode="caesar", operation="encode", text="a", shift=good
            )
            self.assertEqual(result["shift"], good)

    def test_invalid_key(self) -> None:
        for bad in (None, "", "ab1", "a b", "ab-c", "äbc", "你好", 123, True, ["k"]):
            with self.subTest(key=bad):
                self.assert_invalid(
                    mode="vigenere", operation="encode", text="hello", key=bad
                )

    def test_missing_key_for_vigenere(self) -> None:
        self.assert_invalid(mode="vigenere", operation="encode", text="hello")

    def test_missing_shift_for_caesar(self) -> None:
        self.assert_invalid(mode="caesar", operation="encode", text="hello")

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"hello", ["hello"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="rot13", text=bad)
                self.assert_invalid(
                    mode="caesar", operation="encode", text=bad, shift=3
                )
                self.assert_invalid(
                    mode="vigenere", operation="encode", text=bad, key="k"
                )
                self.assert_invalid(mode="crack", text=bad)

    def test_empty_text_rejected(self) -> None:
        for mode in ("rot13", "atbash", "crack"):
            self.assert_invalid(mode=mode, text="")
        self.assert_invalid(mode="caesar", operation="encode", text="", shift=3)
        self.assert_invalid(mode="vigenere", operation="encode", text="", key="k")

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        self.assert_invalid(mode="rot13", text=oversized)
        ok = self.tool.execute(mode="rot13", text="a" * 100_000)
        self.assertEqual(len(ok["result"]), 100_000)

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectClassicCipherTool, ClassicCipherTool)
        self.assertEqual(self.tool.name, "classic_cipher_tool")
        self.assertIn("ROT13", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("ClassicCipherTool", __all__)


if __name__ == "__main__":
    unittest.main()
