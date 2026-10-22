#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_wordplay_tool.py

"""Offline unit tests for WordplayTool.

The tool is built purely on the standard library (itertools,
collections) and never touches the network, so this suite runs fully
offline. Every assertion is deterministic: anagram verdicts are
checked against hand-sorted letter multisets, palindromes against the
classic English and CJK ground truths ("A man, a plan, a canal:
Panama" and 上海自来水来自海上), Scrabble scores against hand-computed
tile sums over the standard English value table, and the anagrams_of
mode against the exact anagram groups embedded in the tool's demo
word list (e.g. listen -> enlist / inlets / silent / tinsel). The
tool contains no randomness — anagram candidates come from
itertools.permutations — so identical inputs must always give
identical outputs, which the suite asserts directly.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import WordplayTool
from agentuniverse.agent.action.tool.common_tool.wordplay_tool import (
    WordplayTool as DirectWordplayTool,
)

# Hand-computed standard English Scrabble scores:
#   quick   = q(10) + u(1) + i(1) + c(3) + k(5)          = 20
#   kwyjibo = k(5) + w(4) + y(4) + j(8) + i(1) + b(3) + o(1) = 26
#   quiz    = q(10) + u(1) + i(1) + z(10)                = 22
#   dry     = d(2) + r(1) + y(4)                         = 7
#   quartz  = q(10) + u(1) + a(1) + r(1) + t(1) + z(10)  = 24
SCORE_QUICK = 20
SCORE_KWYJIBO = 26
SCORE_QUIZ = 22
SCORE_DRY = 7
SCORE_QUARTZ = 24

PANAMA = "A man, a plan, a canal: Panama"
PANAMA_CLEAN = "amanaplanacanalpanama"
CJK_PALINDROME = "上海自来水来自海上"


class WordplayToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib WordplayTool."""

    def setUp(self) -> None:
        self.tool = WordplayTool()

    # ------------------------------------------------------------------ #
    # check mode — is_anagram
    # ------------------------------------------------------------------ #

    def test_anagram_listen_silent(self) -> None:
        result = self.tool.execute(
            mode="check", text="listen", second_text="silent", check="is_anagram"
        )
        anagram = result["anagram"]
        self.assertTrue(anagram["is_anagram"])
        self.assertEqual(
            anagram["basis"], {"letters_only": True, "raw": True}
        )
        self.assertIn("both", anagram["verdict"])
        self.assertEqual(anagram["details"]["differing_letters"], {})
        self.assertEqual(
            anagram["details"]["letter_counts"]["text"],
            {"e": 1, "i": 1, "l": 1, "n": 1, "s": 1, "t": 1},
        )

    def test_anagram_letters_only_basis_verdict(self) -> None:
        # "Dormitory" vs "Dirty Room": same letters, different raw chars.
        result = self.tool.execute(
            mode="check", text="Dormitory", second_text="Dirty Room",
            check="is_anagram",
        )
        anagram = result["anagram"]
        self.assertTrue(anagram["is_anagram"])
        self.assertEqual(
            anagram["basis"], {"letters_only": True, "raw": False}
        )
        self.assertIn("letters-only basis", anagram["verdict"])
        self.assertEqual(anagram["details"]["differing_letters"], {})

    def test_anagram_case_insensitive(self) -> None:
        result = self.tool.execute(
            mode="check", text="LISTEN", second_text="Silent",
            check="is_anagram",
        )
        self.assertTrue(result["anagram"]["is_anagram"])

    def test_anagram_not_anagram_reports_differing_letters(self) -> None:
        result = self.tool.execute(
            mode="check", text="listen", second_text="silents",
            check="is_anagram",
        )
        anagram = result["anagram"]
        self.assertFalse(anagram["is_anagram"])
        self.assertEqual(
            anagram["details"]["differing_letters"], {"s": [1, 2]}
        )
        self.assertEqual(anagram["verdict"], "not anagrams")

    def test_anagram_different_lengths(self) -> None:
        result = self.tool.execute(
            mode="check", text="cat", second_text="cats", check="is_anagram"
        )
        anagram = result["anagram"]
        self.assertFalse(anagram["is_anagram"])
        self.assertEqual(
            anagram["details"]["differing_letters"], {"s": [0, 1]}
        )

    def test_anagram_cjk_multiset(self) -> None:
        # CJK characters are letters for the isalpha-based reduction.
        result = self.tool.execute(
            mode="check", text="上海", second_text="海上", check="is_anagram"
        )
        self.assertTrue(result["anagram"]["is_anagram"])

    def test_anagram_empty_after_strip_error_payload(self) -> None:
        result = self.tool.execute(
            mode="check", text="123", second_text="abc", check="is_anagram"
        )
        self.assertEqual(
            result["anagram"]["error"]["type"], "empty_after_strip"
        )

    # ------------------------------------------------------------------ #
    # check mode — is_palindrome
    # ------------------------------------------------------------------ #

    def test_palindrome_classic_english(self) -> None:
        result = self.tool.execute(
            mode="check", text=PANAMA, check="is_palindrome"
        )
        palindrome = result["palindrome"]
        self.assertTrue(palindrome["is_palindrome"])
        self.assertEqual(palindrome["details"]["cleaned_text"], PANAMA_CLEAN)
        self.assertEqual(palindrome["details"]["cleaned_length"], 21)
        self.assertIsNone(palindrome["details"]["first_mismatch"])

    def test_palindrome_classic_cjk(self) -> None:
        result = self.tool.execute(
            mode="check", text=CJK_PALINDROME, check="is_palindrome"
        )
        palindrome = result["palindrome"]
        self.assertTrue(palindrome["is_palindrome"])
        self.assertEqual(palindrome["details"]["cleaned_length"], 9)

    def test_palindrome_no_x_in_nixon(self) -> None:
        result = self.tool.execute(
            mode="check", text="No 'x' in Nixon", check="is_palindrome"
        )
        self.assertTrue(result["palindrome"]["is_palindrome"])

    def test_palindrome_was_it_a_car(self) -> None:
        result = self.tool.execute(
            mode="check", text="Was it a car or a cat I saw?",
            check="is_palindrome",
        )
        self.assertTrue(result["palindrome"]["is_palindrome"])

    def test_palindrome_not_one_shows_first_mismatch(self) -> None:
        result = self.tool.execute(
            mode="check", text="ab", check="is_palindrome"
        )
        palindrome = result["palindrome"]
        self.assertFalse(palindrome["is_palindrome"])
        self.assertEqual(
            palindrome["details"]["first_mismatch"],
            {"position": 0, "left": "a", "right": "b"},
        )

    def test_palindrome_strict_compares_raw_characters(self) -> None:
        loose = self.tool.execute(
            mode="check", text="Aa", check="is_palindrome"
        )
        strict = self.tool.execute(
            mode="check", text="Aa", check="is_palindrome", strict=True
        )
        self.assertTrue(loose["palindrome"]["is_palindrome"])
        self.assertFalse(strict["palindrome"]["is_palindrome"])
        self.assertEqual(
            strict["palindrome"]["details"]["first_mismatch"],
            {"position": 0, "left": "A", "right": "a"},
        )
        strict_punctuation = self.tool.execute(
            mode="check", text=PANAMA, check="is_palindrome", strict=True
        )
        self.assertFalse(strict_punctuation["palindrome"]["is_palindrome"])
        exact = self.tool.execute(
            mode="check", text="aa", check="is_palindrome", strict=True
        )
        self.assertTrue(exact["palindrome"]["is_palindrome"])

    def test_palindrome_empty_after_strip_error_payload(self) -> None:
        for punctuation_only in ("!!!", "123 456", "   "):
            with self.subTest(text=punctuation_only):
                result = self.tool.execute(
                    mode="check", text=punctuation_only, check="is_palindrome"
                )
                self.assertEqual(
                    result["palindrome"]["error"]["type"],
                    "empty_after_strip",
                )
                self.assertIn(
                    "at least one letter",
                    result["palindrome"]["error"]["message"],
                )

    # ------------------------------------------------------------------ #
    # check mode — both
    # ------------------------------------------------------------------ #

    def test_check_both_combines_results(self) -> None:
        # "anna" is a palindrome and an anagram of "naan" (aann).
        result = self.tool.execute(
            mode="check",
            text="anna",
            second_text="naan",
            check="both",
        )
        self.assertEqual(result["check"], "both")
        self.assertTrue(result["anagram"]["is_anagram"])
        self.assertTrue(result["palindrome"]["is_palindrome"])

    def test_check_both_mixed_error_and_verdict(self) -> None:
        # The palindrome side succeeds while the anagram side cannot.
        result = self.tool.execute(
            mode="check", text="aba", second_text="!!!", check="both"
        )
        self.assertEqual(
            result["anagram"]["error"]["type"], "empty_after_strip"
        )
        self.assertTrue(result["palindrome"]["is_palindrome"])

    # ------------------------------------------------------------------ #
    # anagrams_of mode
    # ------------------------------------------------------------------ #

    def test_anagrams_of_listen_full_group(self) -> None:
        result = self.tool.execute(mode="anagrams_of", text="listen")
        self.assertEqual(
            result,
            {
                "mode": "anagrams_of",
                "text": "listen",
                "word": "listen",
                "letters": 6,
                "anagrams": ["enlist", "inlets", "silent", "tinsel"],
                "count": 4,
                "total_found": 4,
                "truncated": False,
                "excluded_input": True,
                "word_list_size": 499,
                "note": (
                    "matched against the embedded common-English demo word "
                    "list (English only, not a dictionary)"
                ),
            },
        )

    def test_anagrams_of_small_groups(self) -> None:
        cases = [
            ("cat", ["act"]),
            ("earth", ["heart"]),
            ("dog", ["god"]),
            ("stone", ["notes", "onset", "tones"]),
            ("now", ["own", "won"]),
        ]
        for word, expected in cases:
            with self.subTest(word=word):
                result = self.tool.execute(mode="anagrams_of", text=word)
                self.assertEqual(result["anagrams"], expected)
                self.assertEqual(result["count"], len(expected))
                self.assertTrue(result["excluded_input"])

    def test_anagrams_of_excludes_input_word(self) -> None:
        result = self.tool.execute(mode="anagrams_of", text="silent")
        self.assertNotIn("silent", result["anagrams"])
        self.assertIn("listen", result["anagrams"])

    def test_anagrams_of_no_matches(self) -> None:
        # "quijibo"-style nonsense: real permutations, no list hits.
        result = self.tool.execute(mode="anagrams_of", text="quijibo")
        self.assertEqual(result["anagrams"], [])
        self.assertEqual(result["count"], 0)
        self.assertFalse(result["excluded_input"])
        self.assertEqual(result["letters"], 7)

    def test_anagrams_of_strips_punctuation_and_case(self) -> None:
        result = self.tool.execute(mode="anagrams_of", text="Listen!")
        self.assertEqual(result["word"], "listen")
        self.assertEqual(
            result["anagrams"], ["enlist", "inlets", "silent", "tinsel"]
        )

    def test_anagrams_of_deterministic(self) -> None:
        first = self.tool.execute(mode="anagrams_of", text="stone")
        second = self.tool.execute(mode="anagrams_of", text="stone")
        self.assertEqual(first, second)
        # Output is alphabetically sorted.
        self.assertEqual(first["anagrams"], sorted(first["anagrams"]))

    def test_anagrams_of_input_length_cap(self) -> None:
        ok = self.tool.execute(mode="anagrams_of", text="abcdefgh")
        self.assertEqual(ok["letters"], 8)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="anagrams_of", text="abcdefghi")

    # ------------------------------------------------------------------ #
    # palindrome_parts mode
    # ------------------------------------------------------------------ #

    def test_palindrome_parts_abcba(self) -> None:
        result = self.tool.execute(mode="palindrome_parts", text="abcba")
        self.assertEqual(result["longest"], "abcba")
        self.assertEqual(result["longest_length"], 5)
        self.assertEqual(result["palindromes"], ["abcba", "bcb"])
        self.assertFalse(result["truncated"])

    def test_palindrome_parts_bananas(self) -> None:
        result = self.tool.execute(mode="palindrome_parts", text="bananas")
        self.assertEqual(result["longest"], "anana")
        self.assertEqual(result["longest_length"], 5)
        self.assertEqual(result["palindromes"], ["anana", "ana", "nan"])

    def test_palindrome_parts_longest_geeks(self) -> None:
        result = self.tool.execute(
            mode="palindrome_parts", text="forgeeksskeegfor"
        )
        self.assertEqual(result["longest"], "geeksskeeg")
        self.assertEqual(result["longest_length"], 10)
        self.assertIn("geeksskeeg", result["palindromes"])

    def test_palindrome_parts_no_part_of_length_three(self) -> None:
        result = self.tool.execute(mode="palindrome_parts", text="abc")
        self.assertEqual(result["longest"], "a")
        self.assertEqual(result["longest_length"], 1)
        self.assertEqual(result["palindromes"], [])
        self.assertEqual(result["count"], 0)

    def test_palindrome_parts_cleans_before_scanning(self) -> None:
        result = self.tool.execute(mode="palindrome_parts", text=PANAMA)
        self.assertEqual(result["cleaned_text"], PANAMA_CLEAN)
        self.assertEqual(result["longest"], PANAMA_CLEAN)
        self.assertEqual(result["longest_length"], 21)

    def test_palindrome_parts_cjk(self) -> None:
        result = self.tool.execute(
            mode="palindrome_parts", text=CJK_PALINDROME
        )
        self.assertEqual(result["longest"], CJK_PALINDROME)
        self.assertEqual(result["longest_length"], 9)
        # Hand-checked palindromic CJK substrings of length >= 3.
        self.assertEqual(
            result["palindromes"],
            [CJK_PALINDROME, "海自来水来自海", "自来水来自", "来水来"],
        )

    def test_palindrome_parts_truncation(self) -> None:
        # (ab) repeated 60 times has exactly 2*(60-1) = 118 distinct
        # palindromic substrings of length >= 3 (two alternating variants
        # for every odd length 3..119, and no even-length palindromes at
        # all); the cap keeps the first 50.
        result = self.tool.execute(mode="palindrome_parts", text="ab" * 60)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["count"], 50)
        self.assertEqual(result["total_found"], 118)
        self.assertEqual(result["longest_length"], 119)
        self.assertTrue(result["longest"].startswith("a"))
        self.assertTrue(result["longest"].endswith("a"))
        lengths = [len(p) for p in result["palindromes"]]
        self.assertEqual(lengths, sorted(lengths, reverse=True))

    def test_palindrome_parts_empty_after_strip_error_payload(self) -> None:
        result = self.tool.execute(mode="palindrome_parts", text="!!!")
        self.assertEqual(result["error"]["type"], "empty_after_strip")

    # ------------------------------------------------------------------ #
    # letter_score mode
    # ------------------------------------------------------------------ #

    def test_letter_score_hand_computed_values(self) -> None:
        cases = [
            ("quick", SCORE_QUICK),
            ("kwyjibo", SCORE_KWYJIBO),
            ("quiz", SCORE_QUIZ),
            ("dry", SCORE_DRY),
            ("quartz", SCORE_QUARTZ),
            ("hello", 8),  # h(4) + e + l + l + o = 8
        ]
        for word, expected in cases:
            with self.subTest(word=word):
                result = self.tool.execute(mode="letter_score", text=word)
                self.assertEqual(result["score"], expected)
                self.assertEqual(result["word"], word)
                self.assertNotIn("unscored", result)

    def test_letter_score_breakdown_exact(self) -> None:
        result = self.tool.execute(mode="letter_score", text="quiz")
        self.assertEqual(
            result["breakdown"],
            [
                {"letter": "i", "count": 1, "value": 1, "points": 1},
                {"letter": "q", "count": 1, "value": 10, "points": 10},
                {"letter": "u", "count": 1, "value": 1, "points": 1},
                {"letter": "z", "count": 1, "value": 10, "points": 10},
            ],
        )

    def test_letter_score_casefold_and_unscored(self) -> None:
        result = self.tool.execute(mode="letter_score", text="Hello, World!")
        self.assertEqual(result["word"], "helloworld")
        self.assertEqual(result["score"], 17)
        self.assertEqual(
            result["unscored"],
            {"counts": {" ": 1, "!": 1, ",": 1}, "total": 3},
        )

    def test_letter_score_no_scoreable_letters_error_payload(self) -> None:
        for non_ascii in ("上海", "123", "!!!"):
            with self.subTest(text=non_ascii):
                result = self.tool.execute(
                    mode="letter_score", text=non_ascii
                )
                self.assertEqual(
                    result["error"]["type"], "no_scoreable_letters"
                )

    def test_letter_score_mixed_reports_unscored_but_scores(self) -> None:
        result = self.tool.execute(mode="letter_score", text="quartz石")
        self.assertEqual(result["score"], SCORE_QUARTZ)
        self.assertEqual(result["unscored"], {"counts": {"石": 1}, "total": 1})

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="anagram", text="listen")
        self.assert_invalid(mode=None, text="listen")
        self.assert_invalid(mode=123, text="listen")

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"listen", ["listen"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="letter_score", text=bad)
                self.assert_invalid(mode="anagrams_of", text=bad)

    def test_empty_text_rejected(self) -> None:
        for mode in ("check", "anagrams_of", "palindrome_parts",
                     "letter_score"):
            with self.subTest(mode=mode):
                self.assert_invalid(mode=mode, text="")

    def test_text_length_limit(self) -> None:
        oversized = "a" * 2_001
        for mode in ("check", "anagrams_of", "palindrome_parts",
                     "letter_score"):
            with self.subTest(mode=mode):
                self.assert_invalid(mode=mode, text=oversized)
        ok = self.tool.execute(mode="letter_score", text="a" * 2_000)
        self.assertEqual(ok["score"], 2_000)

    def test_invalid_check_value(self) -> None:
        self.assert_invalid(mode="check", text="listen", check="anagram")
        self.assert_invalid(mode="check", text="listen", check=None)
        self.assert_invalid(mode="check", text="listen", check="BOTH")

    def test_anagram_check_requires_second_text(self) -> None:
        self.assert_invalid(
            mode="check", text="listen", second_text=None, check="is_anagram"
        )
        self.assert_invalid(mode="check", text="listen", check="is_anagram")
        self.assert_invalid(
            mode="check", text="listen", check="both", second_text=None
        )

    def test_invalid_second_text(self) -> None:
        for bad in ("", 123, True, b"silent"):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="check",
                    text="listen",
                    second_text=bad,
                    check="is_anagram",
                )
        self.assert_invalid(
            mode="check",
            text="listen",
            second_text="b" * 2_001,
            check="is_anagram",
        )

    def test_invalid_strict(self) -> None:
        self.assert_invalid(mode="check", text="ab", check="is_palindrome",
                            strict="yes")
        self.assert_invalid(mode="check", text="ab", check="is_palindrome",
                            strict=1)
        # None and real booleans are accepted (None defaults to False).
        self.tool.execute(mode="check", text="ab", check="is_palindrome",
                          strict=None)
        self.tool.execute(mode="check", text="ab", check="is_palindrome",
                          strict=False)

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectWordplayTool, WordplayTool)
        self.assertEqual(self.tool.name, "wordplay_tool")
        self.assertIn("anagram", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("WordplayTool", __all__)

    def test_embedded_word_list_shape(self) -> None:
        from agentuniverse.agent.action.tool.common_tool.wordplay_tool import (
            _DEMO_WORDS,
        )

        # The documented demo-list contract: 300-500 common English
        # words, all lowercase ASCII, 3-6 letters.
        self.assertGreaterEqual(len(_DEMO_WORDS), 300)
        self.assertLessEqual(len(_DEMO_WORDS), 500)
        for word in _DEMO_WORDS:
            self.assertTrue(word.isascii(), word)
            self.assertTrue(word.isalpha(), word)
            self.assertTrue(3 <= len(word) <= 6, word)

    # ------------------------------------------------------------------ #
    # Adversarial regression tests
    # ------------------------------------------------------------------ #

    def test_max_text_chars_is_enforced(self) -> None:
        """The documented max_text_chars attribute is live
        configuration: overriding it on the instance tightens (or
        loosens) the input limit for text and second_text alike."""
        tool = WordplayTool()
        tool.max_text_chars = 10
        with self.assertRaises(ValueError) as ctx:
            tool.execute(mode="letter_score", text="a" * 11)
        self.assertIn("10-character limit", str(ctx.exception))
        self.assertEqual(tool.execute(mode="letter_score",
                                      text="a" * 10)["score"], 10)
        with self.assertRaises(ValueError):
            tool.execute(mode="check", text="abcdefghijk",
                         second_text="abcdefghij", check="is_anagram")
        # The default limit still applies to a fresh instance.
        self.assertEqual(
            self.tool.execute(mode="letter_score", text="a" * 2_000)["score"],
            2_000,
        )

    def test_palindrome_edge_matrix(self) -> None:
        """Single letters are trivially palindromes; combining marks
        strip with their base ambiguity, astral letters compare as
        single characters, emoji vanish, and German eszett casefolds
        to 'ss'."""
        result = self.tool.execute(mode="check", text="a",
                                   check="is_palindrome")
        self.assertTrue(result["palindrome"]["is_palindrome"])

        # NFD "é" (e + U+0301): the combining mark is not a letter, so
        # the cleaned text keeps only "e".
        nfd = "e\u0301"
        result = self.tool.execute(mode="check", text=nfd + "e",
                                   check="is_palindrome")
        self.assertEqual(result["palindrome"]["details"]["cleaned_text"],
                         "ee")

        # Astral-plane letters (Deseret) are single str characters and
        # compare naturally; astral emoji are not letters and vanish.
        result = self.tool.execute(
            mode="check", text="𐐀𐐨𐐀", check="is_palindrome"
        )
        self.assertTrue(result["palindrome"]["is_palindrome"])
        self.assertEqual(result["palindrome"]["details"]["cleaned_length"],
                         3)
        result = self.tool.execute(mode="check", text="a😀a",
                                   check="is_palindrome")
        self.assertEqual(result["palindrome"]["details"]["cleaned_text"],
                         "aa")

        # "aßa" -> "assa" under Unicode casefold.
        result = self.tool.execute(mode="check", text="aßa",
                                   check="is_palindrome")
        self.assertTrue(result["palindrome"]["is_palindrome"])
        self.assertEqual(result["palindrome"]["details"]["cleaned_text"],
                         "assa")

    def test_anagram_entirely_non_letter_inputs_error(self) -> None:
        """Strings with no letters at all on either side return the
        structured error payload, never a vacuous equal-multiset True."""
        for first, second in (("!!!", "..."), ("123", "456"),
                              ("123", "abc"), ("  ", "?!")):
            with self.subTest(first=first, second=second):
                result = self.tool.execute(
                    mode="check", text=first, second_text=second,
                    check="is_anagram",
                )
                self.assertEqual(
                    result["anagram"]["error"]["type"],
                    "empty_after_strip",
                )
                self.assertNotIn("is_anagram", result["anagram"])

    def test_anagrams_of_against_independent_permutations(self) -> None:
        """Every embedded-list anagram group is recomputed with an
        independent itertools.permutations implementation over the
        whole 499-word demo list and must match the tool exactly."""
        import itertools

        from agentuniverse.agent.action.tool.common_tool.wordplay_tool import (
            _DEMO_WORDS,
        )

        for word in sorted(_DEMO_WORDS):
            with self.subTest(word=word):
                result = self.tool.execute(mode="anagrams_of", text=word)
                independent = sorted(
                    candidate
                    for candidate in {
                        "".join(p) for p in itertools.permutations(word)
                    }
                    if candidate in _DEMO_WORDS and candidate != word
                )
                self.assertEqual(result["anagrams"], independent)

    def test_scrabble_table_matches_official_distribution(self) -> None:
        """All 26 English tile values against the official distribution:
        1 (aeioulnstr), 2 (dg), 3 (bcmp), 4 (fhvwy), 5 (k), 8 (jx),
        10 (qz)."""
        official = {
            "a": 1, "b": 3, "c": 3, "d": 2, "e": 1, "f": 4, "g": 2,
            "h": 4, "i": 1, "j": 8, "k": 5, "l": 1, "m": 3, "n": 1,
            "o": 1, "p": 3, "q": 10, "r": 1, "s": 1, "t": 1, "u": 1,
            "v": 4, "w": 4, "x": 8, "y": 4, "z": 10,
        }
        from agentuniverse.agent.action.tool.common_tool.wordplay_tool import (
            SCRABBLE_VALUES,
        )

        self.assertEqual(SCRABBLE_VALUES, official)
        self.assertEqual(len(SCRABBLE_VALUES), 26)
        result = self.tool.execute(mode="letter_score",
                                   text="abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(result["score"], sum(official.values()))

    def test_palindrome_parts_even_odd_centers_and_ties(self) -> None:
        """Even-length ('abba', 'aaaa') and odd-length ('aba') centers
        both expand correctly, and on a length tie the first occurrence
        wins while the distinct-substring set dedupes repeats."""
        result = self.tool.execute(mode="palindrome_parts", text="abba")
        self.assertEqual(result["longest"], "abba")
        self.assertEqual(result["palindromes"], ["abba"])

        result = self.tool.execute(mode="palindrome_parts", text="aaaa")
        self.assertEqual(result["longest"], "aaaa")
        self.assertEqual(result["palindromes"], ["aaaa", "aaa"])

        result = self.tool.execute(mode="palindrome_parts", text="aba")
        self.assertEqual(result["longest"], "aba")
        self.assertEqual(result["palindromes"], ["aba"])

        # Two disjoint 'abcba's around a non-palindromic separator:
        # equal longest length -> the first occurrence is reported, and
        # the substring list holds each distinct palindrome once.
        text = "abcbadefabcba"
        result = self.tool.execute(mode="palindrome_parts", text=text)
        self.assertEqual(result["longest"], "abcba")
        self.assertEqual(result["longest_length"], 5)
        self.assertEqual(text.index(result["longest"]), 0)
        self.assertEqual(result["palindromes"], ["abcba", "bcb"])


if __name__ == "__main__":
    unittest.main()
